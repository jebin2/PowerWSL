import subprocess
import os
import sys
from datetime import datetime

IP_STORE = os.path.expanduser("~/.wsl_ssh_ip")
LISTEN_PORT = 2222
LISTEN_ADDRESS = "0.0.0.0"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")

def run(cmd, shell=True):
    log(f"[>] {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"[!] Error:\n{result.stderr.strip()}")
    return result.stdout.strip()

def get_current_wsl_ip():
    return run("hostname -I").split()[0]

def read_stored_ip():
    if os.path.exists(IP_STORE):
        with open(IP_STORE, "r") as f:
            return f.read().strip()
    return None

def save_ip(ip):
    with open(IP_STORE, "w") as f:
        f.write(ip)

def delete_portproxy(ip):
    log(f"[+] Removing portproxy to {ip}...")
    run(f'powershell.exe -Command "netsh interface portproxy delete v4tov4 listenport={LISTEN_PORT} listenaddress={LISTEN_ADDRESS}"')

def add_portproxy(ip):
    log(f"[+] Adding portproxy to {ip}...")
    run(f'powershell.exe -Command "netsh interface portproxy add v4tov4 listenport={LISTEN_PORT} listenaddress={LISTEN_ADDRESS} connectport={LISTEN_PORT} connectaddress={ip}"')

def restart_ssh():
    log("[+] Restarting SSH service...")
    run("sudo service ssh restart")

def install_ssh(username, password):
    log("[+] Installing openssh-server...")
    run("sudo apt update && sudo apt install -y openssh-server")

    log("[+] Setting user password...")
    run(f"echo '{username}:{password}' | sudo chpasswd")

    log("[+] Configuring SSH settings...")
    run("sudo sed -i 's/^#*Port .*/Port 2222/' /etc/ssh/sshd_config")
    run("sudo sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config")
    run("sudo sed -i 's/^#*PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config")

    restart_ssh()
    current_ip = get_current_wsl_ip()
    save_ip(current_ip)
    add_portproxy(current_ip)

    log("[✓] SSH is set up and forwarded!")
    log(f"    ➤ WSL IP: {current_ip}")
    log(f"    ➤ Windows Port: {LISTEN_PORT} → WSL {LISTEN_PORT}")
    log("    ➤ Test: ssh youruser@localhost -p 2222")
    log("    ➤ Or from iPhone via Tailscale IP")

def update_portproxy():
    current_ip = get_current_wsl_ip()
    saved_ip = read_stored_ip()

    if saved_ip == current_ip:
        log(f"[✓] WSL IP unchanged ({current_ip}) — nothing to update.")
    else:
        log(f"[!] WSL IP changed: {saved_ip or 'None'} → {current_ip}")
        if saved_ip:
            delete_portproxy(saved_ip)
        add_portproxy(current_ip)
        save_ip(current_ip)
        restart_ssh()
        log("[✓] Portproxy re-bound to new IP.")

def cleanup_all():
    saved_ip = read_stored_ip()
    if saved_ip:
        delete_portproxy(saved_ip)
        os.remove(IP_STORE)
        log("[✓] Portproxy removed.")

    log("[+] Stopping SSH service...")
    run("sudo service ssh stop")
    log("[✓] Cleanup complete.")

def auto_mode():
    log("[✓] Auto mode: Checking and updating portproxy if needed...")
    update_portproxy()

def main_menu():
    while True:
        print("\n=== WSL SSH + Portproxy Manager ===")
        print("\nWarning: Run this in Administrator.")
        print("1. Install & configure SSH (with portproxy)")
        print("2. Rebind portproxy if WSL IP has changed")
        print("3. Remove SSH & portproxy configuration")
        print("0. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter your WSL username: ").strip()
            password = input("Set a password for this user: ").strip()
            install_ssh(username, password)
        elif choice == "2":
            update_portproxy()
        elif choice == "3":
            cleanup_all()
        elif choice == "0":
            log("Exiting.")
            sys.exit(0)
        else:
            log("Invalid option. Try again.")

if __name__ == "__main__":
    if "--auto" in sys.argv:
        auto_mode()
    else:
        main_menu()
