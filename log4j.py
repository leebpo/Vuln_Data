# make sure csv of `Past Status` & csv of `Current Status` 
# are in same directory as this program
# and are named `past_status.csv` & `current_status.csv`

import pandas as pd
import numpy as np
import copy

# making pandas dataframe of `Current Status` logs
logs = pd.read_csv('./current_status.csv')
logs_rows = logs.index
logs_num_rows = len(logs_rows)

# making pandas dataframe of `Past Status` logs indexed by IPs
past_logs = pd.read_csv('./past_status.csv')
past_by_IP = past_logs.set_index('IP Address')
past_IPs = list(past_by_IP.index)


# helper functions for reformatting Plugin Outputs

# takes original 'Plugin Output' as string
# groups lines into arrays of ['Path : ...', 'Installed...', 'Fixed...']
# returns array of those arrays  
def group_paths(po):
    po = po.split("\n")[1:]
    answer = []
    current_group = []
    for p in po:
        if (p != ''):
            current_group.append(p)
        if p[2:3] == "F":
            answer.append(copy.copy(current_group))
            current_group.clear()
    return answer

# takes original 'Plugin Output' as string
# returns dictionary of (string, string): string
# where keys are pairs lines for installed & fixed versions
# and values are the arrays of paths with those versions
def combined_groups(po):
    grouped_po = group_paths(po)
    answer = {}
    for group in grouped_po:
        path = group[0]
        inst_v = group[1]
        fixed_v = group[2]
        versions = (inst_v, fixed_v)
        if versions in answer.keys():
            answer[versions].append(path)
        else:
            answer[versions] = [path]
    return answer

# takes original 'Plugin Output' as string
# returns new shortened format of 'Plugin Output' string
def reformatted_po(po):
    answer = "Plugin Output:\n"
    groups = combined_groups(po)
    for key in groups.keys():
        (inst_v, fixed_v) = key
        for path in groups[key]:
            answer = f'{answer}{path}\n'
        answer = f'{answer}{inst_v}\n{fixed_v}\n\n'
    return answer


# making new csv files

# filling in columns of `Current Status` logs
# and reformatting its Plugin Output column
unknown_ips = []

# arrays to store new columns
apps = [""]*logs_num_rows
contacts = [""]*logs_num_rows
new_pos = [""]*logs_num_rows
vulnerable = [""]*logs_num_rows
response = [""]*logs_num_rows

for i in logs_rows:
    ip = logs.loc[i, 'IP Address']
    po = logs.loc[i, 'Plugin Output']
    
    # filling in Application, Contact, Vulnerable?, and RESPONSE columns
    if ip in past_IPs: 
        apps[i] = past_by_IP.loc[ip]['Application']
        contacts[i] = past_by_IP.loc[ip]['Contact']
        vulnerable[i] = past_by_IP.loc[ip]['Vulnerable?']
        response[i] = past_by_IP.loc[ip]['RESPONSE']
    else:
        unknown_ips.append(ip)
        
    # reformatting Plugin Output column
    new_po = reformatted_po(po)
    new_pos[i] = new_po
    
print("Unknown IPs")
print(unknown_ips)

# making csv file with new Application, Contact, & Plugin Output columns
logs.drop('Plugin Output', 1, inplace=True)
logs.insert(2, 'Application', apps)
logs.insert(3, 'Contact', contacts)
logs.insert(4, 'Plugin Output', new_pos)
logs.to_csv('./new_current_status.csv')

# making csv file with added Vulnerable? & RESPONSE columns
logs.insert(5, 'Vulnerable?', vulnerable)
logs.insert(6, 'RESPONSE', response)
logs.to_csv('./new_current_status_extra.csv')
