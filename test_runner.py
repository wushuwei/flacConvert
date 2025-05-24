import unittest
import os
import shutil
import sys
import subprocess

# Add the directory containing flacHelper.py and gui.py to the Python path
sys.path.append(os.getcwd())

from flacHelper import scan_and_convert, convert_audio_to_mp3

# --- TKINTER SETUP ---
# Assume xvfb-run is used, so Tkinter *should* be available for initialization.
TKINTER_AVAILABLE = True 
gui_module = None
tk_module = None
messagebox_module = None
filedialog_module = None

try:
    import tkinter as tk_module
    from tkinter import filedialog as filedialog_module, messagebox as messagebox_module
    import gui as gui_module
    print("Successfully imported tkinter and gui modules.")
except ImportError as e:
    print(f"Failed to import tkinter or gui modules: {e}. GUI tests will be impacted.")
    TKINTER_AVAILABLE = False # Fallback if import fails despite xvfb-run

class TestAudioConverter(unittest.TestCase):

    TEST_BASE_DIR = "test_app_files_valid_audio" 
    SOURCE_DIR = os.path.join(TEST_BASE_DIR, "test_source_valid")
    TARGET_DIR_EXPLICIT = os.path.join(TEST_BASE_DIR, "test_target_explicit_valid")
    DEFAULT_TARGET_DIR_NAME = os.path.basename(SOURCE_DIR) + "_mp3"
    DEFAULT_TARGET_DIR = os.path.join(os.path.dirname(SOURCE_DIR), DEFAULT_TARGET_DIR_NAME)
    ASSETS_DIR = "test_assets" 

    @classmethod
    def setUpClass(cls):
        print(f"Setting up test class. TKINTER_AVAILABLE: {TKINTER_AVAILABLE}")
        if os.path.exists(cls.TEST_BASE_DIR):
            shutil.rmtree(cls.TEST_BASE_DIR)
        os.makedirs(cls.TEST_BASE_DIR, exist_ok=True)

        os.makedirs(cls.SOURCE_DIR, exist_ok=True)
        source_subfolder = os.path.join(cls.SOURCE_DIR, "subfolder")
        os.makedirs(source_subfolder, exist_ok=True)
        os.makedirs(os.path.join(cls.SOURCE_DIR, "empty_subfolder"), exist_ok=True) 
        os.makedirs(cls.TARGET_DIR_EXPLICIT, exist_ok=True)

        asset_files = ["dummy.flac", "dummy.wav", "dummy.ogg", "dummy.m4a"]
        if not os.path.exists(cls.ASSETS_DIR):
            print(f"ERROR: Test assets directory '{cls.ASSETS_DIR}' not found.")
            raise FileNotFoundError(f"Test assets directory '{cls.ASSETS_DIR}' not found. Create it first.")

        for asset_name in asset_files:
            shutil.copy(os.path.join(cls.ASSETS_DIR, asset_name), os.path.join(cls.SOURCE_DIR, asset_name))
        
        shutil.copy(os.path.join(cls.ASSETS_DIR, "dummy.flac"), os.path.join(source_subfolder, "nested_dummy.flac"))

        with open(os.path.join(cls.SOURCE_DIR, "non_audio_file.txt"), "w") as f:
            f.write("This is a text file.")
        with open(os.path.join(cls.SOURCE_DIR, "corrupted_audio.flac"), "w") as f:
            f.write("This is intentionally not a valid FLAC file.")

        if TKINTER_AVAILABLE:
            if filedialog_module: 
                cls.original_askdirectory = filedialog_module.askdirectory
            if messagebox_module: 
                cls.original_showinfo = messagebox_module.showinfo
                cls.original_showerror = messagebox_module.showerror
        cls.mock_messages = []

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_BASE_DIR)
        if TKINTER_AVAILABLE and hasattr(cls, 'original_askdirectory') and filedialog_module:
            filedialog_module.askdirectory = cls.original_askdirectory
        if TKINTER_AVAILABLE and hasattr(cls, 'original_showinfo') and messagebox_module:
            messagebox_module.showinfo = cls.original_showinfo
        if TKINTER_AVAILABLE and hasattr(cls, 'original_showerror') and messagebox_module:
            messagebox_module.showerror = cls.original_showerror

    def setUp(self):
        self.mock_messages.clear()
        if TKINTER_AVAILABLE:
            if filedialog_module: filedialog_module.askdirectory = self._mock_askdirectory
            if messagebox_module: 
                messagebox_module.showinfo = self._mock_showinfo
                messagebox_module.showerror = self._mock_showerror
        self.mock_paths_to_return = []

        if os.path.exists(self.TARGET_DIR_EXPLICIT):
            shutil.rmtree(self.TARGET_DIR_EXPLICIT)
        os.makedirs(self.TARGET_DIR_EXPLICIT, exist_ok=True)
        
        default_target_parent = os.path.dirname(self.DEFAULT_TARGET_DIR)
        if not os.path.exists(default_target_parent):
             os.makedirs(default_target_parent)
        if os.path.exists(self.DEFAULT_TARGET_DIR):
            shutil.rmtree(self.DEFAULT_TARGET_DIR)

        if TKINTER_AVAILABLE and tk_module and gui_module:
            try:
                self.root = tk_module.Tk()
                self.app = gui_module.AudioConverterApp(self.root)
            except Exception as e:
                print(f"ERROR: tk.Tk() failed during setUp: {e}. Setting app to None.")
                self.app = None 
                self.root = None 
        else:
            self.root = None
            self.app = None

    def tearDown(self):
        if TKINTER_AVAILABLE and self.root:
            try:
                self.root.destroy()
            except: 
                pass
    
    def _check_mp3_validity(self, mp3_filepath):
        if not os.path.exists(mp3_filepath):
            return False, f"MP3 file not found: {mp3_filepath}"
        try:
            result = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", mp3_filepath, "-f", "null", "-"],
                capture_output=True, text=True, check=False 
            )
            if result.returncode == 0 and not result.stderr:
                return True, ""
            else:
                return False, f"ffmpeg validation error for {mp3_filepath}: {result.stderr}"
        except FileNotFoundError:
            return False, "ffmpeg command not found. Cannot validate MP3."
        except Exception as e:
            return False, f"Exception during MP3 validation of {mp3_filepath}: {e}"

    def _mock_askdirectory(self):
        if self.mock_paths_to_return:
            return self.mock_paths_to_return.pop(0)
        return None

    def _mock_showinfo(self, title, message):
        self.mock_messages.append(f"INFO: {title} - {message}")

    def _mock_showerror(self, title, message):
        self.mock_messages.append(f"ERROR: {title} - {message}")

    def get_last_message(self, type_filter=""):
        for msg in reversed(self.mock_messages):
            if type_filter.upper() in msg:
                return msg
        return None

    @unittest.skipUnless(TKINTER_AVAILABLE and gui_module is not None, "Skipping GUI test: tkinter/gui not fully available")
    def test_01_gui_source_target_selection(self):
        self.assertIsNotNone(self.app, "GUI App not initialized")
        print("\nRunning test_01_gui_source_target_selection...")
        self.mock_paths_to_return = [self.SOURCE_DIR]
        self.app.browse_source()
        self.assertEqual(self.app.source_folder.get(), self.SOURCE_DIR)
        self.mock_paths_to_return = [self.TARGET_DIR_EXPLICIT]
        self.app.browse_target()
        self.assertEqual(self.app.target_folder.get(), self.TARGET_DIR_EXPLICIT)
        print("test_01_gui_source_target_selection: PASSED")

    @unittest.skipUnless(TKINTER_AVAILABLE and gui_module is not None, "Skipping GUI test: tkinter/gui not fully available")
    def test_02_gui_default_target_folder(self):
        self.assertIsNotNone(self.app, "GUI App not initialized")
        print("\nRunning test_02_gui_default_target_folder...")
        self.app.source_folder.set(self.SOURCE_DIR)
        self.app.target_folder.set("") 
        self.app.start_conversion() 
        self.assertTrue(os.path.exists(self.DEFAULT_TARGET_DIR))
        self.assertEqual(self.app.target_folder.get(), self.DEFAULT_TARGET_DIR)
        expected_mp3 = os.path.join(self.DEFAULT_TARGET_DIR, "dummy.mp3")
        self.assertTrue(os.path.exists(expected_mp3))
        is_valid, msg = self._check_mp3_validity(expected_mp3)
        self.assertTrue(is_valid, f"Default target dummy.mp3 invalid: {msg}")
        self.assertIn("Conversion complete!", self.get_last_message("INFO"))
        print("test_02_gui_default_target_folder: PASSED")

    @unittest.skipUnless(TKINTER_AVAILABLE and gui_module is not None, "Skipping GUI test: tkinter/gui not fully available")
    def test_03_gui_specified_new_target_folder(self):
        self.assertIsNotNone(self.app, "GUI App not initialized")
        new_target = os.path.join(self.TEST_BASE_DIR, "test_output_new_gui")
        if os.path.exists(new_target): shutil.rmtree(new_target)

        print("\nRunning test_03_gui_specified_new_target_folder...")
        self.app.source_folder.set(self.SOURCE_DIR)
        self.app.target_folder.set(new_target)
        self.app.start_conversion()
        self.assertTrue(os.path.exists(new_target))
        expected_mp3 = os.path.join(new_target, "dummy.mp3")
        self.assertTrue(os.path.exists(expected_mp3))
        is_valid, msg = self._check_mp3_validity(expected_mp3)
        self.assertTrue(is_valid, f"Specified new target dummy.mp3 invalid: {msg}")
        self.assertIn("Conversion complete!", self.get_last_message("INFO"))
        print("test_03_gui_specified_new_target_folder: PASSED")
        if os.path.exists(new_target): shutil.rmtree(new_target)

    def test_04_conversion_variety_formats_structure_and_validity(self):
        print("\nRunning test_04_conversion_variety_formats_structure_and_validity (flacHelper direct)...")
        scan_and_convert(self.SOURCE_DIR, self.TARGET_DIR_EXPLICIT)
        
        expected_mp3_main = os.path.join(self.TARGET_DIR_EXPLICIT, "dummy.mp3")
        self.assertTrue(os.path.exists(expected_mp3_main), f"{expected_mp3_main} not found.")
        is_valid, msg = self._check_mp3_validity(expected_mp3_main)
        self.assertTrue(is_valid, f"Main dummy.mp3 invalid: {msg}")

        expected_mp3_nested = os.path.join(self.TARGET_DIR_EXPLICIT, "subfolder", "nested_dummy.mp3")
        self.assertTrue(os.path.exists(expected_mp3_nested), f"{expected_mp3_nested} not found.")
        is_valid_nested, msg_nested = self._check_mp3_validity(expected_mp3_nested)
        self.assertTrue(is_valid_nested, f"Nested dummy.mp3 invalid: {msg_nested}")
        
        self.assertFalse(os.path.exists(os.path.join(self.TARGET_DIR_EXPLICIT, "non_audio_file.mp3")))
        self.assertFalse(os.path.exists(os.path.join(self.TARGET_DIR_EXPLICIT, "corrupted_audio.mp3")))
        print("test_04_conversion_variety_formats_structure_and_validity: PASSED")

    def test_05_edge_case_empty_source_folder(self):
        print("\nRunning test_05_edge_case_empty_source_folder (flacHelper direct)...")
        empty_src = os.path.join(self.SOURCE_DIR, "empty_subfolder") 
        scan_and_convert(empty_src, self.TARGET_DIR_EXPLICIT)
        target_files = [f for f in os.listdir(self.TARGET_DIR_EXPLICIT) if os.path.isfile(os.path.join(self.TARGET_DIR_EXPLICIT, f))]
        self.assertEqual(len(target_files), 0, f"Files were created in target from an empty source: {target_files}")
        print("test_05_edge_case_empty_source_folder: PASSED")

    def test_06_edge_case_source_with_no_supported_files(self):
        print("\nRunning test_06_edge_case_source_with_no_supported_files (flacHelper direct)...")
        no_supported_src = os.path.join(self.TEST_BASE_DIR, "no_supported_src_for_test6")
        os.makedirs(no_supported_src, exist_ok=True)
        with open(os.path.join(no_supported_src, "file.txt"), "w") as f: f.write("text")
        scan_and_convert(no_supported_src, self.TARGET_DIR_EXPLICIT)
        target_files = [f for f in os.listdir(self.TARGET_DIR_EXPLICIT) if os.path.isfile(os.path.join(self.TARGET_DIR_EXPLICIT, f))]
        self.assertEqual(len(target_files), 0, f"Files were created from source with no supported audio: {target_files}")
        print("test_06_edge_case_source_with_no_supported_files: PASSED")
        shutil.rmtree(no_supported_src)

    def test_07_edge_case_corrupted_file_handling(self):
        print("\nRunning test_07_edge_case_corrupted_file_handling (flacHelper direct)...")
        old_stdout = sys.stdout 
        sys.stdout = open(os.devnull, 'w')
        scan_and_convert(self.SOURCE_DIR, self.TARGET_DIR_EXPLICIT)
        sys.stdout = old_stdout 

        expected_mp3_main = os.path.join(self.TARGET_DIR_EXPLICIT, "dummy.mp3")
        self.assertTrue(os.path.exists(expected_mp3_main))
        is_valid, msg = self._check_mp3_validity(expected_mp3_main)
        self.assertTrue(is_valid, f"dummy.mp3 (alongside corrupted) invalid: {msg}")

        expected_mp3_nested = os.path.join(self.TARGET_DIR_EXPLICIT, "subfolder", "nested_dummy.mp3")
        self.assertTrue(os.path.exists(expected_mp3_nested))
        is_valid_nested, msg_nested = self._check_mp3_validity(expected_mp3_nested)
        self.assertTrue(is_valid_nested, f"Nested dummy.mp3 (alongside corrupted) invalid: {msg_nested}")

        self.assertFalse(os.path.exists(os.path.join(self.TARGET_DIR_EXPLICIT, "corrupted_audio.mp3")))
        print("test_07_edge_case_corrupted_file_handling: PASSED")

    @unittest.skipUnless(TKINTER_AVAILABLE and gui_module is not None, "Skipping GUI test: tkinter/gui not fully available")
    def test_08_gui_feedback_elements(self):
        self.assertIsNotNone(self.app, "GUI App not initialized")
        print("\nRunning test_08_gui_feedback_elements...")
        self.assertEqual(self.app.status_label.cget("text"), "Select source and target folders to start.")
        self.assertEqual(str(self.app.start_button.cget("state")), tk_module.NORMAL)
        self.assertEqual(self.app.progress_var.get(), 0.0)

        self.app.source_folder.set(self.SOURCE_DIR)
        self.app.target_folder.set(self.TARGET_DIR_EXPLICIT)
        self.app.start_conversion() 
        self.assertIn("Conversion complete!", self.app.status_label.cget("text"))
        self.assertEqual(str(self.app.start_button.cget("state")), tk_module.NORMAL) 
        self.assertEqual(self.app.progress_var.get(), 100.0)
        
        self.app.source_folder.set("") 
        self.app.start_conversion()
        self.assertIn("Source folder selection is required.", self.app.status_label.cget("text"))
        self.assertIn("ERROR: Error - Source folder must be selected.", self.get_last_message("ERROR"))
        self.assertEqual(str(self.app.start_button.cget("state")), tk_module.NORMAL)
        print("test_08_gui_feedback_elements: PASSED")

if __name__ == '__main__':
    print("----------------------------------------------------------------------")
    print("Audio Converter Test Suite - Using Valid Dummy Audio Files")
    print(f"TKINTER_AVAILABLE (at script start): {TKINTER_AVAILABLE}")
    if TKINTER_AVAILABLE and os.environ.get('DISPLAY') is None and not os.environ.get('XVFB_RUN'): 
        print("WARNING: Tkinter may be importable, but $DISPLAY is not set and not under xvfb-run. GUI tests might fail.")
    
    print(f"Base directory for test files: {os.path.abspath(TestAudioConverter.TEST_BASE_DIR)}")
    print(f"Test assets directory expected at: {os.path.abspath(TestAudioConverter.ASSETS_DIR)}")
    print("----------------------------------------------------------------------")
    
    unittest.main(verbosity=1, exit=False)
