# run via powershell to get the GUI access for the program
import subprocess
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

print("1. gc")
print("2. xp")
print("3. other")
print("0. Exit")

choice = input("Choose an directory option: ")
if choice == "1":
    CWD = os.getenv("CAPTIONCREATOR")
elif choice == "2":
    CWD = os.getenv("XPAL")
elif choice == "0":
    print("Exiting.")
    exit(0)
else:
    CWD = input("Enter custom directory: ")

cmd = input("Enter full cmd to run: ")

# Build full bash command to run inside WSL
bash_cmd = f"cd '{CWD}' && {cmd}"

# Run it through PowerShell
subprocess.run([
    POWERSHELL,
    "-Command",
    f"wsl.exe -d Ubuntu -- bash -c \"{bash_cmd}\""
])
