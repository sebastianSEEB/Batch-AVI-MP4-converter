# Batch-AVI-MP4-

# Multi-Threaded Batch AVI to MP4 Converter
A clean, responsive Python GUI application built with Tkinter and FFmpeg to easily convert heavy batch `.avi` video files into widely compatible `.mp4` formats. 
This tool processes conversions via background threads so your interface never freezes, allowing up to 2 concurrent video conversions at the exact same time.

**Features**
Dual-Thread Processing: Converts multiple videos concurrently without lagging your system UI.
Native Windows Player Compatibility: Enforces a standard color layout (`-pix_fmt yuv420p`) so your output files play perfectly in Windows Media Player/Film og TV without throwing codec errors (`0x80004005`).
Clean Progress Tracking: Real-time progress bars mapping individual file statuses.
  Safety First: Gracefully handles missing background assets without crashing your active terminal.

**Prerequisites & Installation**

To run this tool, you need **Python 3** and **FFmpeg** installed on your system.

**Step 1: Install Python**
Ensure Python 3 is installed on your machine. You can download it directly from [python.org](https://www.python.org/downloads/). 
> **Windows Users:** Make sure to check the box that says **"Add Python to PATH"** during installation!

### Step 2: Install and Link FFmpeg

#### For Windows (Easiest via winget)
1. Open **Command Prompt** or **PowerShell** as an Administrator.
2. Run the following command:

   winget install --id=Gyan.FFmpeg -e

3. Restart command prompt

For Windows (Manual Fallback Setup)
If package managers fail, you must point Windows directly to your binaries:

Download the release-essentials zip from gyan.dev FFmpeg.

Extract the folder, rename it to ffmpeg, and move it to your root drive (C:\ffmpeg).

Search your Windows bar for "Edit the system environment variables" and open it.

Click Environment Variables, find the Path row under System variables, and hit Edit.

Click New and paste the direct path to your binary folder: C:\ffmpeg\bin (or your relevant version directory).

Click OK on all windows and fully restart your application environment.


**For Mac OS**
Bash
  brew install ffmpeg

**Linux**
Bash
  sudo apt update && sudo apt install ffmpeg -y


**How to run the code**
1. Clone or download the repository
2. Open a terminal inside the project
3. Launch the script via python
4.   python vidconv.py

**How to use**
1. Choose the directory where the converted videos should be saved after conversion is finished
2. Select the AVI files you wish to convert
3. After it's done, check your output folder (AVI files won't get deleted in the process)
