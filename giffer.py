#! /usr/bin/env python

import click
import cv2
import imageio
import sys


colors = { "red": (255, 0, 0),
           "orange": (255, 165, 0),
           "yellow" : (255, 255, 0),
           "green": (0, 128, 0),
           "blue": (0, 0, 255),
           "purple" : (128, 0, 128),
           "white": (255, 255, 255),
           "black": (0, 0, 0),
           "gray": (128, 128, 128) }


font_faces = { 'complex': cv2.FONT_HERSHEY_COMPLEX,
               'complex_small': cv2.FONT_HERSHEY_COMPLEX_SMALL,
               'duplex': cv2.FONT_HERSHEY_DUPLEX,
               'plain': cv2.FONT_HERSHEY_PLAIN,
               'script_complex': cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
               'script_simplex': cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
               'simplex': cv2.FONT_HERSHEY_SIMPLEX,
               'triplex': cv2.FONT_HERSHEY_TRIPLEX }

# GIFs won't play at 24 fps (or higher). The internet says 12 to 15 fps is what
# they try to play. This fudge factor is to reduce the number of frames between
# the start and stop times. For 24 or 30 fps videos, this will reduce it to what
# GIF players can handle.
FRAME_STEP_SIZE = 2

class GifferError(Exception):
    def __init__(self, message):
        sys.tracebacklimit = 0 # Don't show traceback for this exception
        self.message = message
        super().__init__(self.message)


def get_start_and_end_frame(video_path, start_time, end_time):
    """
    Takes the cv2 video, gets the frames per second and then calculates the
    start and end frames given the start and end times

    Arguments:

        video: the path to the input video 
        start_time: float, the time where our snippet should start
        start_time: float, the time where our snippet should end
    
    Returns: (start_frame, end_frame) both ints
    """
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    start_frame = int(fps * start_time)
    end_frame = int(fps * end_time)
    return start_frame, end_frame

 
def get_output_dimensions(video_path, max_dimension):
    """
    Takes the video instance, determines the dimensions of the video,
    calculates the scaling factor to make the maximum dimension of output be
    that which was requested by the User and returns the desired dimensions.

    Arguments:
        video_path: the path to the video file
        max_dimension: int, the maximum desired horizontal or vertical dimension

    Returns: the dimension tuple used by cv2.Resize
    """
    video = cv2.VideoCapture(video_path)
    success, frame = video.read()
    if success:
        width = int(frame.shape[1])
        height = int(frame.shape[0])
        max_input_dimension = max(width, height)

        if max_dimension:
            if max_dimension > max_input_dimension:
                raise GifferError(f"Can't scale video to larger than the input dimensions")
    
            scaling_factor = max_dimension / max_input_dimension
            output_width = int(width * scaling_factor)
            output_height = int(height * scaling_factor)
            dim = (output_width, output_height)
        else:
            dim = (width, height)
        return dim
    else:
        raise GifferError(f"Unable to read the input file {video_path}")


def find_subtitle_info(subtitle, text_size, dimension, line_width=None, desired_height=None, font_face=None):
    """
    Determines the scaling factor for cv2.putText that will make the text be
    the desired height

    Arguments:
        subtitle: str, the text we want to put in the gif
        line_width: int, the width of the line used to draw the text, defaults to 2
        desired_height: int, the height we want the text to be, defaults to 15
        font_face: the cv2 font we use to write the subtitle, defaults to FONT_HERSHEY_SIMPLEX

    Returns: scale, textSize where scale is the scaling factor we will use and
    textSize is the size of the bounding box of the subtitle for the given scaling factor
    """
    scale = 10
    max_width = dimension[0]
    while 1:
        text_size, baseline = cv2.getTextSize(subtitle, font_face, scale, line_width)
        if text_size[1] > desired_height:
            scale -= 0.1
        else:
            if text_size[0] > max_width:
                raise GifferError(f"Subtitle {subtitle} won't fit in a window of size {max_width} and text height {desired_height}")
            return text_size, baseline, scale 
        if scale <= 0:
            raise ValueError(f"Invalid scale: {scale}")


