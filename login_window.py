import tkinter as tk
import ctypes
import keyboard
import winreg

def toggle_sign_out(disable=True):
    """Hides or restores the 'Sign out' button on the Ctrl+Alt+Del screen."""
    try:
        # Path for Explorer policies (where the Logoff button is controlled)
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        
        # Create or open the key
        registry_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        
        # 1 hides the Sign Out button, 0 restores it
        value = 1 if disable else 0
        winreg.SetValueEx(registry_key, "NoLogoff", 0, winreg.REG_DWORD, value)
        winreg.SetValueEx(registry_key, "NoClose", 0, winreg.REG_DWORD, value)
        # winreg.SetValueEx(registry_key, "HideFastUserSwitching", 0, winreg.REG_DWORD, 1) # different registry path n key
        winreg.CloseKey(registry_key)
    except Exception as e:
        print(f"Registry edit failed (Run as Admin required): {e}")

# --- CONFIGURATION ---
# Set to True for a normal, testable window with an 'X' button.
# Set to False for a fullscreen, unoverridable lock overlay.
# IS_CLOSEABLE = False   
IS_CLOSEABLE = True   

# Hardcoded credentials for this example
VALID_USER = "admin"
VALID_PASS = "1234"

# Win32 API Constants for Topmost enforcement
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002



def enforce_topmost(window):
    """Forces the window to the top and retains keyboard focus."""
    if not IS_CLOSEABLE:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        ctypes.windll.user32.SetWindowPos(
            hwnd, 
            HWND_TOPMOST, 
            0, 0, 0, 0, 
            SWP_NOMOVE | SWP_NOSIZE 
        )
        
        # ADD THIS: Force Tkinter to constantly steal back keyboard focus
        window.focus_force()
        
        window.after(50, enforce_topmost, window)


def block_system_keys():
    """Suppresses all system, navigation, and modifier keys, leaving only typing keys."""
    
    banned_keys = [
        # Modifiers & System
        'ctrl', 'left ctrl', 'right ctrl',
        'alt', 'left alt', 'right alt',
        'windows', 'left windows', 'right windows',
        'menu', 'esc', 'print screen', 'scroll lock', 'pause', 'caps lock',
        
        # Navigation & Editing
        'insert', 'delete', 'home', 'end', 'page up', 'page down',
        'up', 'down', 'left', 'right'
    ]
    
    # Add F1 through F24 to the banned list
    for i in range(1, 25):
        banned_keys.append(f'f{i}')
        
    # Block all individual keys in the list
    for key in banned_keys:
        keyboard.block_key(key)
        
    # Explicitly block system combos just in case Windows tries to grab them first
    keyboard.add_hotkey('alt+tab', lambda: None, suppress=True)
    keyboard.add_hotkey('alt+esc', lambda: None, suppress=True)
    keyboard.add_hotkey('ctrl+esc', lambda: None, suppress=True)
    keyboard.add_hotkey('ctrl+shift+esc', lambda: None, suppress=True)

def unblock_system_keys():
    """Removes all keyboard hooks so the PC functions normally again."""
    keyboard.unhook_all()

def remove_all_security_layer():
    unblock_system_keys()
    toggle_sign_out(disable=False)





def attempt_login(event=None):
    """Checks the credentials and closes the overlay if correct."""
    user = username_entry.get()
    pwd = password_entry.get()
    
    if user == VALID_USER and pwd == VALID_PASS:
        root.destroy() # Correct password destroys the overlay, unlocking the PC
        remove_all_security_layer()
    
    else:
        error_label.config(text="Access Denied. Incorrect credentials.")
        password_entry.delete(0, tk.END)

# 1. Setup Base Window
root = tk.Tk()
root.configure(bg="#1e1e1e") # Dark background

if IS_CLOSEABLE:
    root.title("System Login (Windowed Mode)")
    root.geometry("450x350")
    root.attributes('-fullscreen', True)
    root.wm_attributes("-topmost", True)
    block_system_keys()
    toggle_sign_out(disable=True)
else:
    root.title("System Locked")
    # Make it exactly the size of the user's screen
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry(f"{screen_w}x{screen_h}+0+0")
    
    # Remove window borders, taskbar icon, and close buttons
    root.overrideredirect(True)

    block_system_keys()
    
    # Start the aggressive topmost loop to prevent other apps from overriding it
    root.after(100, lambda: enforce_topmost(root))

# 2. UI Design: Centered Login Box
login_frame = tk.Frame(root, bg="#2d2d2d", padx=40, pady=40, highlightbackground="#444444", highlightthickness=2)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

# Title
tk.Label(login_frame, text="PC AUTHENTICATION", font=("Consolas", 18, "bold"), bg="#2d2d2d", fg="white").pack(pady=(0, 20))

# Username Field
tk.Label(login_frame, text="Username:", font=("Consolas", 12), bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
username_entry = tk.Entry(login_frame, font=("Consolas", 14), width=25, bg="#1e1e1e", fg="white", insertbackground="white")
username_entry.pack(pady=(0, 15))
username_entry.focus() # Auto-select the username box

# Password Field
tk.Label(login_frame, text="Password:", font=("Consolas", 12), bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
password_entry = tk.Entry(login_frame, font=("Consolas", 14), width=25, bg="#1e1e1e", fg="white", insertbackground="white", show="*")
password_entry.pack(pady=(0, 10))

# Error Label (Empty by default)
error_label = tk.Label(login_frame, text="", font=("Consolas", 10), bg="#2d2d2d", fg="#ff5555")
error_label.pack(pady=(0, 10))

# Login Button
login_button = tk.Button(login_frame, text="UNLOCK", font=("Consolas", 12, "bold"), bg="#007acc", fg="white", 
                         activebackground="#005999", activeforeground="white", relief="flat", command=attempt_login)
login_button.pack(fill="x", pady=(10, 0))

# Bind the Enter key so the user doesn't have to click the button
root.bind('<Return>', attempt_login)

# 3. Run Application
root.mainloop()