import datetime
import os
import webbrowser
from coverage import Coverage
from src import ROOT_PATH

COVERAGE_PATH = os.path.join(ROOT_PATH, "coverage")

def report_coverage(cov: Coverage, target, open_coverage: bool):
    path = os.path.join(COVERAGE_PATH, f"coverage_{target.__name__}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}")
    cov.html_report(directory=path, title="CrossHair Coverage")
    print(f"Coverage results printed to: {path}. Open the index.html file in a browser to see the results.")

    if open_coverage:
        webbrowser.open(f"file://{os.path.join(path, "index.html")}")
        
    cov.erase()