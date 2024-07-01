import os
from pydub import AudioSegment
from pathvalidate import sanitize_filepath


def convert_flac_to_mp3(flac_path, mp3_path):
    try:
        # Sanitize the file path
        sanitized_path = sanitize_filepath(flac_path, replacement_text="_")

        # Use the sanitized path in the rest of your code
        audio = AudioSegment.from_file(sanitized_path, format="flac")
        audio.export(mp3_path, format="mp3")
    except Exception as e:
        print(f"Error converting file {flac_path}: {e}")

def scan_and_convert(root_folder, output_folder):
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.flac'):
                flac_path = os.path.join(foldername, filename)
                relative_path = os.path.relpath(flac_path, root_folder)
                mp3_path = os.path.join(output_folder, relative_path.replace('.flac', '.mp3'))
                os.makedirs(os.path.dirname(mp3_path), exist_ok=True)
                convert_flac_to_mp3(flac_path, mp3_path)

# Replace 'root_folder' and 'output_folder' with your folders
# input='G:\\otherMusic\\''
input ='G:\\otherMusic'
output = 'G:\\mp3'
scan_and_convert(input, output)
