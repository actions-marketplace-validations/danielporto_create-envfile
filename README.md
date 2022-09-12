# Create .Env File Github Action

[![GitHub
release](https://img.shields.io/github/release/SpicyPizza/create-envfile.svg?style=flat-square)](https://github.com/SpicyPizza/create-envfile/releases/latest)
[![GitHub
marketplace](https://img.shields.io/badge/marketplace-create--env--file-blue?logo=github&style=flat-square)](https://github.com/marketplace/actions/create-env-file)
[![Licence](https://img.shields.io/github/license/SpicyPizza/create-envfile)](https://github.com/SpicyPizza/create-envfile/blob/main/LICENSE)

## About

A Github Action to create an '.env' file with Github Secrets. This is useful
when you are creating artifacts that contain values stored in Github Secrets.
This creates a file with variables that are defined in the Action config.

## Usage

The Action looks for environment variables that start with `envkey_` and creates
an '.env' file with them. These are defined in the `with` section of the Action
config. Here is an example of it in use:

```yml
name: Create envfile

on: [ push ]

jobs:

  create-envfile:
 
    runs-on: ubuntu-latest
 
    steps:
    - name: Make envfile
      uses: SpicyPizza/create-envfile@v1.3
      with:
        envkey_DEBUG: false
        envkey_SOME_API_KEY: "123456abcdef"
        envkey_SECRET_KEY: ${{ secrets.SECRET_KEY }}
        envkey_10_A_NUMBERED_KEY: "lorem"
        envkey_3_ANOTHER_NUMBERED_KEY: "ipsum"
        envkey_5_NUMBERED_KEY_VALUE_WITH_SPACES: "lorem ipsum"
        envkey_1_ONE_MORE_NUMBERED_KEY: true
        jsonkey_VARKEY1: '[{"key": "VARKEY",	"value": "VARVALUE"}, {	"key": "VARKEY1",	"value": "VARVALUE1"}, {	"key": "VARKEY2",	"value": "VARVALUE2"}]'
        jsonkey_JVARKEYWITHALIAS: 'OVERRIDEKEY|[{"key": "JVARKEY",	"value": "VARVALUE"}, {"key": "OVERRIDEKEY",	"value": "VARVALUE"}, {	"key": "JVARKEY1",	"value": "VARVALUE1"}, {	"key": "JVARKEY2",	"value": "VARVALUE2"}, {	"key": "JVARKEYSPACE",	"value": "VAR KEY SPACE"}, {	"key": "JVARKEYVAR",	"value": "$VAR"}, {	"key": "JVARKEYLITERAL",	"value": "$VA%%%R"}]'
        some_other_variable: foobar
        directory: <directory_name>
        file_name: .env
        fail_on_empty: false
```

## Inputs

In the example above, there are several key/value pairs that will be added to
the '.env' file:

| Name                                  | Description                                                                                                                                                              |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `envkey_DEBUG`, `envkey_SOME_API_KEY` | These values can be whatever, and they will be added to the '.env' file as `DEBUG` and `SOME_API_KEY` .                                                                  |
| `envkey_SECRET_KEY`                   | This one will use a secret stored in the repository's Github Secrets, and add it to the file as  `SECRET_KEY`                                                            |
| `envkey_8_SOME_KEY`                   | This one defines a priority for the variables that appear in the resulting env file. Lower numbers appear first, prefixes are not included.                              |
| `envkey_SOME_HASH_`                   | This one allow values that have special characters such as '$' in bash variables. Useful to pass tokens and hashes. In practice, the value is enclosed in single quotes. |
| `jsonkey_VARKEY1`                     | This one allow values to be retrieved from a json string. Useful to overcome the Github secret limits. (All the above annotations apply)                                 |
| `directory` (**Optional**)            | This key will set the directory in which you want to create `env` file. **Important: cannot start with `/`. Action will fail if the specified directory doesn't exist.** |
| `file_name` (**Optional**)            | Set the name of the output '.env' file. Defaults to `.env`                                                                                                               |
| `fail_on_empty` (**Optional**)        | If set to true, the Action will fail if any env key is empty. Default to `false`.                                                                                        |

Note that the jsonkey has a json as value and the key name can be looked up from
it. That's useful when we need to compact several variables in a single secret
string, for instance, to overcome the Github limit of 100 secrets per
repository/workflow. Attention only that the size of the secret cannot be
greater than 64K.
More info: https://docs.github.com/en/actions/security-guides/encrypted-secrets#limits-for-secrets

Assuming that the Github Secret that was used is `password123`, the '.env' file
that is created from the config above would contain:

```text
ONE_MORE_NUMBERED_KEY=true
ANOTHER_NUMBERED_KEY="ipsum"
NUMBERED_KEY_VALUE_WITH_SPACES="lorem ipsum"
A_NUMBERED_KEY="lorem"
DEBUG=false
SOME_API_KEY="123456abcdef"
SECRET_KEY=password123
VARKEY1=VARVALUE1
JVARKEYWITHALIAS=VARVALUE
```

## Potential Issues

### Warnings

When the Action runs, it will show `Warning: Unexpected input(s) ...`. This is
because Github is expecing all the potential input variables to be defined by
the Action's definition. You can read more about it in [this
issue](https://github.com/SpicyPizza/create-envfile/issues/10).

![](https://user-images.githubusercontent.com/12802646/106284483-594e2300-6254-11eb-9e5d-3a6426da0435.png)
