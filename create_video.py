import os
import sys
from moviepy.editor import *

from pydub import AudioSegment
from datetime import datetime

# Set the directories
images_dir = "images"
sound_dir = "sound"
output_dir = "output"

# Set the duration, crossfade time, fps, and margin
image_duration = 3
crossfade_duration = 3
fps = 24
margin = 20

# Set the video size based on the "size" parameter
if len(sys.argv) > 1:
    if sys.argv[1].lower() == "fullhd":
        video_size = (1920, 1080)
        video_size_str = "fullhd"
    elif sys.argv[1].lower() == "4k":
        video_size = (3840, 2160)
        video_size_str = "4k"
    else:
        print("Invalid size parameter. Use 'fullhd' or '4k'.")
        exit()
else:
    video_size = (1920, 1080)
    video_size_str = "fullhd"


# Create directories if they don't exist
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

if not os.path.exists(sound_dir):
    os.makedirs(sound_dir)

# Read image files from the directory
image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
image_files.sort()

if not image_files:
    print("No images found")
    exit()

# Create a list of ImageClip objects with specified duration and resize them to fit the video without upscaling
def resize_and_center(img_clip, video_size, margin):
    img_width, img_height = img_clip.size
    video_width, video_height = video_size

    scale_factor = min((video_width - 2 * margin) / img_width, (video_height - 2 * margin) / img_height)

    if scale_factor > 1:
        scale_factor = 1

    new_width, new_height = int(img_width * scale_factor), int(img_height * scale_factor)
    resized_clip = img_clip.resize((new_width, new_height))

    pos_x = (video_width - new_width) // 2
    pos_y = (video_height - new_height) // 2

    return resized_clip.set_position((pos_x, pos_y))

image_clips = [
    resize_and_center(ImageClip(os.path.join(images_dir, f)).set_duration(image_duration), video_size, margin)
    for f in image_files
]

# Create a crossfade transition between images
video_clips = []
for i in range(len(image_clips) - 1):
    video_clips.append(image_clips[i].crossfadeout(crossfade_duration))
    video_clips.append(image_clips[i + 1].crossfadein(crossfade_duration))

# Concatenate clips
concatenated_clips = concatenate_videoclips(video_clips, method="compose")

# Set fade in and fade out durations
fade_in_duration = 0
fade_out_duration = 3

# Calculate the total duration of the images
total_duration = (image_duration * len(image_clips)) + (crossfade_duration * (len(image_clips) - 1))

# Add the soundtrack if it exists
sound_files = [f for f in os.listdir(sound_dir) if f.endswith('.mp3')]
if sound_files:
    soundtrack_file = os.path.join(sound_dir, sound_files[0])

    # Convert the audio to M4A format for better compatibility
    audio = AudioSegment.from_file(soundtrack_file, format="mp3")
    audio.export("temp_audio.m4a", format="ipod")
    soundtrack = AudioFileClip("temp_audio.m4a")

    # Truncate the soundtrack to the total duration of the images
    if soundtrack.duration > total_duration:
        soundtrack = soundtrack.subclip(0, total_duration)

    # Apply fade in and fade out effects
    soundtrack = soundtrack.audio_fadein(fade_in_duration).audio_fadeout(fade_out_duration)

    final_video = concatenated_clips.set_audio(soundtrack)
else:
    final_video = concatenated_clips

# Save the video with the specified fps
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"video_gallery_{video_size_str}_{current_datetime}.mp4"

final_video.write_videofile(os.path.join(output_dir, output_file), codec="libx264", fps=fps, audio_codec="aac")

# Remove the temporary audio file
if os.path.exists("temp_audio.m4a"):
    os.remove("temp_audio.m4a")