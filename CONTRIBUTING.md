# Contributing to Streamlit component template

Welcome to Streamlit component template! We appreciate your interest in contributing to our project.

## Setting up pyenv and Intellij Idea

### 1. Install pyenv

Run command:
```shell
$ curl https://pyenv.run | bash
```

### 2. Use pyenv to install python

```shell
$ pyenv install <python_version>
```
- python_version - version of python, you can use
```shell
$ pyenv install --list
```
to check all available version, recommended 3.11.4

### 3. Creating virtual environment

```shell
$ pyenv virtualenv <python_version> <environment_name>
```

- python_version - version of python
- environment_name - your custom name of pyenv environment

### 4. Activate virtual environment

```shell
$ pyenv activate <environment_name>
```

- environment_name - your previously chosen pyenv environment name

### 5. Setup pyenv in Intellij IDEA

To configure your Python SDK in your project, follow these steps:

1. Open "File" menu.
2. Navigate to "Project Structure."
3. Under "Project," locate "Edit (SDK)."
4. Click on "Add Python SDK" (using the plus button).
5. Select "Virtualenv Environment."
6. Choose "Existing environment."
7. Specify the path to your Python environment using <your_pyenv_location>.

## Run locally example

### 1. Install and build frontend examples and templates

```shell
$ ./dev.py all-npm-install
$ ./dev.py all-npm-build
```

### 2. Install python packages

```shell
$ ./dev.py all-python-build-package
```

### 3. Set _RELEASE flag

For development we need to set _RELEASE flag. Open __init__.py file for any example or template and set _RELEASE flag to true. 
Remember to set this flag back to false if you want to create PR.

### 4. Install template as editable package

Go to directory of example or template and run `pip install -e .`.
Example:
```shell
$ cd examples/CustomDataframe
$ pip install -e .
```

### 5. Run python script and frontend

Example for CustomDataframe

Run python script
```shell
$ streamlit run examples/CustomDataframe/custom_dataframe/example.py
```

Run frontend:
```shell
$ cd examples/CustomDataframe/custom_dataframe/frontend
$ npm run start
```

# Testing

## Run locally

### 1. Run example locally

Please check "Run Locally example" section

### 2. Run pytest command

Example for CustomDataframe

```shell
$ pytest examples/CustomDataframe/e2e
```

## Run in docker

Run following commands:

```shell
$ ./dev.py e2e-build-images
$ ./dev.py e2e-run-tests
```