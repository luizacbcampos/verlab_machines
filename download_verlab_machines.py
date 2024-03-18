'''
This program is used to download the names and info from verlab machines from the verlab website.
The csv is processed and 
'''

import os
import re
import csv
import subprocess

def process_csv():
    '''
    This function processes the csv file and extracts the necessary information.
    '''
    with open("temp.csv", "r") as file:
        reader = csv.reader(file)
        data = list(reader)
    
    new_data = [data[0]+["obs_simple"]]
    
    for i in range(1, len(data)):
        if data[i][0] == "": continue
        if re.match(r"servidor", data[i][0].lower()) or re.match(r"desktop", data[i][0].lower()):
            continue
        if re.search(r"\(defeito\)", data[i][0].lower()):
            data[i][0] = re.sub(r"\(defeito\)", "", data[i][0].lower()).strip()
            data[i][1] = ("(defeito) " + data[i][1]).strip()
        
        for j in range(len(data[i])):
            data[i][j] = re.sub(r"\n", " ", data[i][j])

        # Simplify the observation
        obs_simple = ""
        if re.search(r"(defeito)", data[i][1].lower()):
            obs_simple = "defeito"
        elif re.search(r"(reserv)", data[i][1].lower()):
            obs_simple = "reservada"
        elif re.search(r"(emprest)", data[i][1].lower()):
            obs_simple = "emprestada"
        elif re.search(r"(chunk)", data[i][1].lower()):
            obs_simple = "chunk"
        elif re.search(r"(priorid)", data[i][1].lower()):
            obs_simple = "prioridade"

        for j in range(len(data[i])):
            data[i][j] = data[i][j].strip()
    
        new_data.append(data[i]+[obs_simple])

    # Write the new data to a new csv file
    with open("verlab_machines.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows(new_data)

    # Remove the temp file
    os.remove("temp.csv")


def download_new_version(docs_link):
    '''
    This function downloads the new version of the verlab machines csv file.
    '''
    download_command = f"wget --no-check-certificate -O temp.csv '{docs_link}'"
    out, errors = subprocess.Popen(download_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(timeout=40)

    # Check if the file was downloaded
    if os.path.exists("temp.csv"):
        process_csv()
    else:
        print("File not downloaded")
        exit(1)

if __name__ == '__main__':
    with open("doc_info", "r") as file:
        doc_key, gid = file.read().strip().split("\n")
    docs_link = f"https://docs.google.com/spreadsheets/d/{doc_key}/export?gid={gid}&format=csv"

    download_new_version(docs_link)