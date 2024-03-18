# Verlab Machines Interface

Python code to check GPU utilization of Verlab machines.

## How to use

On the Verlab Wiki there is a google sheet with all the machines available. Extract the `doc_key` and the `gid` from the url into the file `doc_info`. Those informations are displayed on the URL like this:

```
https://docs.google.com/spreadsheets/d/{doc_key}/export?gid={gid}&format=csv
```

Your `doc_info` file should look like this:
```
doc_key
gid
```

In order for the main code (verlab_machines.py) to run smoothly you will need to setup a jump host to the verlab machines. You should also set up a SSH Key Pair.


After setting everything up, run:

```
python verlab_machines.py
```

## Example
```
+------------------------------------------------------------------------------+
| Host                                                                          |
|-------------------------------------------------------------------------------|
| proc1 not on                                                                  |
|-------------------------------------------------------------------------------|
| proc6 at 2024-03-18, 14:17:32:      (prioridade)                              |
|      proc6 GPU [0]: 57%; 14246/24564                                          |
|      proc6 GPU [1]: 95%; 23572/24564                                          |
|-------------------------------------------------------------------------------|
| epona at 2024-03-18, 14:17:37:      (chunk)                                   |
|      epona GPU [0]: 0%; 14/6081                                               |
+------------------------------------------------------------------------------+

```