def make_gif(video_path, output_file, start_frame, end_frame, dimension, duration, subtitle=None, loops=None, color=None, line_width=None, text_size=None, font_face=None):
    """
    Takes all the information collected from the command line and generates the
    gif. If a subtitle is to be genrated, it is scaled appropriately and added
    to each frame

    Arguments:
        video_path: str, the path the input video file
        output_file: str, the name of the output gif file
        start_frame: int, the frame at in the input at which the gif will start
        end_fram: int, the frame in the input at which the gif will stop
        dimension: (int, int) the dimensions of the output gif
        duration: float, the length of time from the start frame to the end frame
        subtitle: str, If added by the user, the subtitle that will be added to each frame
        loops: int, the number of loops after the first playing of the gif
        color: (int, int, int), the rgb color in which to render the subtitle
        line_width: int, the pixel width of the lines used to draw the subtitle letters
        text_size:, int, the size (in pixels) of the subtitle 
        font_face: str, the cv2 font to use when rendereing the subtitle
    """
    if subtitle:
        width, height = dimension
        bounding_box, baseline, scale = find_subtitle_info(subtitle, text_size, dimension, desired_height=text_size, line_width=line_width, font_face=font_face)

    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, start_frame - 1)
    with imageio.get_writer(output_file, mode="I", loop=loops, duration=duration) as writer:
        for i in range(start_frame, end_frame + 1, FRAME_STEP_SIZE):
            success, frame = video.read()
            if not success:
                raise GifferError(f"Unable to read frame {i} from {video_path}")

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if dimension:
                rgb_frame = cv2.resize(rgb_frame, dimension, interpolation=cv2.INTER_AREA)

            if subtitle:
                cv2.putText(
                    rgb_frame,
                    subtitle,
                    (int(width/2 - bounding_box[0]/2), height - baseline - 4),
                    font_face,
                    scale,
                    color, 
                    line_width)
            
            writer.append_data(rgb_frame)

            if FRAME_STEP_SIZE > 1:
                # Skip over the frames we're throwing away.
                for j in range(FRAME_STEP_SIZE - 1):
                    _, _ = video.read()
            


@click.command()
@click.option('--input', '-i', type=click.Path(), required=True, help="The input video file")
@click.option('--start', '-s', type=float, required=True, help="The starting time (in seconds) of the snippet")
@click.option('--end', '-e', type=float, required=True, help="The ending time (in seconds) of the snippet")
@click.option('--output', '-o', type=click.Path(exists=False), required=True, help="The name of the output file")
@click.option('--max-dimension', '-m', type=int, help="The maximum dimension of the output file")
@click.option('--loops', '-l', type=int, help="The number of loops the gif should play defaults to infinite", default=0)
@click.option('--subtitle', '-st', type=str, help="A string to add to each frame of the gif")
@click.option('--color', '-c', type=str, help="Text color (red, orange, yellow, green, blue, purple, white, black, gray). Defaults to white", default="white")
@click.option('--line-width', '-lw', type=int, help="The line width used to draw subtitle letters. Defaults to 2", default=2)
@click.option('--text-size', '-t', type=int, help="The text size in which to write the subtitle. Defaults to 15", default=15)
@click.option('--font-face', '-f', type=str, help="The cv2 hershey font face in which to write the text (complex, complex_small, duplex, plain, script_complex, script_simplex, simplex, triplex).  Defaults to simplex", default="simplex")
def giffer(input, start, end, output, max_dimension, loops, subtitle, color, line_width, text_size, font_face):
    """
    Takes a video file, extracts the frames from start to end and saves them as
    a gif. It reads the fps from the input file and uses that to determine
    where to extract the frames
    """
    start_frame, end_frame = get_start_and_end_frame(input, start, end)
    duration = end - start 
    output_dim = get_output_dimensions(input, max_dimension)

    try:
        rgb_color = colors[color.lower()]
    except KeyError:
        raise GifferError(f"Color {color} is not a supported color name")

    try:
        cv2_font_face = font_faces[font_face.lower()]
    except KeyError:
        raise GifferError(f"Font face {font_face} is not a supported font face name")
    
    make_gif(
        input,
        output,
        start_frame,
        end_frame,
        output_dim,
        duration,
        subtitle=subtitle,
        loops=loops,
        color=rgb_color,
        line_width=line_width,
        text_size=text_size,
        font_face=cv2_font_face)


if __name__ == '__main__':
    giffer()