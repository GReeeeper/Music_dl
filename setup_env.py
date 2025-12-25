import os
import sys
import subprocess
import shutil
import platform

def check_command(command):
    return shutil.which(command) is not None

def install_system_dependencies():
    system = platform.system()
    print(f"Detected OS: {system}")
    
    if not check_command("ffmpeg"):
        print("WARNING: 'ffmpeg' not found in PATH.")
        if system == "Linux":
            print("Please run: sudo apt install ffmpeg (or equivalent for your distro)")
        elif system == "Darwin":
            print("Please run: brew install ffmpeg")
        elif system == "Windows":
            print("Please download FFmpeg from https://ffmpeg.org/download.html and add it to your PATH.")
        
        # We don't exit here, as the user might want to proceed for now, 
        # but functionality will be limited.
    else:
        print("FFmpeg is available.")

    # Check for libmpv (required by Flet on Linux)
    if system == "Linux":
        # quick check if we can find libmpv.so.1 or mpv executable as a proxy
        # usually 'mpv' package contains the lib.
        if not check_command("mpv"):
             print("WARNING: 'mpv' (providing libmpv.so.1) might be missing.")
             print("Flet requires libmpv.so.1 to run on Linux.")
             print("Please run: sudo pacman -S mpv (Arch) or sudo apt install libmpv-dev mpv (Ubuntu/Debian)")

def create_virtual_env():
    venv_dir = os.path.join(os.getcwd(), "venv")
    
    # Check if venv exists AND has the python interpreter
    python_bin = os.path.join(venv_dir, "bin", "python")
    if platform.system() == "Windows":
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")

    if os.path.exists(venv_dir):
        if os.path.exists(python_bin):
            print("Virtual environment already exists.")
            return venv_dir
        else:
            print("Virtual environment folder exists but appears corrupted (missing python). Recreating...")
            shutil.rmtree(venv_dir)

    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    print("Virtual environment created at", venv_dir)
    return venv_dir

def install_requirements(venv_dir):
    print("Installing requirements...")
    
    # Determine the python executable within the venv
    if platform.system() == "Windows":
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_bin = os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(python_bin):
        print(f"Error: Python executable not found at {python_bin}")
        print("Virtual environment creation might have failed.")
        sys.exit(1)

    try:
        # call python -m pip instead of pip directly
        subprocess.check_call([python_bin, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([python_bin, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def main():
    print("=== Music Downloader Setup ===")
    install_system_dependencies()
    venv_dir = create_virtual_env()
    install_requirements(venv_dir)
    print("\nSetup complete!")
    
    python_bin = os.path.join(venv_dir, "bin", "python")
    if platform.system() == "Windows":
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        
    print(f"To run the app: {python_bin} src/main.py")

if __name__ == "__main__":
    main()
