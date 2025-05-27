import subprocess
import sys
import os
import re

class WindowController:
    def __init__(self, custom_env=None):
        """Initialize the window controller with PowerShell path"""
        if custom_env and hasattr(custom_env, 'POWERSHELL'):
            self.powershell_path = custom_env.POWERSHELL
        else:
            # Default PowerShell path for WSL
            self.powershell_path = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

        # Get the directory where this script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.ps_script = os.path.join(self.script_dir, "window_manager.ps1")

        # Check if PowerShell script exists
        if not os.path.exists(self.ps_script):
            print(f"Error: PowerShell script not found at {self.ps_script}")
            print("Please ensure window_manager.ps1 is in the same directory as this Python script.")
            sys.exit(1)

    def run_powershell_command(self, action, window_index=None):
        """Execute PowerShell command with the given parameters"""
        cmd = [
            self.powershell_path,
            "-ExecutionPolicy", "Bypass",
            "-File", self.ps_script,
            "-Action", action
        ]

        if window_index:
            cmd.extend(["-WindowIndex", str(window_index)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), 1

    def list_windows(self):
        """List all active windows"""
        stdout, stderr, returncode = self.run_powershell_command("list")

        if returncode != 0:
            print(f"Error listing windows: {stderr}")
            return []

        print(stdout)

        # Parse the output to extract window information for programmatic use
        windows = []
        lines = stdout.split('\n')
        in_table = False

        for line in lines:
            if line.startswith('---'):
                in_table = True
                continue
            elif in_table and line.strip():
                # Parse table rows
                parts = line.split()
                if parts and parts[0].isdigit():
                    index = int(parts[0])
                    # Extract title, process, and state (handle spaces in titles)
                    match = re.match(r'^(\d+)\s+(.+?)\s+(\w+)\s+(\w+)\s*$', line)
                    if match:
                        windows.append({
                            'index': index,
                            'title': match.group(2).strip(),
                            'process': match.group(3),
                            'state': match.group(4)
                        })
            elif line.startswith('Usage Examples:'):
                break

        return windows

    def minimize_window(self, window_index):
        """Minimize a window by index"""
        stdout, stderr, returncode = self.run_powershell_command("minimize", window_index)

        if returncode != 0:
            print(f"Error: {stderr}")
        else:
            print(stdout.strip())

        return returncode == 0

    def maximize_window(self, window_index):
        """Maximize a window by index"""
        stdout, stderr, returncode = self.run_powershell_command("maximize", window_index)

        if returncode != 0:
            print(f"Error: {stderr}")
        else:
            print(stdout.strip())

        return returncode == 0

    def restore_window(self, window_index):
        """Restore a window by index"""
        stdout, stderr, returncode = self.run_powershell_command("restore", window_index)

        if returncode != 0:
            print(f"Error: {stderr}")
        else:
            print(stdout.strip())

        return returncode == 0

    def close_window(self, window_index):
        """Close a window by index"""
        stdout, stderr, returncode = self.run_powershell_command("close", window_index)

        if returncode != 0:
            print(f"Error: {stderr}")
        else:
            print(stdout.strip())

        return returncode == 0

    def focus_window(self, window_index):
        """Focus/bring to front a window by index"""
        stdout, stderr, returncode = self.run_powershell_command("focus", window_index)

        if returncode != 0:
            print(f"Error: {stderr}")
        else:
            print(stdout.strip())

        return returncode == 0

    def toggle_window(self, window_index):
        """Toggle maximize/restore a window by index"""
        stdout, stderr, returncode = self.run_powershell_command("toggle", window_index)

        if returncode != 0:
            print(f"Error: {stderr}")
        else:
            print(stdout.strip())

        return returncode == 0

def main():
    """Interactive command-line interface"""
    # You can pass your custom_env here if you have it
    # wc = WindowController(custom_env)
    wc = WindowController()

    print("Windows Controller - WSL Edition")
    print("=" * 40)

    while True:
        print("\nAvailable commands:")
        print("1. list - List all active windows")
        print("2. min <index> - Minimize window by index")
        print("3. max <index> - Maximize window by index")
        print("4. restore <index> - Restore window by index")
        print("5. close <index> - Close window by index")
        print("6. focus <index> - Focus window by index")
        print("7. toggle <index> - Toggle maximize/restore window by index")
        print("8. quit - Exit")

        try:
            command = input("\nEnter command: ").strip()

            if command.lower() in ['quit', 'q', 'exit']:
                break
            elif command.lower() == 'list':
                wc.list_windows()
            elif command.startswith('min '):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    wc.minimize_window(window_index=int(parts[1]))
                else:
                    print("Invalid format. Use: min <index>")
            elif command.startswith('max '):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    wc.maximize_window(window_index=int(parts[1]))
                else:
                    print("Invalid format. Use: max <index>")
            elif command.startswith('restore '):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    wc.restore_window(window_index=int(parts[1]))
                else:
                    print("Invalid format. Use: restore <index>")
            elif command.startswith('close '):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    wc.close_window(window_index=int(parts[1]))
                else:
                    print("Invalid format. Use: close <index>")
            elif command.startswith('focus '):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    wc.focus_window(window_index=int(parts[1]))
                else:
                    print("Invalid format. Use: focus <index>")
            elif command.startswith('toggle '):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    wc.toggle_window(window_index=int(parts[1]))
                else:
                    print("Invalid format. Use: toggle <index>")
            else:
                print("Unknown command. Type 'list' to see windows or 'quit' to exit.")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

# Example usage functions similar to your minimize_active_window
def minimize_window_by_index(index, custom_env=None):
    """Function to minimize a window by index - similar to your minimize_active_window"""
    wc = WindowController(custom_env)
    return wc.minimize_window(window_index=index)

def maximize_window_by_index(index, custom_env=None):
    """Function to maximize a window by index"""
    wc = WindowController(custom_env)
    return wc.maximize_window(window_index=index)

def restore_window_by_index(index, custom_env=None):
    """Function to restore a window by index"""
    wc = WindowController(custom_env)
    return wc.restore_window(window_index=index)

def close_window_by_index(index, custom_env=None):
    """Function to close a window by index"""
    wc = WindowController(custom_env)
    return wc.close_window(window_index=index)

def list_active_windows(custom_env=None):
    """Function to list all active windows"""
    wc = WindowController(custom_env)
    return wc.list_windows()

def toggle_window_by_index(index, custom_env=None):
    """Function to toggle maximize/restore a window by index"""
    wc = WindowController(custom_env)
    return wc.toggle_window(window_index=index)

if __name__ == "__main__":
    main()
