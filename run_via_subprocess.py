import subprocess
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

directory = input("Enter working directory or enter quit to exit: ")
if directory.lower() == "quit":
    print("Exiting.")
    exit(0)

cmd = input("Enter full cmd to run: ")

# Force unbuffered output
full_cmd = f"export DISPLAY=:0 && cd '{directory}' && {cmd}"

result = subprocess.run(
    ["bash", "-c", full_cmd],
    env={**os.environ, "PYTHONUNBUFFERED": "1"}
)
