import importlib
import os
import sys


def load_module_from_path(file_path):
    """
    Load a Python module from the given file path.

    Parameters:
        file_path (str): The path to the Python file to load.
        
    Returns:
        module: The loaded module object.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
