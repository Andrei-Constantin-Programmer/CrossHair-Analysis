#!/usr/bin/env python3
"""
Script to run CrossHair symbolic execution on a target solution.

This script imports a target function from the solution module (target_solution.py)
and uses CrossHair's API to perform symbolic execution and analyze the function's
contract specifications.

Adapted from the CPython codebase (https://github.com/python/cpython) and utilizing CrossHair.
"""

from src.log_analysis import log_analysis_results
from typing import Callable
from crosshair.core import analyze_function, analyze_class
from crosshair.options import AnalysisOptions
from crosshair.condition_parser import AnalysisKind
import logging
logging.basicConfig(level=logging.DEBUG)

def run_crosshair_analysis_class(target, verbose, console_dump):
    run_crosshair_analysis(analyze_class, target, verbose, console_dump)

def run_crosshair_analysis_function(target, verbose, console_dump):
    run_crosshair_analysis(analyze_function, target, verbose, console_dump)

def run_crosshair_analysis(analysis_function: Callable, target, verbose, console_dump):
    options = AnalysisOptions(
        analysis_kind=[AnalysisKind.asserts, AnalysisKind.icontract],
        enabled=True,
        specs_complete=True,
        per_condition_timeout=60.0,
        report_all=True,
        report_verbose=verbose,
        timeout=60.0,
        per_path_timeout=50.0,
        max_iterations=5000,
        max_uninteresting_iterations=5000,
    )

    analysis_results = analysis_function(target, options)
    log_analysis_results(target, analysis_results, console_dump)