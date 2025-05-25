# run via powershell to get the GUI access for the program
import subprocess

POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

print("1. CaptionCreator")
print("2. XPal")
print("0. Exit")

choice = input("Choose an option: ")
if choice == "1":
    CWD = "/home/jebineinstein/git/CaptionCreator"
elif choice == "2":
    CWD = "/home/jebineinstein/git/XPal"
elif choice == "0":
    print("Exiting.")
    exit(0)

cmd = input("Enter full cmd to run: ")

# Build full bash command to run inside WSL
bash_cmd = f"cd '{CWD}' && {cmd}"

# Run it through PowerShell
subprocess.run([
    POWERSHELL,
    "-Command",
    f"wsl.exe -d Ubuntu -- bash -c \"{bash_cmd}\""
])
