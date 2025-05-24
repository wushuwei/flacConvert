import sys
import os

print("Initial sys.path:", sys.path)
print("PYTHONPATH env var:", os.environ.get('PYTHONPATH'))

import tkinter

def check_tkinter_availability():
    try:
        print("Attempting to import tkinter...")
        # Check if DISPLAY environment variable is set, which is crucial for Tkinter
        display_var = os.environ.get('DISPLAY')
        if not display_var:
            print("WARNING: DISPLAY environment variable is not set. Tkinter might fail to initialize a window.")
        
        root = tkinter.Tk()
        print("tkinter.Tk() instantiated successfully.")
        root.destroy()
        print("Tkinter root window created and destroyed successfully.")
        return True
    except ImportError as e:
        print(f"ImportError: Failed to import tkinter. Error: {e}")
        # Specifically check for _tkinter error
        if "_tkinter" in str(e).lower():
            print("This specific error often means the _tkinter.so shared library was not found or could not be loaded.")
            print("Relevant sys.path for _tkinter search:", sys.path)
        return False
    except tkinter.TclError as e:
        print(f"tkinter.TclError: Failed to initialize Tk. This often means no display is available. Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if check_tkinter_availability():
        print("RESULT: Tkinter appears to be available and working.")
    else:
        print("RESULT: Tkinter is NOT available or failed to initialize.")
