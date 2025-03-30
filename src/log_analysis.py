import os
import datetime
import re
from crosshair.main import long_describe_message
from src import ROOT_PATH

LOGS_PATH = os.path.join(ROOT_PATH, "logs")

def _remove_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def log_analysis_results(target, analysis_results, analysis_options, console_dump):
    os.makedirs(LOGS_PATH, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_filename = f"log_{target.__name__}_{timestamp}.txt"
    log_path = os.path.join(LOGS_PATH, log_filename)

    with open(log_path, "w", encoding="utf-8") as log_file:
        analysis_header = f"CrossHair Analysis Results for {target.__name__}:"
        log_file.write(f"{analysis_header}\n")
        if console_dump:
            print(analysis_header)

        if not analysis_results:
            no_results = "No results."
            log_file.write(f"{no_results}\n")
            if console_dump:
                print(no_results)
        else:
            for result in analysis_results:
                line = long_describe_message(result, analysis_options)
                if line is None:
                    continue
                log_file.write(f"{_remove_ansi(line)}\n")
                if console_dump:
                    print(line)

    print(f"Analysis results logged to: {log_path}")
