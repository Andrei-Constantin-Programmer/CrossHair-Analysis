#!/usr/bin/env python

import argparse
import sys
from src.load_module import load_module_from_path
from src.run_analysis import run_crosshair_analysis_function, run_crosshair_analysis_class

def parse_arguments():
    """Parse command-line arguments and return parsed options."""
    parser = argparse.ArgumentParser(description="Run CrossHair analysis on a function or class.")

    parser.add_argument(
        "file_path", 
        type=str, 
        help="Path to the Python file containing the function or class to analyse.")
    
    parser.add_argument(
        "function_name", 
        type=str, 
        nargs="?", 
        default=None, 
        help="Name of the function to analyse (default: None (check class instead of specific function)).")
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output.")
    
    parser.add_argument(
        "--console-dump", 
        action="store_true", 
        help="Print analysis results to console in addition to logging.")
    
    args = parser.parse_args()
    return args.file_path, args.function_name, args.verbose, args.console_dump

def main():
    file_path, function_name, verbose, console_dump = parse_arguments()
    
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
        run_crosshair_analysis_function(target_function, verbose, console_dump)
    else:
        run_crosshair_analysis_class(module, verbose, console_dump)

if __name__ == "__main__":
    main()
