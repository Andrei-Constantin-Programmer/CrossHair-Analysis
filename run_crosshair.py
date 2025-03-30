#!/usr/bin/env python

import argparse
import json
import os
import sys
from src.load_module import load_module_from_path
from src.run_analysis import run_crosshair_analysis_function, run_crosshair_analysis_class, run_crosshair_analysis_module

def parse_arguments():
    """Parse command-line arguments and return parsed options."""
    parser = argparse.ArgumentParser(description="Run CrossHair analysis on a function or class.")
    
    parser.add_argument(
        "file_path", 
        nargs="?",
        type=str, 
        help="Path to the Python file containing the function, class, or module to analyse.")
    
    parser.add_argument(
        "--batch", 
        action="store_true",
        help="Run batch analysis from 'targets.JSON'"
    )

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

    if args.batch:
        if args.file_path or args.function_name or args.class_name:
            parser.error("When using --batch, do not provide file_path or function/class.")
    elif not args.file_path:
        parser.error("Must provide file_path unless using --batch.")

    return args.file_path, args.batch, args.function_name, args.class_name, args.verbose, args.console_dump, args.open_coverage

def main():
    file_path, batch, function_name, class_name, verbose, console_dump, open_coverage = parse_arguments()
    
    if batch:
        try:
            run_batch_analysis(verbose, console_dump, open_coverage)
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading batch file: {e}")
            sys.exit(1)
    else:
        try:
            run_analysis_target(file_path, function_name, class_name, verbose, console_dump, open_coverage)
        except (FileNotFoundError, ImportError, AttributeError) as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    
def run_batch_analysis(verbose, console_dump, open_coverage):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch_path = os.path.join(script_dir, "targets.json")

    with open(batch_path, "r") as f:
        targets = json.load(f)

    if not isinstance(targets, list):
        raise TypeError("Batch file must contain a list of target objects.")

    for i, target in enumerate(targets, start=1):
        try:
            file_path = target["file"]
            function_name = target.get("function")
            class_name = target.get("class")

            print(f"\n[{i}/{len(targets)}] Running analysis for: {file_path} "
                  f"(function: {function_name}, class: {class_name})")

            run_analysis_target(file_path, function_name, class_name, verbose, console_dump, open_coverage)

        except KeyError as e:
            print(f"Target #{i} is missing a required key: {e}")
        except Exception as e:
            print(f"Analysis failed for Target #{i}: {e}")


def run_analysis_target(file_path, function_name, class_name, verbose, console_dump, open_coverage):
    module = load_module_from_path(file_path)

    if function_name:
        if not hasattr(module, function_name):
            raise AttributeError(f"The module does not contain a function named '{function_name}'.")
        target_function = getattr(module, function_name)
        run_crosshair_analysis_function(target_function, file_path, verbose, console_dump, open_coverage)

    elif class_name:
        if not hasattr(module, class_name):
            raise AttributeError(f"The module does not contain a class named '{class_name}'.")
        target_class = getattr(module, class_name)
        run_crosshair_analysis_class(target_class, file_path, verbose, console_dump, open_coverage)

    else:
        run_crosshair_analysis_module(module, file_path, verbose, console_dump, open_coverage)


if __name__ == "__main__":
    main()
