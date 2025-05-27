import subprocess
import sys
import os

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
GRAY = "\033[90m"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii_banner():
    print(f"""
{CYAN}{BOLD}╔════════════════════════════════════════════════════════════╗
║                    {GREEN}🚀 SSH File Transfer Tool{CYAN}                   ║
║                        {YELLOW}Powered by SCP{CYAN}                          ║
╚════════════════════════════════════════════════════════════╝{RESET}
""")

def print_separator():
    print(f"{GRAY}{'─' * 60}{RESET}")

def get_input(prompt, default=None, required=True):
    """Enhanced input function with validation"""
    while True:
        label = f"{YELLOW}➤ {prompt}{RESET}"
        if default:
            label += f" {GRAY}[{default}]{RESET}"
        label += f"{WHITE}: "

        user_input = input(label).strip()
        result = user_input or default

        if required and not result:
            print(f"{RED}⚠️  This field is required. Please enter a value.{RESET}")
            continue

        return result

def expand_path(path):
    """Expand user home directory and environment variables in path"""
    if path:
        # Expand ~ to user home directory
        path = os.path.expanduser(path)
        # Expand environment variables
        path = os.path.expandvars(path)
    return path

def validate_file_path(file_path, check_exists=True):
    """Validate if a file path exists (for local files)"""
    if check_exists and not os.path.exists(file_path):
        print(f"{YELLOW}⚠️  Warning: File '{file_path}' does not exist locally.{RESET}")
        confirm = input(f"{YELLOW}Continue anyway? (y/N): {RESET}").strip().lower()
        return confirm in ['y', 'yes']
    return True

def run_scp_command(command):
    """Execute SCP command with enhanced feedback"""
    try:
        print(f"\n{CYAN}🔄 Starting file transfer...{RESET}")
        print(f"{GRAY}Command: {' '.join(command)}{RESET}")
        print_separator()

        # Run with real-time output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 universal_newlines=True, bufsize=1)

        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())

        process.wait()

        if process.returncode == 0:
            print(f"\n{GREEN}✅ Transfer completed successfully!{RESET}")
            print(f"{GREEN}🎉 File has been transferred.{RESET}")
        else:
            print(f"\n{RED}❌ Transfer failed with exit code {process.returncode}{RESET}")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Transfer interrupted by user.{RESET}")
    except Exception as e:
        print(f"\n{RED}❌ Unexpected error occurred:{RESET}")
        print(f"{RED}{str(e)}{RESET}")

def show_connection_info(username, host, port):
    """Display connection information in a formatted way"""
    print(f"\n{CYAN}📡 Connection Details:{RESET}")
    print(f"   {WHITE}User:{RESET} {GREEN}{username}{RESET}")
    print(f"   {WHITE}Host:{RESET} {GREEN}{host}{RESET}")
    print(f"   {WHITE}Port:{RESET} {GREEN}{port}{RESET}")
    print_separator()

def download_file():
    print(f"\n{GREEN}{BOLD}📥 DOWNLOAD MODE{RESET}")
    print(f"{GRAY}Transfer files from remote SSH server to local machine{RESET}\n")

    # Get connection details
    username = get_input("SSH Username")
    host = get_input("SSH Host (IP or domain)")
    port = get_input("SSH Port", "22")

    show_connection_info(username, host, port)

    # Get file paths
    remote_path = get_input("Remote file path (full path on server)")
    local_path = get_input("Local destination path", ".")

    # Expand local path (handle ~ and environment variables)
    local_path = expand_path(local_path)

    # Show transfer summary
    print(f"\n{MAGENTA}📋 Transfer Summary:{RESET}")
    print(f"   {WHITE}From:{RESET} {CYAN}{username}@{host}:{remote_path}{RESET}")
    print(f"   {WHITE}To:{RESET}   {CYAN}{local_path}{RESET}")

    # Confirm before proceeding
    print(f"\n{YELLOW}Ready to start download?{RESET}")
    confirm = input(f"{YELLOW}Press Enter to continue or 'q' to quit: {RESET}").strip().lower()

    if confirm == 'q':
        print(f"{YELLOW}📤 Download cancelled.{RESET}")
        return

    scp_cmd = ["scp", "-P", port, f"{username}@{host}:{remote_path}", local_path]
    run_scp_command(scp_cmd)

