# run via powershell to get the GUI access for the program
import subprocess
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

directory = input("Enter working directory or enter quit to exit: ")
if directory == "quit":
    print("Exiting.")
    exit(0)

cmd = input("Enter full cmd to run: ")

# Build full bash command to run inside WSL
bash_cmd = f"cd '{directory}' && {cmd}"
print(bash_cmd)

# Run it through PowerShell
subprocess.run([
    POWERSHELL,
    "-Command",
    f"wsl.exe -d Ubuntu -- bash -c \"{bash_cmd}\""
])
