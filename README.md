# Assignment 2
Project originally designed as an assignment for my Validation and Verification assignment at UCL.  
Powered by [Crosshair](https://github.com/pschanely/CrossHair).

## Table of Contents
- [Installing](#installing)
- [Run Analysis](#run-analysis)
  - [Parameters](#analysis-parameters)
  - [Sample targets.json](#sample-targetsjson)
  - [Help](#analysis-help)
- [Logs and Coverage Output](#logs-and-coverage-output)

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
python run_crosshair.py <path_to_module> [-function -func <name> | -class <name>] [--verbose] [--console-dump] [--open-coverage]
```

For example:
```bash
python run_crosshair.py dataset/bisect/bisect.py -func bisect_right
```

Running a batch:
```bash
python run_crosshair.py --batch
```
This will read the targets.json file (example below) and run multiple analyses.

### **Analysis Parameters**
- `<path_to_module>` (**Required unless `--batch` is used**) – Path to the Python file containing the function, class, or module to analyse.
- `-function, -func <name>` (**Optional**) – Name of the function to analyse (default: `None`).
- `-class <name>` (**Optional**) - Name of the class to analyse (default: `None`).
- `--batch` (**Optional - incompatible with `path_to_module`, `-function`, and `-class`**) – Runs batch analysis on multiple targets defined in a `targets.json` file located in the root directory.
- `--verbose` (**Optional**) – Enables verbose output for detailed logging.
- `--console-dump` (**Optional**) – Prints analysis results to the console in addition to logging.
- `--open-coverage` (**Optional**) - Automatically opens the generated HTML coverage report in the default web browser after analysis.

If neither `-function`/`-func` nor `-class` is provided, then the entire module will be analysed.

### Sample targets.json
Below is an example **targets.json** file showing four different targets:

```json
[
  {
    "file": "dataset/bisect/bisect_program.py",
    "function": "bisect_right"
  },
  {
    "file": "dataset/egyptian_fraction/egyptian_fraction.py",
    "function": "egyptian_fraction"
  },
  {
    "file": "dataset/encoder/encoder.py",
    "class": "Encoder"
  },
  {
    "file": "dataset/request/request.py",
    "class": "Request"
  }
]
```

**Notes**:
- **file** (string, required): the path to the Python file you want CrossHair to analyze.
- **function** (string, optional): the name of the function to analyze. Use this if you want to check a specific function.
- **class** (string, optional): the name of the class to analyze. If you omit both `function` and `class`, CrossHair will treat the file as a module.

### Analysis Help
To display a help message with detailed usage instructions, run:

```bash
python run_crosshair.py --help
``` 

# Logs and Coverage Output
After each analysis run, two types of output are generated:

- **Logs**: Detailed CrossHair results are saved in the `logs/` directory with filenames like `log_<TargetName>_<timestamp>.txt`.
- **Coverage Reports**: An HTML coverage report is created in the `coverage/` directory. Each report is stored in a timestamped subdirectory like `coverage_<TargetName>_<timestamp>`.

To view the coverage report:
1. Navigate to the appropriate directory under `coverage/`
2. Open the `index.html` file in your browser:

If `--open-coverage` is used, the coverage report will open automatically after analysis.
If `--verbose` is used, the CrossHair log will be more detailed.
If `--console-dump` is used, the CrossHair log will be displayed in console in addition to the file.
