import os
from pydub import AudioSegment
from pydub.utils import mediainfo

from .constants import SOUNDS_DIR_LOCAL

def normalize_audio(audio, target_dBFS):
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)

def processau(directory, target_dBFS=-3.5, progress_callback=None, force=True):
    file_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[-1].lower()
            if file_extension in {".wav", ".mp3", ".flac", ".m4a"}:
                audio = AudioSegment.from_file(file_path, file_extension[1:])
                normalized_audio = normalize_audio(audio, target_dBFS)
                normalized_audio.export(file_path, format=file_extension[1:])
                print(f"Normalized {file_path}")

                file_count += 1
                if progress_callback:
                    progress_callback(file_count, file)

if __name__ == "__main__":
    directory = os.path.join(SOUNDS_DIR_LOCAL)
    processau(directory)
