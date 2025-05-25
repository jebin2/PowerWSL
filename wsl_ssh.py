import subprocess
import os
import sys

IP_STORE = os.path.expanduser("~/.wsl_ssh_ip")
LISTEN_PORT = 2222
LISTEN_ADDRESS = "0.0.0.0"

def run(cmd, shell=True):
    print(f"[>] {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Error:\n{result.stderr.strip()}")
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
    print(f"[+] Removing portproxy to {ip}...")
    run(f'powershell.exe -Command "netsh interface portproxy delete v4tov4 listenport={LISTEN_PORT} listenaddress={LISTEN_ADDRESS}"')

def add_portproxy(ip):
    print(f"[+] Adding portproxy to {ip}...")
    run(f'powershell.exe -Command "netsh interface portproxy add v4tov4 listenport={LISTEN_PORT} listenaddress={LISTEN_ADDRESS} connectport={LISTEN_PORT} connectaddress={ip}"')

def restart_ssh():
    print("[+] Restarting SSH service...")
    run("sudo service ssh restart")

def install_ssh(username, password):
    print("\n[+] Installing openssh-server...")
    run("sudo apt update && sudo apt install -y openssh-server")

    print("[+] Setting user password...")
    run(f"echo '{username}:{password}' | sudo chpasswd")

    print("[+] Configuring SSH settings...")
    run("sudo sed -i 's/^#*Port .*/Port 2222/' /etc/ssh/sshd_config")
    run("sudo sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config")
    run("sudo sed -i 's/^#*PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config")

    restart_ssh()
    current_ip = get_current_wsl_ip()
    save_ip(current_ip)
    add_portproxy(current_ip)

    print("\n[✓] SSH is set up and forwarded!")
    print(f"    ➤ WSL IP: {current_ip}")
    print(f"    ➤ Windows Port: {LISTEN_PORT} → WSL {LISTEN_PORT}")
    print("    ➤ Test: ssh youruser@localhost -p 2222")
    print("    ➤ Or from iPhone via Tailscale IP")

def update_portproxy():
    current_ip = get_current_wsl_ip()
    saved_ip = read_stored_ip()

    if saved_ip == current_ip:
        print(f"[✓] WSL IP unchanged ({current_ip}) — nothing to update.")
    else:
        print(f"[!] WSL IP changed: {saved_ip or 'None'} → {current_ip}")
        if saved_ip:
            delete_portproxy(saved_ip)
        add_portproxy(current_ip)
        save_ip(current_ip)
        restart_ssh()
        print("[✓] Portproxy re-bound to new IP.")

def cleanup_all():
    saved_ip = read_stored_ip()
    if saved_ip:
        delete_portproxy(saved_ip)
        os.remove(IP_STORE)
        print("[✓] Portproxy removed.")

    print("[+] Stopping SSH service...")
    run("sudo service ssh stop")
    print("[✓] Cleanup complete.")

def auto_mode():
    print("[✓] Auto mode: Checking and updating portproxy if needed...")
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
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    if "--auto" in sys.argv:
        auto_mode()
    else:
        main_menu()
