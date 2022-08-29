#!/usr/local/bin/python
import os
import re
import sys

env_keys = list(dict(os.environ).keys())

out_file = ""

ordered_pattern = "INPUT_ENVKEY_\d+_"
# Make sure the env keys are sorted to have deterministic output
priority_envs = [ e for e in env_keys if re.match(ordered_pattern, e) ]
# a custom sort function ensure the order of the elements that were numbered
priority_envs = sorted(priority_envs, key=lambda x: int(x.split('_')[2]))

other_envs = [ e for e in env_keys if e not in priority_envs ]
other_envs = sorted(other_envs)

all_envs = list()
all_envs.extend(priority_envs)
all_envs.extend(other_envs)


for key in all_envs:
    if key.startswith("INPUT_ENVKEY_"):
        value = os.getenv(key, "")

        # If the key is empty, throw an error.
        if value == "" and os.getenv("INPUT_FAIL_ON_EMPTY", "false") == "true":
            raise Exception(f"Empty env key found: {key}")

        # remove order id if exists:
        if re.match(ordered_pattern, key):
            key = re.split(ordered_pattern,key)[1]
        else:
            key = key.split("INPUT_ENVKEY_")[1]

        # if the value has spaces, use quotes
        if key.endswith("_") in value: # enforce literal
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

# This should resolve https://github.com/SpicyPizza/create-envfile/issues/27
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
