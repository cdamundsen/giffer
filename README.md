# giffer
Python code to extract a section of a video and save it as a GIF

## Motivation
We've all been there, it would be so great if to have a gif of a part of a movie, but none of the gif websites have the particular snippet that you want. That's where giffer comes in. If you have a video from which you want to extract a little bit for an animated gif, you can create the gif of your dreams.

## Usage
`giffer.py --input input_video_file.mp4 --start start_of_the_gif --end end_of_the_gif --output output_name.gif [--max-dimension largest_dimension_of_the_output]`

or

`giffer.py --help`

### Arguments
- `--input` or `-i`: the path to a video file that can be read by opencv
- `--start` or `-s`: the time (in seconds) when the gif should start
- `--end` or `-e`: the time (in seconds) when the gif should end
- `--output` or `-o`: the name of the output file (giffer will not overwrite and existing file)
- `--max-dimension` or `-m`: the maximum width or height of the output gif (in pixels). If the input file was made in landscape, this will be the width. If the input file was made in portrait mode, this will be the height

## To do
I plan to add an option to include a caption in the output gif
