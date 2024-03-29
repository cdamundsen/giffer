# giffer
Python code to extract a section of a video and save it as a GIF

## Motivation
We've all been there, it would be so great if to have a gif of a part of a movie, but none of the gif websites have the particular snippet that you want. That's where giffer comes in. If you have a video from which you want to extract a little bit for an animated gif, you can create the gif of your dreams.

## Usage
`giffer.py --input input_video_file.mp4 --start start_of_the_gif --end end_of_the_gif --output output_name.gif [--max-dimension largest_dimension_of_the_output]`

or

`giffer.py --help`

### Arguments
- `--input` or `-i`: the path to a video file that can be read by opencv.
- `--start` or `-s`: the time (in seconds) when the gif should start.
- `--end` or `-e`: the time (in seconds) when the gif should end.
- `--output` or `-o`: the name of the output file (giffer will not overwrite an existing file).
- `--max-dimension` or `-m`: optional, but highly recommended. The maximum width or height of the output gif (in pixels). If the input file was made in landscape, this will be the width. If the input file was made in portrait mode, this will be the height. If not set defaults to the size of the input file.
- `--loops`, or `-l`: optional, the number of loops of the gif that should be played. Defaults to infinite.
- `--subtitle` or `-st`: optional, a string to be added centered near the bottom of each frame of the output gif.
- `--color` or `-c`: optional, the name of the color in which to write the subtitle. Supported color names: red, orange, yellow, green, blue, purple, white, black, gray. Defaults to white.
- `--text_size` or `-t`: optional, the size of the subtitle bounding box in pixels, defaults to 15.
- `--font-face` or `-f`: optional the name of the cv2 hershey font face to use when writing the subtitle. Supported names: complex, complex_small, duplex, plain, script_complex, script_simplex, simplex, triplex).  Defaults to simplex.

## Notes
GIF players, according to the internet, like to play at 12 to 15 FPS. I've noticed that if I convert a 24 FPS video segment to a GIF, it takes roughly twice as long to play as the interval I selected from the video. So the internet appears to be correct. I've added a fudge factor that adds every other frame from the desired interval when creating the GIF. This should make it play in the appropriate time for 24 or 30 FPS input videos, at the expense of making the GIF a bit choppy.
## To do
I'd like to add the option to read the Tx3g subtitle from the input file and use that as the subtitle.
