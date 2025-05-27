param(
    [Parameter(Mandatory=$true)]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [int]$WindowIndex
)

# Add necessary types for window management
Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    using System.Text;

    public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool IsWindowVisible(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool IsIconic(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool IsZoomed(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

        [DllImport("user32.dll")]
        public static extern int GetWindowTextLength(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        [DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

        [DllImport("kernel32.dll")]
        public static extern uint GetCurrentThreadId();

        [DllImport("user32.dll")]
        public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);

        [DllImport("user32.dll")]
        public static extern bool BringWindowToTop(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

        [DllImport("user32.dll")]
        public static extern bool AllowSetForegroundWindow(uint dwProcessId);

        [DllImport("user32.dll")]
        public static extern bool SetActiveWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern IntPtr SetFocus(IntPtr hWnd);

        public const int SW_HIDE = 0;
        public const int SW_SHOWNORMAL = 1;
        public const int SW_SHOWMINIMIZED = 2;
        public const int SW_SHOWMAXIMIZED = 3;
        public const int SW_SHOWNOACTIVATE = 4;
        public const int SW_SHOW = 5;
        public const int SW_MINIMIZE = 6;
        public const int SW_SHOWMINNOACTIVE = 7;
        public const int SW_SHOWNA = 8;
        public const int SW_RESTORE = 9;
        public const int WM_CLOSE = 0x0010;
        public const uint SWP_NOSIZE = 0x0001;
        public const uint SWP_NOMOVE = 0x0002;
        public const uint SWP_SHOWWINDOW = 0x0040;
        public static readonly IntPtr HWND_TOP = new IntPtr(0);
        public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
        public static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
    }
"@

function Get-WindowTitle {
    param([IntPtr]$hwnd)

    $length = [Win32]::GetWindowTextLength($hwnd)
    if ($length -gt 0) {
        $sb = New-Object System.Text.StringBuilder($length + 1)
        [Win32]::GetWindowText($hwnd, $sb, $sb.Capacity) | Out-Null
        return $sb.ToString()
    }
    return ""
}

function Get-WindowState {
    param([IntPtr]$hwnd)

    if ([Win32]::IsIconic($hwnd)) {
        return "Minimized"
    }
    elseif ([Win32]::IsZoomed($hwnd)) {
        return "Maximized"
    }
    else {
        return "Normal"
    }
}

function Get-ActiveWindows {
    $windows = @()
    $processes = Get-Process | Where-Object { $_.MainWindowTitle -ne "" }

    foreach ($process in $processes) {
        if ([Win32]::IsWindowVisible($process.MainWindowHandle)) {
            $title = Get-WindowTitle -hwnd $process.MainWindowHandle
            if ($title -and $title.Trim() -ne "") {
                $state = Get-WindowState -hwnd $process.MainWindowHandle

                $windowInfo = [PSCustomObject]@{
                    Index = $windows.Count + 1
                    Title = $title
                    ProcessName = $process.ProcessName
                    ProcessId = $process.Id
                    Handle = $process.MainWindowHandle
                    State = $state
                }
                $windows += $windowInfo
            }
        }
    }

    return $windows
}

function List-Windows {
    $windows = Get-ActiveWindows

    if ($windows.Count -eq 0) {
        Write-Output "No active windows found."
        return
    }

    Write-Output ("=" * 100)
    Write-Output "Active Windows List"
    Write-Output ("=" * 100)
    Write-Output ("{0,-3} {1,-50} {2,-20} {3,-12}" -f "#", "Title", "Process", "State")
    Write-Output ("-" * 100)

    foreach ($window in $windows) {
        $title = if ($window.Title.Length -gt 47) { $window.Title.Substring(0, 47) + "..." } else { $window.Title }
        $process = if ($window.ProcessName.Length -gt 17) { $window.ProcessName.Substring(0, 17) + "..." } else { $window.ProcessName }

        Write-Output ("{0,-3} {1,-50} {2,-20} {3,-12}" -f $window.Index, $title, $process, $window.State)
    }

    Write-Output ""
    Write-Output "Usage Examples:"
    Write-Output "  powershell.exe -File window_manager.ps1 -Action minimize -WindowIndex 1"
    Write-Output "  powershell.exe -File window_manager.ps1 -Action maximize -WindowIndex 2"
    Write-Output "  powershell.exe -File window_manager.ps1 -Action restore -WindowIndex 3"
    Write-Output "  powershell.exe -File window_manager.ps1 -Action close -WindowIndex 2"
}

function Force-FocusWindow {
    param([IntPtr]$hwnd)

    try {
        # Get current foreground window and thread
        $foregroundWindow = [Win32]::GetForegroundWindow()
        $currentThread = [Win32]::GetCurrentThreadId()

        # Get target window thread
        $targetProcessId = 0
        $targetThread = [Win32]::GetWindowThreadProcessId($hwnd, [ref]$targetProcessId)

        # Get foreground window thread
        $foregroundProcessId = 0
        $foregroundThread = [Win32]::GetWindowThreadProcessId($foregroundWindow, [ref]$foregroundProcessId)

        # Method 1: If window is minimized, restore it first
        if ([Win32]::IsIconic($hwnd)) {
            [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) | Out-Null
            Start-Sleep -Milliseconds 100
        }

        # Method 2: Allow the target process to set foreground window
        [Win32]::AllowSetForegroundWindow($targetProcessId) | Out-Null

        # Method 3: Attach thread inputs if different threads
        $attached = $false
        if ($currentThread -ne $targetThread) {
            $attached = [Win32]::AttachThreadInput($currentThread, $targetThread, $true)
        }
        if ($foregroundThread -ne $targetThread -and $foregroundThread -ne $currentThread) {
            [Win32]::AttachThreadInput($foregroundThread, $targetThread, $true) | Out-Null
        }

        # Method 4: Multiple attempts to bring window to front
        [Win32]::BringWindowToTop($hwnd) | Out-Null
        [Win32]::SetWindowPos($hwnd, [Win32]::HWND_TOP, 0, 0, 0, 0, [Win32]::SWP_NOMOVE -bor [Win32]::SWP_NOSIZE -bor [Win32]::SWP_SHOWWINDOW) | Out-Null
        [Win32]::SetForegroundWindow($hwnd) | Out-Null
        [Win32]::SetActiveWindow($hwnd) | Out-Null
        [Win32]::SetFocus($hwnd) | Out-Null

        # Brief moment to let it take effect
        Start-Sleep -Milliseconds 50

        # Method 5: If still not focused, try the topmost trick
        $currentForeground = [Win32]::GetForegroundWindow()
        if ($currentForeground -ne $hwnd) {
            # Temporarily make it topmost, then remove topmost
            [Win32]::SetWindowPos($hwnd, [Win32]::HWND_TOPMOST, 0, 0, 0, 0, [Win32]::SWP_NOMOVE -bor [Win32]::SWP_NOSIZE) | Out-Null
            Start-Sleep -Milliseconds 10
            [Win32]::SetWindowPos($hwnd, [Win32]::HWND_NOTOPMOST, 0, 0, 0, 0, [Win32]::SWP_NOMOVE -bor [Win32]::SWP_NOSIZE) | Out-Null
            [Win32]::SetForegroundWindow($hwnd) | Out-Null
        }

        # Detach thread inputs
        if ($attached) {
            [Win32]::AttachThreadInput($currentThread, $targetThread, $false) | Out-Null
        }
        if ($foregroundThread -ne $targetThread -and $foregroundThread -ne $currentThread) {
            [Win32]::AttachThreadInput($foregroundThread, $targetThread, $false) | Out-Null
        }

        # Check if we succeeded
        Start-Sleep -Milliseconds 100
        $finalForeground = [Win32]::GetForegroundWindow()
        return $finalForeground -eq $hwnd

    } catch {
        Write-Output "DEBUG: Exception in Force-FocusWindow: $($_.Exception.Message)"
        return $false
    }
}

function Control-Window {
    param(
        [string]$Action,
        [int]$WindowIndex
    )

    $windows = Get-ActiveWindows

    if ($windows.Count -eq 0) {
        Write-Output "ERROR: No active windows found."
        return
    }

    # Find window by index
    if ($WindowIndex -gt 0 -and $WindowIndex -le $windows.Count) {
        $targetWindow = $windows[$WindowIndex - 1]
    } else {
        Write-Output "ERROR: Window index $WindowIndex is out of range (1-$($windows.Count))."
        return
    }

    $hwnd = $targetWindow.Handle
    $title = $targetWindow.Title
    $success = $false

    switch ($Action.ToLower()) {
        "minimize" {
            $success = [Win32]::ShowWindow($hwnd, [Win32]::SW_MINIMIZE)
            if ($success) {
                Write-Output "SUCCESS: Minimized '$title'"
            } else {
                Write-Output "ERROR: Failed to minimize '$title'"
            }
        }
        "maximize" {
            $success = [Win32]::ShowWindow($hwnd, [Win32]::SW_SHOWMAXIMIZED)
            if ($success) {
                Write-Output "SUCCESS: Maximized '$title'"
            } else {
                Write-Output "ERROR: Failed to maximize '$title'"
            }
        }
        "restore" {
            $success = [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE)
            if ($success) {
                Write-Output "SUCCESS: Restored '$title'"
            } else {
                Write-Output "ERROR: Failed to restore '$title'"
            }
        }
        "show" {
            $success = [Win32]::ShowWindow($hwnd, [Win32]::SW_SHOW)
            if ($success) {
                Write-Output "SUCCESS: Showed '$title'"
            } else {
                Write-Output "ERROR: Failed to show '$title'"
            }
        }
        "close" {
            $success = [Win32]::PostMessage($hwnd, [Win32]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero)
            if ($success) {
                Write-Output "SUCCESS: Sent close message to '$title'"
            } else {
                Write-Output "ERROR: Failed to close '$title'"
            }
        }
        "focus" {
            $success = Force-FocusWindow -hwnd $hwnd
            if ($success) {
                Write-Output "SUCCESS: Focused '$title'"
            } else {
                Write-Output "WARNING: Attempted to focus '$title' - it may be blinking in taskbar due to Windows focus restrictions"
            }
        }
        "toggle" {
            # Toggle between maximized and restored state
            $currentState = Get-WindowState -hwnd $hwnd
            if ($currentState -eq "Maximized") {
                $success = [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE)
                if ($success) {
                    Write-Output "SUCCESS: Restored '$title' (was maximized)"
                } else {
                    Write-Output "ERROR: Failed to restore '$title'"
                }
            } else {
                # If minimized, restore first, then maximize
                if ($currentState -eq "Minimized") {
                    [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) | Out-Null
                    Start-Sleep -Milliseconds 100
                }
                $success = [Win32]::ShowWindow($hwnd, [Win32]::SW_SHOWMAXIMIZED)
                if ($success) {
                    Write-Output "SUCCESS: Maximized '$title' (was $($currentState.ToLower()))"
                } else {
                    Write-Output "ERROR: Failed to maximize '$title'"
                }
            }
        }
        default {
            Write-Output "ERROR: Unknown action '$Action'. Supported actions: list, minimize, maximize, restore, show, close, focus, toggle"
        }
    }
}

# Main execution logic
switch ($Action.ToLower()) {
    "list" {
        List-Windows
    }
    { $_ -in @("minimize", "maximize", "restore", "show", "close", "focus", "toggle") } {
        Control-Window -Action $Action -WindowIndex $WindowIndex
    }
    default {
        Write-Output "ERROR: Unknown action '$Action'"
        Write-Output ""
        Write-Output "Supported actions:"
        Write-Output "  list                           - List all active windows"
        Write-Output "  minimize -WindowIndex <number> - Minimize window by index"
        Write-Output "  maximize -WindowIndex <number> - Maximize window by index"
        Write-Output "  restore -WindowIndex <number>  - Restore window by index"
        Write-Output "  show -WindowIndex <number>     - Show window by index"
        Write-Output "  close -WindowIndex <number>    - Close window by index"
        Write-Output "  focus -WindowIndex <number>    - Focus window by index"
        Write-Output "  toggle -WindowIndex <number>   - Toggle maximize/restore window by index"
        Write-Output ""
        Write-Output "Examples:"
        Write-Output "  powershell.exe -File window_manager.ps1 -Action list"
        Write-Output "  powershell.exe -File window_manager.ps1 -Action minimize -WindowIndex 1"
        Write-Output "  powershell.exe -File window_manager.ps1 -Action maximize -WindowIndex 2"
        Write-Output "  powershell.exe -File window_manager.ps1 -Action toggle -WindowIndex 1"
    }
}
