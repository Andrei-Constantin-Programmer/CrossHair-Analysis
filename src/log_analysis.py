import os
import datetime

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
LOGS_PATH = os.path.join(ROOT_PATH, "logs")

def log_analysis_results(target, analysis_results):
    os.makedirs(LOGS_PATH, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_filename = f"log_{target.__name__}_{timestamp}.txt"
    log_path = os.path.join(LOGS_PATH, log_filename)

    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"CrossHair Analysis Results for {target.__name__}:\n")
        if not analysis_results:
            log_file.write("No results.\n")
        else:
            for result in analysis_results:
                log_file.write(str(result) + "\n")

    print(f"Analysis results logged to: {log_path}")
