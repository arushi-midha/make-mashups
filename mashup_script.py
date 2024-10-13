import os
import yt_dlp
import moviepy.editor as mp
from pydub import AudioSegment
import argparse
import sys

# Function to create directories if they don't exist
def create_directories(directories):
    for folder in directories:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")

# Function to download n videos of a specific singer
def download_videos(singer_name, n_videos, video_folder):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Try best video+audio or fallback to best available
        'outtmpl': f'{video_folder}/%(title)s.%(ext)s',  # Save videos to the specified folder
        'noplaylist': True,  # Prevent downloading playlists
        'ignoreerrors': True,  # Skip errors
    }
    
    search_query = f"ytsearch{n_videos}:{singer_name}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([search_query])  # Search and download videos
            print(f"Downloaded {n_videos} videos of {singer_name}.")
        except Exception as e:
            print(f"Failed to download videos: {e}")

# Function to extract audio from downloaded videos
def extract_audio_from_videos(video_folder, audio_folder):
    video_files = [f for f in os.listdir(video_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))]

    if video_files:
        print(f"Found {len(video_files)} video files in the '{video_folder}' folder.")

        for video_file in video_files:
            video_path = os.path.join(video_folder, video_file)
            audio_file_name = os.path.splitext(video_file)[0] + ".mp3"
            audio_path = os.path.join(audio_folder, audio_file_name)

            try:
                video = mp.VideoFileClip(video_path)
                audio = video.audio
                if audio:  # Ensure the video has an audio stream
                    audio.write_audiofile(audio_path)
                    print(f"Extracted audio from {video_file} successfully!")
                else:
                    print(f"No audio stream found in {video_file}")
            except Exception as e:
                print(f"Failed to extract audio from {video_file}: {e}")
    else:
        print(f"No video files found in the '{video_folder}' folder.")

# Function to trim the audio files
def trim_audio_files(audio_folder, trimmed_audio_folder, trim_duration_ms):
    for filename in os.listdir(audio_folder):
        if filename.endswith('.mp3'):  # Add more formats if necessary
            audio = AudioSegment.from_file(os.path.join(audio_folder, filename))
            trimmed_audio = audio[:trim_duration_ms]  # Trim the first n seconds

            output_trim_path = os.path.join(trimmed_audio_folder, filename)
            trimmed_audio.export(output_trim_path, format="wav")  # Export as .wav

            print(f"Trimmed {filename} and saved to {output_trim_path}")

# Function to merge trimmed audio files
def merge_trimmed_audio(trimmed_audio_folder, output_file):
    merged_audio = AudioSegment.empty()

    # List all audio files in the trimmed_audio folder and merge them
    for filename in sorted(os.listdir(trimmed_audio_folder)):
        if filename.endswith('.wav') or filename.endswith('.mp3'):  # Adjust for your file types
            file_path = os.path.join(trimmed_audio_folder, filename)
            print(f"Adding {file_path} to the merged audio")

            # Load the audio file and append it to the merged_audio
            audio = AudioSegment.from_file(file_path)
            merged_audio += audio

    # Export the merged audio file
    merged_audio.export(output_file, format="wav")
    print(f"Merged audio saved as {output_file}")

# Main function to orchestrate the entire process
def create_singer_audio_mashup(singer_name, n_videos, trim_duration, output_file):
    video_folder = "videos"
    audio_folder = "audio"
    trimmed_audio_folder = "trimmed_audios"

    # Convert trim duration to milliseconds
    trim_duration_ms = trim_duration * 1000

    # Create necessary directories
    create_directories([video_folder, audio_folder, trimmed_audio_folder])

    # Step 1: Download videos
    download_videos(singer_name, n_videos, video_folder)

    # Step 2: Extract audio from videos
    extract_audio_from_videos(video_folder, audio_folder)

    # Step 3: Trim the audio files
    trim_audio_files(audio_folder, trimmed_audio_folder, trim_duration_ms)

    # Step 4: Merge the trimmed audio files
    merge_trimmed_audio(trimmed_audio_folder, output_file)

# Argument parsing and error handling
def main():
    parser = argparse.ArgumentParser(description="Download, convert, trim, and merge audio from YouTube videos.")
    parser.add_argument("singer_name", type=str, help="The name of the singer to search for.")
    parser.add_argument("n_videos", type=int, help="The number of videos to download.")
    parser.add_argument("trim_duration", type=int, help="Number of seconds to trim from each video's audio.")
    parser.add_argument("output_file", type=str, help="The name for the merged output audio file (e.g., 'output.wav').")

    args = parser.parse_args()

    # Input validation
    if args.n_videos <= 0:
        print("Error: Number of videos must be a positive integer greater than zero.")
        sys.exit(1)
    if args.trim_duration <= 0:
        print("Error: Trim duration must be a positive integer greater than zero.")
        sys.exit(1)
    if not args.output_file.endswith('.wav'):
        print("Error: Output file must have a .wav extension.")
        sys.exit(1)

    # Run the main mashup creation process
    try:
        create_singer_audio_mashup(args.singer_name, args.n_videos, args.trim_duration, args.output_file)
        print("Audio mashup creation completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
