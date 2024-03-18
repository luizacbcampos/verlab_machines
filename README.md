# Verlab Machines Interface

Python code to check GPU utilization of Verlab machines.

## How to use

On the Verlab Wiki there is a google sheet with all the machines available. Extract the `doc_key` and the `gid` from the url. Those informations are displayed on the URL like this:

```
https://docs.google.com/spreadsheets/d/{doc_key}/export?gid={gid}&format=csv
```

In order for the main code (verlab_machines.py) to run smoothly you will need to setup a jump host to the verlab machines. You should also set up a SSH Key Pair.


After setting everything up, run:

```
python verlab_machines.py
```
