import os
from pydub import AudioSegment
from pydub.utils import mediainfo

from .constants import SOUNDS_DIR_LOCAL


def normalise_audio(audio, target_dBFS):
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)


def processau(directory, target_dBFS=-6.0, progress_callback=None):
    file_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[-1].lower()
            
            # Skip files with '_norm' in their name
            if '_norm' in os.path.splitext(file)[0]:
                continue

            if file_extension in {".wav", ".mp3", ".flac", ".m4a", ".ogg"}:
                audio = AudioSegment.from_file(file_path, file_extension[1:])
                normalised_audio = normalise_audio(audio, target_dBFS)

                # Set the output format, sample rate, and bitrate
                output_format = "wav"
                output_sample_rate = 44100
                output_bitrate = "128k"

                # Convert the audio format, sample rate, and bitrate
                converted_audio = normalised_audio.set_frame_rate(output_sample_rate).set_channels(2)
                output_filename = os.path.splitext(file)[0] + "_norm." + output_format
                output_file_path = os.path.join(root, output_filename)

                # Export the audio
                converted_audio.export(output_file_path, format=output_format, bitrate=output_bitrate)
                print(f"Converted and normalised {file_path} to {output_file_path}")

                # Delete the original file
                os.remove(file_path)

                file_count += 1
                if progress_callback:
                    progress_callback(file_count, file)

                    progress_callback(file_count, file)


if __name__ == "__main__":
    directory = os.path.join(SOUNDS_DIR_LOCAL)
    processau(directory)
