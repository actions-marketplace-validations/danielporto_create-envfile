#!/usr/local/bin/python
import os
import re
import sys
import json
from pprint import pprint as pp


def find_value(key, list_of_maps):
    for pair in list_of_maps:
        if key == pair['key']:
            return pair['value']
    return ""

env_keys = list(dict(os.environ).keys())

out_file = ""

# ordered_pattern = "INPUT_ENVKEY_4_VAR"
# ordered_json_pattern = "INPUT_JSONKEY_1_VAR"
prioritized_vars_pattern = "INPUT_\w+_\d+_"

# extract prioritized keys
priority_envs = [ e for e in env_keys if re.match(prioritized_vars_pattern, e) ]

# sort keys using priority then alphabetical, ignoring the prefix
if priority_envs:
    priority_map = dict()
    for entry in priority_envs:
        priority = int(entry.split('_')[2])
        if priority in priority_map:
            priority_map[priority].append(entry)
        else:
            priority_map[priority] = [entry]

    priority_keys_sorted = sorted(priority_map.keys())
    
    priority_envs_sorted = list()
    # sort items with the same priority alphabetically
    for priority in priority_keys_sorted:
        priority_envs_sorted += sorted(priority_map[priority], key=lambda x: '_'.join(x.split('_')[3:]))
    priority_envs = priority_envs_sorted

# pp(priority_envs)
# retrieve the other non prioritized envs
other_envs = [ e for e in env_keys if (re.match("INPUT_ENVKEY", e) or re.match("INPUT_JSONKEY", e)) and e not in priority_envs ]
# sort the other non prioritized elements alphabetically
other_envs = sorted(other_envs, key=lambda x: '_'.join(x.split('_')[2:]))
# pp(other_envs)

all_envs = list()
all_envs.extend(priority_envs)
all_envs.extend(other_envs)

# pp(all_envs)

for key in all_envs:
    if key.startswith("INPUT_ENVKEY_"):
        value = os.getenv(key, "")

        # If the key is empty, throw an error.
        if value == "" and os.getenv("INPUT_FAIL_ON_EMPTY", "false") == "true":
            raise Exception(f"Empty env key found: {key}")

        # remove order id if exists:
        if re.match(prioritized_vars_pattern, key):
            key = re.split(prioritized_vars_pattern, key)[1]
        else:
            key = key.split("INPUT_ENVKEY_")[1]

        # if the value has spaces, use quotes
        if key.endswith("_"): # enforce literal
            out_file += "{}='{}'\n".format(key[:-1], value)
        elif " " in value or "$" in value: # for spaces and variables, use double quotes
            out_file += "{}=\"{}\"\n".format(key, value)
        else: # all the rest do not include quotes
            out_file += "{}={}\n".format(key, value)

    elif key.startswith("INPUT_JSONKEY_"):
        jsonstr = os.getenv(key, "")

        # If the key is empty, throw an error.
        if jsonstr == "" and os.getenv("INPUT_FAIL_ON_EMPTY", "false") == "true":
            raise Exception(f"Empty env key found: {key}")

        # remove order id if exists:
        if re.match(prioritized_vars_pattern, key):
            key = re.split(prioritized_vars_pattern,key)[1]
        else:
            key = key.split("INPUT_JSONKEY_")[1]

        # unpack envs (we assume the json is well formatted or prefixed with the filter):
        filter_pattern = "\w+\|"
        if re.match(filter_pattern, jsonstr):
            # print("NEWKEY:",key)
            jsonkey=jsonstr[:jsonstr.find("|")]
            # print("JSONKEY:",jsonkey)
            jsonstr=jsonstr[jsonstr.find("|")+1:]    
            env_pairs = json.loads(jsonstr)
            for item in env_pairs:
                if item['key'] == jsonkey:
                    item['key'] = key
                    break
        else:
            env_pairs = json.loads(jsonstr)

        # lookup the value ignoring literal suffix
        if key.endswith("_"):
            value = find_value(key[:-1], env_pairs)
        else: 
            value = find_value(key, env_pairs)

        # If the key is empty, throw an error.
        if value == "" and os.getenv("INPUT_FAIL_ON_EMPTY", "false") == "true":
            raise Exception(f"Empty json key found: {key}")

        # if the value has spaces, use quotes
        if key.endswith("_"): # enforce literal
            print(key)
            print("{}='{}'\n".format(key[:-1], value))
            out_file += "{}='{}'\n".format(key[:-1], value)
        elif " " in value or "$" in value: # for spaces and variables, use double quotes
            out_file += "{}=\"{}\"\n".format(key, value)
        else: # all the rest do not include quotes
            out_file += "{}={}\n".format(key, value)

# get directory name in which we want to create .env file
directory = str(os.getenv("INPUT_DIRECTORY", ""))

# get file name in which we want to add variables
# .env is set by default
file_name = str(os.getenv("INPUT_FILE_NAME", ".env"))

path = str(os.getenv("GITHUB_WORKSPACE", "/github/workspace"))

# ensure path exists
if path in ["", "None"]:
    path = "."

if directory == "":
    full_path = os.path.join(path, file_name)
elif directory.startswith("/"):
    # Throw an error saying that absolute paths are not allowed. This is because
    # we're in a Docker container, and an absolute path would lead us out of the
    # mounted directory.
    raise Exception("Absolute paths are not allowed. Please use a relative path.")
elif directory.startswith("./"):
    full_path = os.path.join(path, directory[2:], file_name)
# Any other case should just be a relative path
else:
    full_path = os.path.join(path, directory, file_name)

print("Creating file: {}".format(full_path))

with open(full_path, "w") as text_file:
    text_file.write(out_file)
