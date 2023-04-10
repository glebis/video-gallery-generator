# Video Gallery Creator

A command-line Python script that creates a video gallery from a folder of images with an optional soundtrack. The script allows you to set various parameters such as video size, image duration, crossfade duration, frames per second, margin, and background color.

## Features

* Automatically resizes and centers images based on the video size without upscaling.
* Creates a crossfade transition between images.
* Supports different video sizes: Full HD, 4K, and Instagram Stories.
* Allows setting image margin and margin color.
* Background and margin colors can be customized.
* Can be used as a command line script with customizable parameters.

## Usage

```python create_video.py [-s SIZE] [-d DURATION] [-c CROSSFADE] [-f FPS] [-m MARGIN] [-b BACKGROUND] [--margin_color MARGIN_COLOR]```


## Arguments

* `-s, --size`: Choose the video size. Options: `fullhd`, `4k`, or `instastory`. Default: `fullhd`.
* `-d, --duration`: Set the duration of each image in seconds. Default: `3`.
* `-c, --crossfade`: Set the crossfade duration between images in seconds. Default: `3`.
* `-f, --fps`: Set the frames per second for the video. Default: `24`.
* `-m, --margin`: Set the margin for the images in pixels. Default: `20`.
* `-b, --background`: Set the background color for the video. Default: `black`.
* `--margin_color`: Set the margin color for the images. Default: `black`.

## Requirements

* Python 3.x
* moviepy
* pydub

## Installation

1. Install the required Python libraries:

```pip install moviepy pydub```


2. Clone the repository and navigate to the project folder:

```
git clone https://github.com/glebis/video-gallery-generator.git
cd video-gallery-generator
```


3. Run the script with the desired arguments:

```python create_video.py --size fullhd --duration 3 --crossfade 3 --fps 24 --margin 20 --background black --margin_color black```


## Authors

* Gleb Kalinin
* ChatGPT 4 (OpenAI)
