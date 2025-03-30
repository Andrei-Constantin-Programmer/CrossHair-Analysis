#!/usr/bin/env python

import argparse
import sys
from src.load_module import load_module_from_path
from src.run_analysis import run_crosshair_analysis_function, run_crosshair_analysis_class, run_crosshair_analysis_module

def parse_arguments():
    """Parse command-line arguments and return parsed options."""
    parser = argparse.ArgumentParser(description="Run CrossHair analysis on a function or class.")

    parser.add_argument(
        "file_path", 
        type=str, 
        help="Path to the Python file containing the function, class, or module to analyse.")
    
    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument(
        "-function", "-func",
        dest="function_name",
        type=str,
        help="Name of the function to analyse."
    )

    group.add_argument(
        "-class",
        dest="class_name",
        type=str,
        help="Name of the class to analyse."
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output.")
    
    parser.add_argument(
        "--console-dump", 
        action="store_true", 
        help="Print analysis results to console in addition to logging.")
    
    parser.add_argument(
        "--open-coverage",
        action="store_true",
        help="Open the generated coverage HTML report in the default browser."
    )
    
    args = parser.parse_args()
    return args.file_path, args.function_name, args.class_name, args.verbose, args.console_dump, args.open_coverage

def main():
    file_path, function_name, class_name, verbose, console_dump, open_coverage = parse_arguments()
    
    try:
        module = load_module_from_path(file_path)
    except (FileNotFoundError, ImportError) as e:
        print(f"Error loading module: {e}")
        sys.exit(1)
    
    if function_name:
        if not hasattr(module, function_name):
            print(f"Error: The module does not contain a function named '{function_name}'.")
            sys.exit(1)
        target_function = getattr(module, function_name)
        run_crosshair_analysis_function(target_function, file_path, verbose, console_dump, open_coverage)

    elif class_name:
        if not hasattr(module, class_name):
            print(f"Error: The module does not contain a class named '{class_name}'.")
            sys.exit(1)
        target_class = getattr(module, class_name)
        run_crosshair_analysis_class(target_class, file_path, verbose, console_dump, open_coverage)

    else:
        run_crosshair_analysis_module(module, file_path, verbose, console_dump, open_coverage)

if __name__ == "__main__":
    main()
