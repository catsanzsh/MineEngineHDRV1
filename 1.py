import tkinter as tk
from tkinter import ttk
import os
import subprocess
import shutil  # For shutil.which to find Java
import uuid    # For generating UUIDs for offline play
import random  # For slightly varying player name

# Try to import the library, guide user if not found
try:
    import minecraft_launcher_lib
except ImportError:
    # This message will print to console if the library isn't installed.
    # A GUI pop-up would be more user-friendly in a real app.
    print("喵! Error: minecraft-launcher-lib is not installed!")
    print("Please install it by running: pip install minecraft-launcher-lib")
    # Consider exiting or disabling functionality if critical
    # For this example, we'll let it proceed and error out if functions are called.
    # exit() # Uncomment to exit if the library is critical for startup

class AdvancedMinecraftLauncher:
    def __init__(self, root):
        self.root = root
        root.title("Cute & Advanced Minecraft Launcher 喵~")
        root.minsize(450, 300) # A bit more space for messages

        self.version_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready, nya~ Fetch versions to start!")

        # --- UI Elements ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="Select Minecraft Version:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.version_combo = ttk.Combobox(main_frame, textvariable=self.version_var, state="readonly", width=35)
        self.version_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Refresh Versions 喵!", command=self.fetch_versions_from_lib).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download/Install Version", command=self.install_selected_version).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Launch Game Purr!", command=self.launch_selected_game).pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=400, justify=tk.LEFT)
        self.status_label.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="w")

        main_frame.grid_columnconfigure(1, weight=1) # Make combobox expand

        # Define the Minecraft directory for this launcher
        default_minecraft_path = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), '.cute_advanced_minecraft_launcher')
        self.minecraft_dir = os.path.abspath(default_minecraft_path)
        os.makedirs(self.minecraft_dir, exist_ok=True)
        print(f"Purr! Minecraft directory set to: {self.minecraft_dir}")

        # Callbacks for minecraft-launcher-lib progress updates
        self.install_callbacks = {
            "setStatus": self._set_status_callback,
            "setProgress": self._set_progress_callback,
            # "setMax": self._set_max_progress_callback # Optional, if using a determinate progress bar
        }
        self.current_operation_status = "" # Stores the current operation text for progress updates

        if 'minecraft_launcher_lib' in globals(): # Check if import was successful
            self.fetch_versions_from_lib() # Fetch versions on startup
        else:
            self.status_var.set("Error: minecraft-launcher-lib not found. Please install it. Meow...")

    def _update_ui(self):
        """Forces UI update."""
        self.root.update_idletasks()

    def _set_status_callback(self, text):
        self.current_operation_status = text
        self.status_var.set(f"Status: {text}")
        self._update_ui()

    def _set_progress_callback(self, value):
        # This assumes value is an integer from 0 to 100.
        self.status_var.set(f"Status: {self.current_operation_status} (Progress: {value}%)")
        self._update_ui()

    def fetch_versions_from_lib(self):
        if 'minecraft_launcher_lib' not in globals():
            self.status_var.set("Cannot fetch versions, library missing. Meow :(")
            return
            
        self.status_var.set("Fetching version manifest, nya~...")
        self._update_ui()
        try:
            version_list = minecraft_launcher_lib.utils.get_version_list()
            versions = [v['id'] for v in version_list] # Show all types: release, snapshot, etc.
            self.version_combo['values'] = versions
            if versions:
                latest_release = minecraft_launcher_lib.utils.get_latest_version().get("release")
                if latest_release and latest_release in versions:
                    self.version_var.set(latest_release)
                elif self.version_combo['values']: # Fallback to first if latest not found
                    self.version_combo.current(0)
            self.status_var.set("Version manifest fetched! Select a version, purr.")
        except Exception as e:
            self.status_var.set(f"Error fetching manifest: {str(e)} Meow...")
        self._update_ui()

    def install_selected_version(self):
        if 'minecraft_launcher_lib' not in globals():
            self.status_var.set("Cannot install, library missing. Sad meow :(")
            return

        selected_version = self.version_var.get()
        if not selected_version:
            self.status_var.set("Nyah! Please select a version first.")
            return

        self.status_var.set(f"Preparing to install {selected_version} into {self.minecraft_dir}...")
        self._update_ui()

        try:
            minecraft_launcher_lib.install.install_minecraft_version(
                versionid=selected_version,
                minecraft_directory=self.minecraft_dir,
                callback=self.install_callbacks
            )
            self.status_var.set(f"Version {selected_version} installed successfully! Purrrrfect!")
        except minecraft_launcher_lib.exceptions.VersionNotFound:
            self.status_var.set(f"Error: Version {selected_version} not found by the library. Meow :(")
        except Exception as e:
            self.status_var.set(f"Error installing {selected_version}: {str(e)}. Aww...")
        self._update_ui()

    def launch_selected_game(self):
        if 'minecraft_launcher_lib' not in globals():
            self.status_var.set("Cannot launch, library missing. Meow :(")
            return

        selected_version = self.version_var.get()
        if not selected_version:
            self.status_var.set("Meow! Please select a version to launch.")
            return

        self.status_var.set(f"Preparing to launch {selected_version}, nya~...")
        self._update_ui()

        java_executable = shutil.which("java") or shutil.which("javaw")
        
        # Basic platform-specific Java path guessing if not in PATH
        if not java_executable and os.name == 'nt': # Windows specific search
            common_paths = [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Java"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Java"),
                os.path.join(os.environ.get("ProgramW6432", "C:\\Program Files"), "Eclipse Adoptium"), # For Adoptium JDK/JRE
                # Official launcher often bundles Java here:
                os.path.join(os.getenv('APPDATA'), '.minecraft', 'runtime'), 
                os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'Minecraft Launcher', 'runtime')
            ]
            # Look for java.exe in common JDK/JRE bin directories
            for p_path in common_paths:
                if os.path.isdir(p_path):
                    for root_dir, dirs, files in os.walk(p_path):
                        if "java.exe" in files and "bin" in root_dir.lower():
                            test_path = os.path.join(root_dir, "java.exe")
                            # Prefer javaw.exe if available in the same directory
                            javaw_test_path = os.path.join(root_dir, "javaw.exe")
                            if os.path.exists(javaw_test_path):
                                java_executable = javaw_test_path
                                break
                            java_executable = test_path
                            break
                    if java_executable:
                        break
            if java_executable:
                 print(f"Purr! Found Java at: {java_executable}")
            else:
                self.status_var.set("Java not found in PATH or common locations. Please install Java. Sad meow...")
                return
        elif not java_executable: # For non-Windows or if still not found
            self.status_var.set("Java (java/javaw) not found in PATH. Please install Java. Meow...")
            return

        options = {
            "username": f"Player{random.randint(1000, 9999)}", # Cute random player name
            "uuid": str(uuid.uuid4()),
            "token": "0",  # Placeholder for offline mode (no authentication)
            "executablePath": java_executable,
            "jvmArguments": ["-Xmx4G", "-Xms2G"], # Example: 4GB max, 2GB initial heap
            # 'gameDirectory' defaults to 'minecraft_directory' if not set, which is fine here.
        }

        try:
            minecraft_command_list = minecraft_launcher_lib.command.get_minecraft_command(
                version=selected_version,
                minecraft_directory=self.minecraft_dir,
                options=options
            )
            
            self.status_var.set(f"Launching {selected_version}... Get ready to play, purr!")
            print(f"Executing command: {' '.join(minecraft_command_list)}") # For your debugging eyes
            self._update_ui()

            creation_flags = 0
            if os.name == 'nt' and java_executable.endswith("java.exe"): # Hide console for java.exe on Windows
                creation_flags = subprocess.CREATE_NO_WINDOW # 0x08000000

            process = subprocess.Popen(minecraft_command_list, cwd=self.minecraft_dir, creationflags=creation_flags)
            self.status_var.set(f"Minecraft {selected_version} launched (PID: {process.pid}). Have fun, meow!")

        except minecraft_launcher_lib.exceptions.VersionNotFound:
            self.status_var.set(f"Launch Error: Version {selected_version} data missing. Try re-installing. Aww...")
        except FileNotFoundError:
            self.status_var.set(f"Error: Java executable '{options.get('executablePath', 'java')}' not found or invalid. Meow :(")
        except Exception as e:
            self.status_var.set(f"Error launching game: {str(e)}. Oh noes...")
        self._update_ui()

if __name__ == "__main__":
    main_root = tk.Tk()
    app = AdvancedMinecraftLauncher(main_root)
    main_root.mainloop()