def upload_file():
    print(f"\n{GREEN}{BOLD}📤 UPLOAD MODE{RESET}")
    print(f"{GRAY}Transfer files from local machine to remote SSH server{RESET}\n")

    # Get local file first
    local_path = get_input("Local file path to upload")

    # Expand local path (handle ~ and environment variables)
    local_path = expand_path(local_path)

    # Validate local file exists
    if not validate_file_path(local_path):
        print(f"{RED}❌ Aborted due to file validation.{RESET}")
        return

    # Get connection details
    username = get_input("SSH Username")
    host = get_input("SSH Host (IP or domain)")
    port = get_input("SSH Port", "22")

    show_connection_info(username, host, port)

    # Get remote destination
    remote_path = get_input("Remote destination path")

    # Show transfer summary
    print(f"\n{MAGENTA}📋 Transfer Summary:{RESET}")
    print(f"   {WHITE}From:{RESET} {CYAN}{local_path}{RESET}")
    print(f"   {WHITE}To:{RESET}   {CYAN}{username}@{host}:{remote_path}{RESET}")

    # Show file info if available
    try:
        file_size = os.path.getsize(local_path)
        file_size_mb = file_size / (1024 * 1024)
        print(f"   {WHITE}Size:{RESET} {GREEN}{file_size_mb:.2f} MB{RESET}")
    except:
        pass

    # Confirm before proceeding
    print(f"\n{YELLOW}Ready to start upload?{RESET}")
    confirm = input(f"{YELLOW}Press Enter to continue or 'q' to quit: {RESET}").strip().lower()

    if confirm == 'q':
        print(f"{YELLOW}📤 Upload cancelled.{RESET}")
        return

    scp_cmd = ["scp", "-P", port, local_path, f"{username}@{host}:{remote_path}"]
    run_scp_command(scp_cmd)

def show_help():
    """Display help information"""
    print(f"\n{CYAN}{BOLD}📚 HELP & TIPS{RESET}")
    print(f"""
{WHITE}Common Usage Examples:{RESET}
  • Remote path: {GREEN}/home/user/document.txt{RESET}
  • Local path:  {GREEN}~/Downloads/{RESET} or {GREEN}/Users/john/Desktop/{RESET}

{WHITE}Path Expansion:{RESET}
  • {GREEN}~{RESET} expands to your home directory
  • {GREEN}~/Downloads/{RESET} becomes {GREEN}/Users/yourname/Downloads/{RESET}
  • Environment variables like {GREEN}$HOME{RESET} are also expanded

{WHITE}SSH Connection:{RESET}
  • Make sure you can SSH to the server first
  • Use SSH keys for passwordless authentication
  • Default SSH port is 22

{WHITE}File Paths:{RESET}
  • Use absolute paths when in doubt
  • For directories, ensure they exist on the destination
  • Use quotes for paths with spaces
""")
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def main():
    try:
        clear_screen()
        print_ascii_banner()

        while True:
            print(f"\n{CYAN}{BOLD}🎯 Choose an option:{RESET}")
            print(f"{BLUE}  {BOLD}1.{RESET} {WHITE}📥 Download file from SSH server{RESET}")
            print(f"{BLUE}  {BOLD}2.{RESET} {WHITE}📤 Upload file to SSH server{RESET}")
            print(f"{BLUE}  {BOLD}3.{RESET} {WHITE}📚 Show help & tips{RESET}")
            print(f"{BLUE}  {BOLD}4.{RESET} {WHITE}❌ Exit{RESET}")

            choice = get_input("Your choice", "1", required=False)

            if choice == "1":
                download_file()
            elif choice == "2":
                upload_file()
            elif choice == "3":
                show_help()
            elif choice == "4" or choice.lower() in ['exit', 'quit', 'q']:
                print(f"\n{GREEN}👋 Thanks for using SSH File Transfer Tool!{RESET}")
                break
            else:
                print(f"{RED}❌ Invalid choice. Please select 1-4.{RESET}")

            # Ask if user wants to continue
            if choice in ["1", "2"]:
                print(f"\n{CYAN}Would you like to perform another transfer?{RESET}")
                continue_choice = input(f"{YELLOW}Press Enter to continue or 'q' to quit: {RESET}").strip().lower()
                if continue_choice == 'q':
                    print(f"\n{GREEN}👋 Thanks for using SSH File Transfer Tool!{RESET}")
                    break
                clear_screen()
                print_ascii_banner()

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Goodbye!{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
