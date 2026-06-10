import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import threading
import os
import platform

class AviToMp4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch AVI to MP4 Converter")
        self.root.geometry("700x450")
        
        # Limit concurrent conversions to 2 at a time
        self.max_concurrent_tasks = threading.Semaphore(2)
        self.output_directory = ""
        self.ffmpeg_missing_warned = False
        
        # --- UI Setup ---
        self.header = tk.Label(root, text="FFmpeg Batch Converter", font=("Helvetica", 14, "bold"))
        self.header.pack(pady=10)

        # Output Folder Selection Frame
        self.dir_frame = tk.Frame(root)
        self.dir_frame.pack(pady=5, fill=tk.X, padx=20)
        
        self.out_btn = tk.Button(self.dir_frame, text="1. Choose Output Folder", command=self.choose_folder, width=25, bg="#e0e0e0")
        self.out_btn.pack(side=tk.LEFT, padx=5)
        
        self.out_lbl = tk.Label(self.dir_frame, text="No folder selected...", fg="gray", anchor="w")
        self.out_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # File Selection Frame
        self.file_frame = tk.Frame(root)
        self.file_frame.pack(pady=5, fill=tk.X, padx=20)

        self.select_btn = tk.Button(self.file_frame, text="2. Select AVI Files & Convert", command=self.select_files, width=25, bg="#e0e0e0")
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # Canvas and scrollbar for the queue UI
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        self.scrollbar.pack(side="right", fill="y", pady=10)

    def choose_folder(self):
        """Allows the user to select the output directory via a dedicated button."""
        folder = filedialog.askdirectory(title="Select Output Folder for MP4s")
        if folder:
            self.output_directory = folder
            self.out_lbl.config(text=self.output_directory, fg="black")

    def select_files(self):
        """Allows the user to select files, ensuring an output folder is set first."""
        if not self.output_directory:
            messagebox.showwarning("Missing Folder", "Please choose an output folder first! (Step 1)")
            return

        files = filedialog.askopenfilenames(
            title="Select AVI Videos",
            filetypes=[("AVI files", "*.avi")]
        )
        
        if not files: 
            return

        for filepath in files:
            self.add_file_to_queue(filepath)

    def add_file_to_queue(self, filepath):
        """Creates the UI elements for a single file and starts its thread."""
        filename = os.path.basename(filepath)
        out_file = os.path.join(self.output_directory, os.path.splitext(filename)[0] + ".mp4")
        
        row = tk.Frame(self.scroll_frame)
        row.pack(fill=tk.X, pady=5, padx=5)
        
        lbl = tk.Label(row, text=filename, width=30, anchor='w')
        lbl.pack(side=tk.LEFT)
        
        progress = ttk.Progressbar(row, length=200, mode='determinate')
        progress.pack(side=tk.LEFT, padx=10)
        
        action_btn = tk.Button(row, text="Queued...", width=15, state=tk.DISABLED)
        action_btn.pack(side=tk.LEFT)
        
        thread = threading.Thread(
            target=self.process_conversion, 
            args=(filepath, out_file, progress, action_btn), 
            daemon=True
        )
        thread.start()

    def get_video_duration(self, filepath):
        """Uses ffprobe to get the total length of the video."""
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', filepath
        ]
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            output = subprocess.check_output(cmd, text=True, creationflags=creationflags)
            return float(output.strip())
        except FileNotFoundError:
            return -1.0 
        except Exception:
            return 1.0  

    def process_conversion(self, in_file, out_file, progress_bar, action_btn):
        with self.max_concurrent_tasks:
            self.root.after(0, lambda: action_btn.config(text="Converting..."))
            
            duration = self.get_video_duration(in_file)
            
            if duration == -1.0:
                self.root.after(0, lambda: self.show_ffmpeg_error(action_btn))
                return

            # Forced yuv420p layout ensures native Windows player compatibility
            cmd = [
                'ffmpeg', '-i', in_file, 
                '-c:v', 'libx264', 
                '-pix_fmt', 'yuv420p', 
                '-c:a', 'aac', 
                '-progress', 'pipe:1', '-y', out_file
            ]
            
            creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            
            try:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True,
                    creationflags=creationflags
                )
                
                for line in process.stdout:
                    if "out_time_us=" in line:
                        us_str = line.split("=")[1].strip()
                        try:
                            us = int(us_str)
                            current_sec = us / 1000000.0
                            pct = min(100, (current_sec / duration) * 100)
                            self.root.after(0, lambda p=pct: progress_bar.config(value=p))
                        except ValueError:
                            pass
                
                process.wait()
                
                # Double check that the process completed cleanly and output file exists
                if process.returncode == 0 and os.path.exists(out_file):
                    self.root.after(0, self.finish_ui, progress_bar, action_btn, out_file)
                else:
                    self.root.after(0, lambda: action_btn.config(text="Error occurred", fg="red"))
                
            except FileNotFoundError:
                self.root.after(0, lambda: self.show_ffmpeg_error(action_btn))

    def show_ffmpeg_error(self, btn):
        """Updates the UI if FFmpeg is not installed properly."""
        btn.config(text="FFmpeg Missing!", fg="red", state=tk.DISABLED)
        if not self.ffmpeg_missing_warned:
            self.ffmpeg_missing_warned = True
            messagebox.showerror(
                "FFmpeg Not Found", 
                "The system cannot find 'ffmpeg'.\n\n"
                "Please ensure FFmpeg is installed and added to your Windows PATH environment variable."
            )

    def finish_ui(self, progress_bar, btn, out_file):
        progress_bar['value'] = 100
        btn.config(
            text="Open MP4", 
            state=tk.NORMAL, 
            command=lambda: self.open_file(out_file),
            fg="green"
        )

    def open_file(self, filepath):
        """Opens the finished video natively on the OS."""
        if platform.system() == 'Windows':
            os.startfile(filepath)
        elif platform.system() == 'Darwin':
            subprocess.call(('open', filepath))
        else:
            subprocess.call(('xdg-open', filepath))

if __name__ == "__main__":
    root = tk.Tk()
    app = AviToMp4Converter(root)
    root.mainloop()
