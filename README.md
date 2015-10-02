#golangenv

This tool is inspired by [nodeenv](https://github.com/ekalinin/nodeenv) and allows you to install golang into your virtualenvs.

Unlike nodeenv, golangenv **only** works inside virtualenvs.

## Install

```
$ virtualenv myenv
$ source myenv/bin/activate
$ pip install golangenv
$ golangenv install 1.5.1
```

## Example

```
$ mkdir frontend
$ echo 'use_env frontend' > frontenv/.env
$ cd frontend
$ pip install nodeenv golangenv
$ golangenv install 1.5.1
$ go version
```
