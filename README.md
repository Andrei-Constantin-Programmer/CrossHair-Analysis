# Assignment 2

## Table of Contents
- [Installing](#installing)
- [Run Analysis](#run-analysis)
  - [Parameters](#analysis-parameters)
  - [Help](#analysis-help)
- [Run Tests](#run-tests)

## Installing

1. Ensure **Python 3.8.x** or higher is installed

2. Clone project
Clone the repository locally, or download and extract the ZIP file.

3. Install prerequisite packages
Run the following command from the project root:
```bash
pip install -r requirements.txt
```

## Run Analysis
To run Crosshair, use the command-line interface:
```bash
python run_crosshair.py <path_to_module> [function_name]
```

For example:
```bash
python run_crosshair.py dataset/bisect.py bisect_right
```