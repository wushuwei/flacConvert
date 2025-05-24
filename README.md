# flacConvert
usage:  & C:/Users/wushu/miniconda3/python.exe c:/Users/wushu/Src/Jupyter/flacHelper.py

## Environment Setup

Python 3 is required for this project.

### Python Dependencies
Core Python dependencies can be installed using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```
The core dependencies are:
* `pathvalidate`
* `pydub`

### External Dependencies
**ffmpeg** is a crucial external dependency that must be installed separately. 
You can download it from the [official ffmpeg download page](https://ffmpeg.org/download.html). 
Alternatively, you can install it via package managers:
*   **Debian/Ubuntu:** `sudo apt-get install ffmpeg`
*   **macOS (using Homebrew):** `brew install ffmpeg`

### GUI Requirements (gui.py)
For the graphical user interface (`gui.py`), **Tkinter** is required. Tkinter is often included with Python standard installations. However, on some Linux distributions, it might require separate installation. For example, on Debian/Ubuntu:
```bash
sudo apt-get install python3-tk
```

**Note on Headless Environments:**
If you intend to run GUI applications in a headless environment (e.g., on a server or during automated testing without a display), a virtual framebuffer like `Xvfb` might be needed. In such cases, commands might need to be prefixed with `xvfb-run`. For example:
```bash
xvfb-run python gui.py
```

## Running the Converter

The primary way to use the converter is through the graphical user interface (GUI).

To run the GUI, use the following command in your terminal:
```bash
python gui.py
```

### GUI Operations
The GUI provides a simple interface for converting your audio files:
-   **Browse for Source Folder:** Click the "Browse" button next to "Source Folder" to select the directory containing the audio files you want to convert.
-   **Browse for Target Folder:** Click the "Browse" button next to "Target Folder" to choose where the converted MP3 files will be saved. 
    -   If you do not select a target folder, a new folder named `[source_folder_name]_mp3` (e.g., if your source folder is `MyMusic`, it will create `MyMusic_mp3`) will be automatically created within the same directory as your source folder. The converted files will then be saved into this automatically generated folder.
-   **Start Conversion:** Once you have selected the source folder (and optionally, the target folder), click the "Start Conversion" button to begin the conversion process.
-   **Status Updates:** A status bar or label within the GUI will display the progress of the conversion and indicate when the process is complete.

The underlying audio conversion logic is handled by `flacHelper.py`, which is capable of processing FLAC, WAV, OGG, and M4A audio file formats.

## Running Unit Tests

The project includes a suite of unit tests to verify its functionality. These tests ensure that the core conversion logic, user interface interactions (where applicable), and various operational scenarios perform as expected.

To run the tests, use the `test_runner.py` script from the root of the project:
```bash
python test_runner.py
```

### Prerequisites for Running Tests
Before running the tests, please ensure the following conditions are met:
-   **Python Dependencies:** All dependencies listed in `requirements.txt` must be installed. You can install them using:
    ```bash
    pip install -r requirements.txt
    ```
-   **ffmpeg:** `ffmpeg` must be installed and accessible in your system's PATH. Some tests rely on `ffmpeg` to validate the integrity of converted MP3 files.
-   **Test Assets:** The `test_assets` directory must be present in the root of the project. This directory should contain dummy audio files (e.g., `dummy.flac`, `dummy.m4a`, `dummy.ogg`, `dummy.wav`) that are used by the tests to perform conversion operations.

### Test Coverage
The unit tests cover several aspects of the application, including:
-   **GUI Interactions:** Basic GUI operations are tested if `tkinter` is available and the environment is not headless (or `Xvfb` is used).
-   **Audio Conversion:** Conversion processes for all supported formats (FLAC, WAV, OGG, M4A) to MP3.
-   **Folder Handling:** Correct processing of nested source folders and the creation of appropriate target folder structures.
-   **Edge Cases:** Scenarios such as attempting to convert files in an empty source folder or a folder containing no audio files.

## Adding Screenshots (Optional)

While this README currently does not include screenshots, they can be very helpful for users to quickly understand the application's interface and workflow. If you are contributing to the documentation or wish to visualize the application, consider adding screenshots for the following areas:

*   **Main GUI Window:** A screenshot of the main application window (`gui.py`) showing the 'Source Folder' and 'Target Folder' input fields, the 'Browse' buttons, and the 'Start Conversion' button.
    *   `[Image: Main GUI Window]`
*   **Folder Selection:** A screenshot depicting the folder selection dialog when clicking a 'Browse' button.
    *   `[Image: Folder Selection Dialog]`
*   **Conversion Progress/Completion:** A screenshot showing the GUI during a conversion (e.g., progress bar if available) or after a successful conversion, highlighting the status message.
    *   `[Image: Conversion Progress/Completion Status]`
*   **Example File Structure:** A screenshot showing an example directory structure before conversion (e.g., a source folder with FLAC files) and after conversion (e.g., the target folder with corresponding MP3 files and preserved subdirectories).
    *   `[Image: Example File Structure Before and After Conversion]`
