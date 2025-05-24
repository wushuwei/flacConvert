import os
from pydub import AudioSegment
from pathvalidate import sanitize_filepath


def convert_audio_to_mp3(input_path, output_path):
    try:
        # Sanitize the file path
        sanitized_path = sanitize_filepath(input_path, replacement_text="_")

        # Use the sanitized path in the rest of your code
        audio = AudioSegment.from_file(sanitized_path)
        audio.export(output_path, format="mp3")
    except Exception as e:
        print(f"Error converting file {input_path}: {e}")

def scan_and_convert(root_folder, output_folder):
    supported_extensions = ['.flac', '.wav', '.ogg', '.m4a', '.aac', '.wma']
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(tuple(supported_extensions)):
                input_file_path = os.path.join(foldername, filename)
                relative_path = os.path.relpath(input_file_path, root_folder)
                mp3_filename = os.path.splitext(relative_path)[0] + '.mp3'
                mp3_path = os.path.join(output_folder, mp3_filename)
                os.makedirs(os.path.dirname(mp3_path), exist_ok=True)
                convert_audio_to_mp3(input_file_path, mp3_path)
