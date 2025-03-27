# Assignment 2

## Table of Contents
- [Installing](#installing)
- [Run Analysis](#run-analysis)
  - [Parameters](#analysis-parameters)
  - [Help](#analysis-help)

## Installing

1. Ensure **Python 3.13.x** or higher is installed.

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
python run_crosshair.py <path_to_module> [function_name] [--verbose] [--console-dump]
```

For example:
```bash
python run_crosshair.py dataset/bisect.py bisect_right
```

### **Analysis Parameters**
- `<path_to_module>` (**Required**) – Path to the Python file containing the function or class to analyse.
- `[function_name]` (**Optional**) – Name of the function to analyse (default: `None`, meaning the class will be analysed instead).
- `--verbose` (**Optional**) – Enables verbose output for detailed logging.
- `--console-dump` (**Optional**) – Prints analysis results to the console in addition to logging.

### Analysis Help
To display a help message with detailed usage instructions, run:

```bash
python run_crosshair.py --help
``` 