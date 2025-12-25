import os
import subprocess
import sys
import platform

def get_executable_path(tool_name):
    """
    Finds the executable path for a tool (flet, pyinstaller) 
    relative to the current python interpreter (assumed to be in venv).
    """
    bin_dir = os.path.dirname(sys.executable)
    
    if platform.system() == "Windows":
        # Check for .exe first
        exe_path = os.path.join(bin_dir, f"{tool_name}.exe")
        if os.path.exists(exe_path):
            return exe_path
        # fallback to just name if not found in venv scripts (might rely on global path)
        return tool_name 
    else:
        path = os.path.join(bin_dir, tool_name)
        if os.path.exists(path):
            return path
        return tool_name

def build():
    print("Building executable...")
    
    # Resolve paths
    flet_exe = get_executable_path("flet")
    
    cmd = [flet_exe, "pack", "src/main.py", "--name", "musicdl"]
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("Build complete! Check the 'dist' directory.")
    except Exception as e:
        print(f"Error during 'flet pack': {e}")
        print("Trying fallback to raw PyInstaller...")
        
        pyinstaller_exe = get_executable_path("pyinstaller")
        cmd_fallback = [pyinstaller_exe, "src/main.py", "--name", "musicdl", "--onefile", "--noconsole"]
        print(f"Running fallback: {' '.join(cmd_fallback)}")
        
        try:
            subprocess.check_call(cmd_fallback)
            print("Build complete (via PyInstaller)! Check the 'dist' directory.")
        except Exception as e2:
             print(f"Fatal error during build: {e2}")

if __name__ == "__main__":
    print(f"Using Python: {sys.executable}")
    
    # Ensure packaging tools are installed
    # We use python -m pip to be safe
    print("Ensuring dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "flet"])
    
    build()
