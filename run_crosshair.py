import sys
from src.load_module import load_module_from_path
from src.run_analysis import run_crosshair_analysis_function, run_crosshair_analysis_class

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_crosshair.py <path_to_module> [function_name]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    function_name = sys.argv[2] if len(sys.argv) > 2 else "bisect_right"
    
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
        run_crosshair_analysis_function(target_function)
    else:
        run_crosshair_analysis_class(module)

if __name__ == "__main__":
    main()
