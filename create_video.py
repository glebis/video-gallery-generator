import os
import sys
import argparse
from moviepy.editor import *
from moviepy.video.VideoClip import TextClip
from PIL import ImageFont

from pydub import AudioSegment
from datetime import datetime


# Create the argument parser
parser = argparse.ArgumentParser(description="Create a video gallery from a folder of images and an optional soundtrack.")

# Define arguments and their properties
args_list = [
    {"short": "-s", "long": "--size", "choices": ["fullhd", "4k", "instastory"], "default": "fullhd", "help": "Choose the video size: fullhd, 4k, or instastory."},
    {"short": "-d", "long": "--duration", "type": float, "default": 3, "help": "Set the duration of each image in seconds."},
    {"short": "-c", "long": "--crossfade", "type": float, "default": 3, "help": "Set the crossfade duration between images in seconds."},
    {"short": "-f", "long": "--fps", "type": int, "default": 24, "help": "Set the frames per second for the video."},
    {"short": "-m", "long": "--margin", "type": int, "default": 20, "help": "Set the margin for the images in pixels."},
    {"short": "-b", "long": "--background", "default": "black", "help": "Set the background color for the video."},
    {"short": "-mc", "long": "--margin_color", "type": tuple, "default": (0,0,0), "help": "Set the margin color for the images."},
    {"short": "-t", "long": "--title_duration", "type": float, "default": 3, "help": "Set the duration of the title in seconds."},
    {"short": "-tf", "long": "--title_font", "default": "Arial", "help": "Set the font for the title."},
    {"short": "-ts", "long": "--title_font_size", "type": int, "default": 36, "help": "Set the font size for the title."},
    {"short": "-tw", "long": "--title_font_weight", "default": "normal", "choices": ["normal", "bold"], "help": "Set the font weight for the title."},
    {"short": "-tt", "long": "--title_file", "default": "titles.txt", "help": "Set the path to a file containing the title text."},
    {"short": "-tc", "long": "--title_color", "default": "white", "type": str,  "help": "Set the color for the subtitles."},
    {"short": "-ff", "long": "--title_font_file", "default": None, "help": "Set the path to a TTF file for the title font."},

]



# Add arguments to the parser
for arg in args_list:
    kwargs = {k: v for k, v in arg.items() if k not in ["short", "long"]}
    if "short" in arg:
        parser.add_argument(arg["short"], arg["long"], **kwargs)
    else:
        parser.add_argument(arg["long"], **kwargs)

# Parse arguments
args = parser.parse_args()

# Set the video size based on the "size" parameter
size_options = {
    "fullhd": (1920, 1080),
    "4k": (3840, 2160),
    "instastory": (1080, 1920),
}

video_size = size_options[args.size]
video_size_str = args.size
title_file = args.title_file
title_color = args.title_color
title_font = args.title_font
title_font_weight = args.title_font_weight

# Set the duration, crossfade time, fps, and margin
image_duration = args.duration
crossfade_duration = args.crossfade
fps = args.fps
margin = args.margin

# Set the background and margin color
background_color = args.background
margin_color = args.margin_color


# Set the directories
images_dir = "images"
sound_dir = "sound"
output_dir = "output"

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

title_text = {}
# Read title texts from file if it exists
if os.path.exists(title_file):
    with open(title_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            if len(parts) != 2:
                continue
            filename, title = parts
            title_text[filename] = title



def create_title_clip(title_text, font=title_font, font_size=48, font_weight=title_font_weight, duration=10, video_size=video_size, font_file=None):
    if font_file is not None:
        font = font_file

    text_clip = TextClip(title_text, fontsize=font_size, font=font, color=title_color)
    text_clip = text_clip.set_duration(duration)
    if font_weight == "bold":
        text_clip = text_clip.set_bold(True)

    # Set the position of the text clip to the right-bottom corner of the video
    # text_clip = text_clip.set_position((video_size[0]-((text_clip.w)/2), video_size[1]))
    #print(text_clip.w)
    # text_clip = text_clip.set_position(("right", "bottom"))

    text_clip = text_clip.set_start(max(0, text_clip.start - 16))


    return text_clip


# Create a list of ImageClip objects with specified duration and resize them to fit the video without upscaling
def resize_and_center(img_clip, video_size, margin, title_text=""):
    img_width, img_height = img_clip.size
    video_width, video_height = video_size


    scale_factor = min((video_width - 2 * margin) / img_width, (video_height - 2 * margin) / img_height)

    if scale_factor > 1:
        scale_factor = 1

    new_width, new_height = int(img_width * scale_factor), int(img_height * scale_factor)
    resized_clip = img_clip.resize((new_width, new_height))

    pos_x = (video_width - new_width) // 2
    pos_y = (new_height - (margin*3)) 
    # print(video_height)
    # print(new_height)

    if title_text:
        title_clip = create_title_clip(title_text, args.title_font, args.title_font_size, args.title_font_weight, args.title_duration, video_size, font_file=args.title_font_file)
        # title_clip = title_clip.set_pos((pos_x + margin, pos_y + margin))
        title_clip = title_clip.set_position(("center", pos_y))

        fade_in_duration = 0
        fade_out_duration = 2
        title_clip = title_clip.fadein(fade_in_duration).fadeout(fade_out_duration)



        return CompositeVideoClip([resized_clip, title_clip])
    else:
        return resized_clip.set_position((pos_x, pos_y)).margin(margin, color=margin_color)


# Create a crossfade transition between images
video_clips = []
for i in range(len(image_files) - 1):
    img_clip = ImageClip(os.path.join(images_dir, image_files[i])).set_duration(image_duration)
    next_img_clip = ImageClip(os.path.join(images_dir, image_files[i+1])).set_duration(image_duration)

    img_clip = resize_and_center(img_clip, video_size, margin, title_text=title_text.get(image_files[i], ""))
    next_img_clip = resize_and_center(next_img_clip, video_size, margin)

    video_clips.append(img_clip.crossfadeout(crossfade_duration))
    video_clips.append(next_img_clip.crossfadein(crossfade_duration))

# Add the last image to the video
last_img_clip = ImageClip(os.path.join(images_dir, image_files[-1])).set_duration(image_duration)
last_img_clip = resize_and_center(last_img_clip, video_size, margin, title_text=title_text.get(image_files[-1], ""))
video_clips.append(last_img_clip)

# Concatenate clips
concatenated_clips = concatenate_videoclips(video_clips, method="compose")

# Set fade in and fade out durations
fade_in_duration = 0
fade_out_duration = 3

# Calculate the total duration of the images
total_duration = (image_duration * len(image_files)) + (crossfade_duration * (len(image_files) - 1))

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
    

