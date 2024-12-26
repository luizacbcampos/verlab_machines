import os
import re
import csv
import subprocess
import concurrent.futures
from datetime import datetime

LEN_LINE = 80
AMOUNT_DASHES = 78
HOST_LINE = "+"+"-"*AMOUNT_DASHES+"+"
LEFT_LINE = "| "
RIGTH_LINE = " |"

def text_in_color(text, color):
    if color.lower() == "red":
        return "\033[91m{}\033[00m" .format(text)
    elif color.lower() == "green":
        return "\033[92m{}\033[00m" .format(text)
    elif color.lower() == "yellow":
        return "\033[93m{}\033[00m" .format(text)
    elif color.lower() == "blue":
        return "\033[94m{}\033[00m" .format(text)
    elif color.lower() == "magenta":
        return "\033[95m{}\033[00m" .format(text)
    elif color.lower() == "cyan":
        return "\033[96m{}\033[00m" .format(text)
    
    else:
        return text

def get_hosts_list():
    default_host_list = ["proc1", "proc2", "proc3", "proc4", "proc5", "proc6", "proc7", "dalek", 
                 "epona", "escher", "eva", "ghost", "nymeria", "roomba", "marvin", "magritte", 
                 "kaya", "kiora", "shaggydog", "wall-e", ]
    # Run download_verlab_machines.py
    try:
        out, errors = subprocess.Popen("python download_verlab_machines.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(timeout=40)
    except subprocess.TimeoutExpired:
        print("Could not get new host list. Using default list.")
        return default_host_list

    # Read the csv file
    try:
        with open("verlab_machines.csv", "r") as file:
            data = list(csv.reader(file))
    except:
        return default_host_list

    host_list = []
    for i in range(1, len(data)):
        if data[i][-1] == "defeito": continue
        if data[i][-1] == "reservada": continue
        if data[i][-1] == "emprestada": continue
        host_list.append(data[i][0])
        host_obs.append(data[i][-1])
    return host_list


def re_match(line, pattern):
    match = re.search(pattern, line)
    return match

def run_cmd(host, cmd):
    try:
        out, errors = subprocess.Popen(f"ssh {host} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(timeout=40)
    except subprocess.TimeoutExpired:
        return "TimeoutExpired"
    out = out.decode('ascii')
    errors = errors.decode('ascii')
    if "nvidia-smi: command not found" in errors:
        return "NVIDIA-SMI has failed"
    return out

def check_host(host):
    cmd = f"ssh -o ConnectTimeout=7 {host} exit"
    out, errors = subprocess.Popen(f"{cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    errors = errors.decode("ascii")
    if errors.startswith("################################################"): # Warning message CRC is displaying on the terminal.
        if errors.endswith("password:"):
            return False
        return True
    if errors != "":
        return False
    return True

def print_host_table(info_list, colList=["Host"], sep='\uFFFA', first_time = True):
    '''
        Pretty print the host table with the information of the GPUs
        as a dynamically sized table.
        If first_time is True, it will print the header.
        If column names (colList) aren't specified, they will show in random order.
        sep: row separator. Ex: sep='\n' on Linux. Default: dummy to not split line.
    '''
    max_line_len = LEN_LINE - 2
    line_list = [colList] if first_time else [] # 1st row = header
    for i in range(0, len(info_list), len(colList)):
        this_line = []
        for j in range(len(colList)):
            this_line.append(info_list[i+j] if i+j < len(info_list) else "")
        line_list.append(this_line)
    print_table(line_list, max_line_len, sep, first_time)

def print_table(myList, max_line_len = LEN_LINE - 2, sep='\uFFFA', first_time = True):
    '''
        Pretty print a list of lists (myList) as a dynamically sized table.
        If first_time is False, it will print a separator line.
        sep: row separator. Ex: sep='\n' on Linux. Default: dummy to not split line.
    '''
    colSize = []
    amount_col = len(myList[0])
    for i, col in enumerate(zip(*myList)):
        this_col_max = max(max(map(len, (sep.join(col)).split(sep))), max_line_len)
        if this_col_max > max_line_len: this_col_max = max_line_len
        if i == 0 or i == amount_col-1: this_col_max = this_col_max - 1 # first and last columns
        else: this_col_max = this_col_max - 2 # middle columns
        colSize.append(this_col_max)

    formatStr = '| ' + ' | '.join(["{{:<{}}}".format(i) for i in (colSize)]) + ' |'
    line = formatStr.replace(' | ','-+-').replace(" ", "-").format(*['-' * i for i in colSize])
    item = myList.pop(0)
    lineDone = False

    if not first_time:
        print(line)
   
    while myList or any(item):
        if all(not i for i in item):
            item = myList.pop(0)
            if line and (sep!='\uFFFA' or not lineDone):
                print(line)
                lineDone = True
        row = [i.split(sep,1) for i in item]


        row_text = formatStr.format(*[i[0] for i in row])
        if "\033" in row_text:
            # Get the amount of spaces missing per color code
            without_color = re.sub(r'\033\[[0-9;]*m', '', row_text)
            amount_with_color = len(re.findall(r'\033\[[0-9;]*m', row_text))
            missing_spaces_per_color_code = (len(row_text) - len(without_color))//amount_with_color
            # Add missing spaces to the color codes
            row_text = row_text.replace("\033[", " "*missing_spaces_per_color_code+"\033[")
        print(row_text)
        item = [i[1] if len(i)>1 else '' for i in row]

class NV_csv(object):
    """
        docstring for NV_csv
    """
    
    def __init__(self, host, cmd, host_obs=""):
        self.host = host
        self.host_obs = host_obs
        self.cmd = cmd
        self.output = run_cmd(host, cmd)
        
    @staticmethod
    def clean_output(output):
        lines = output.split("\n")
        lines = [x for x in lines if x != '']
        return lines

    @staticmethod
    def extract_number(text):
        return re.findall(r'\d+', text)[0]
    
    def run(self):
        failure = self.output_failure(self.output)
        if failure[0]:
            return failure[1]
        
        self.lines = self.clean_output(self.output)

        self.info = self.read_output()
        self.no_gpus = len(list(self.info.keys()))
        self.convert_information()

        self.timestamp = self.get_timestamp()

        return self.display_info()

    def output_failure(self, output):
        ''''
            Check if output has failure
        '''
        if "NVIDIA-SMI has failed" in output:
            txt = "{} failure\n".format(self.host)
            return True, txt
        elif "Timeout expired" in output:
            txt = "{} timeout expired\n".format(self.host)
            return True, txt
        return False, ""

    def convert_information(self):
        '''
            Convert information to numbers
        '''

        for i in range(self.no_gpus):
            self.info[i]["timestamp"] = datetime.strptime(self.info[i]["timestamp"], '%Y/%m/%d %H:%M:%S.%f')
            self.info[i]["pcie.link.gen.max"] = int(self.info[i]["pcie.link.gen.max"])
            self.info[i]["pcie.link.gen.current"] = int(self.info[i]["pcie.link.gen.current"])
            self.info[i]["temperature.gpu"] = int(self.info[i]["temperature.gpu"])
            self.info[i]["utilization.gpu [%]"] = self.extract_number(self.info[i]["utilization.gpu [%]"])
            self.info[i]["utilization.memory [%]"] = self.extract_number(self.info[i]["utilization.memory [%]"])
            self.info[i]["memory.total [MiB]"] = self.extract_number(self.info[i]["memory.total [MiB]"])
            self.info[i]["memory.free [MiB]"] = self.extract_number(self.info[i]["memory.free [MiB]"])
            self.info[i]["memory.used [MiB]"] = self.extract_number(self.info[i]["memory.used [MiB]"])


    def read_output(self):
        d = {}
        for i in self.lines[0].split(","):
            d[i.strip()] = None
        keys = list(d.keys())

        info = {}
        for i in range(len(self.lines[1:])):
            info[i] = d.copy()
            line = self.lines[1+i]
            for j, value in enumerate(line.split(",")):
                info[i][keys[j]] = value.strip()
        
        return info

    def get_timestamp(self):
        try:
            timestamp = self.info[self.no_gpus-1]["timestamp"]
        except:
            timestamp = datetime.now()
        return timestamp

    def gpu_utilization(self, gpu_number):
        return self.info[gpu_number]['utilization.gpu [%]']
    
    def get_gpu_total(self, gpu_number):
        if type(self.info[gpu_number]['memory.total [MiB]'])==str:
            return int(self.info[gpu_number]['memory.total [MiB]'])
        return self.info[gpu_number]['memory.total [MiB]']

    def get_gpu_used(self, gpu_number):
        if type(self.info[gpu_number]['memory.used [MiB]'])==str:
            return int(self.info[gpu_number]['memory.used [MiB]'])
        return self.info[gpu_number]['memory.used [MiB]']
            
    def display_info(self):

        # txt = HOST_LINE\n"
        txt = ""
        if self.host_obs != "":
            txt += "{} at {}:".format(self.host, self.timestamp.strftime("%Y-%m-%d, %H:%M:%S"))
            txt += text_in_color(f" ({self.host_obs})", "cyan")
            txt += '\n'

        else:
            txt += "{} at {}:\n".format(self.host, self.timestamp.strftime("%Y-%m-%d, %H:%M:%S"))    

        for i in range(self.no_gpus):
            gpu_percent = int(self.get_gpu_used(i)/self.get_gpu_total(i)*100)
            if gpu_percent > 80:
                txt += text_in_color(f"{self.host} GPU [{i}]: {gpu_percent}%; {self.get_gpu_used(i)}/{self.get_gpu_total(i)}", "red") + '\n'
            elif gpu_percent > 30:
                txt += text_in_color(f"{self.host} GPU [{i}]: {gpu_percent}%; {self.get_gpu_used(i)}/{self.get_gpu_total(i)}", "yellow") + '\n'
            else:
                txt += text_in_color(f"{self.host} GPU [{i}]: {gpu_percent}%; {self.get_gpu_used(i)}/{self.get_gpu_total(i)}", "green") + '\n'
        return txt

def process_host(host, host_observation):
    if check_host(host):
        host_NV = NV_csv(host, csv_cmd, host_observation)
        return host_NV.run()
    return f"{host} not on"

if __name__ == '__main__':
    
    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines
    
    amount_of_columns = terminal_width//LEN_LINE

    host_obs, host_info = [], []
    host_list = get_hosts_list()
    cmd = "nvidia-smi"
    csv_cmd = "nvidia-smi --query-gpu=timestamp,name,pci.bus_id,driver_version,pstate,pcie.link.gen.max,pcie.link.gen.current,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv"

    amount_dashes = LEN_LINE*amount_of_columns - 2
    table_line = "+" + "-"*amount_dashes + "+"

    print(table_line) 
    first_time = True
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(process_host, host, host_observation) for host, host_observation in zip(host_list, host_obs)]
        for future in concurrent.futures.as_completed(results):
            host_info.append(future.result())

            if len(host_info) == amount_of_columns:
                print_host_table(host_info, colList=["Host"]*amount_of_columns, sep='\n', first_time=first_time)
                first_time = False
                host_info = []

    if len(host_info) != 0:
        print_host_table(host_info, colList=["Host"]*amount_of_columns, sep='\n', first_time=first_time)

    print(table_line)
