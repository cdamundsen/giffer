#! /usr/bin/env python

import click
import cv2
import imageio
import sys


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

        if max_dimension > max_input_dimension:
            raise GifferError(f"Can't scale video to larger than the input dimensions")

        scaling_factor = max_dimension / max_input_dimension
        output_width = int(width * scaling_factor)
        output_height = int(height * scaling_factor)
        dim = (output_width, output_height)
        return dim
    else:
        raise GifferError(f"Unable to read the input file {video_path}")


def get_frames(video_path, start_frame, end_frame, dimension):
    """
    Reads in the desired frames from the video, if the dimensions are to be
    changed, resizes the frames

    Arguments

        video_path: str, the path the video file
        start_frame: int the first frame in the snippet
        end_frame: int the last frame in the snippet
        dimension: (width, height) the desired dimension of the output, can be None
    
    Returns: a list of images are read from the video file
    """
    frames = []
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, start_frame-1)
    for i in range(start_frame, end_frame + 1):
        success, frame = video.read()
        if not success:
            raise GifferError(f"Unable to read from the video file {video_path}")
        if dimension:
            frames.append(cv2.resize(frame, dimension, interpolation = cv2.INTER_AREA))
        else:
            frames.append(frame)
    return frames


def write_gif(frames, loops, duration, output_file):
    """
    Given a list of frames read (and perhaps resized) from the input video
    file, saves them to a gif file

    Arguments:

        frames: a list of images as returned by cv2.read call
        loops: the number of times the gif should loop
        output_file: the path to the output gif file
    """
    with imageio.get_writer(output_file, mode="I", loop=loops, duration=duration) as writer:
        for frame in frames:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            writer.append_data(rgb_frame)


@click.command()
@click.option('--input', '-i', type=click.Path(), required=True, help="The input video file")
@click.option('--start', '-s', type=float, required=True, help="The starting time (in seconds) of the snippet")
@click.option('--end', '-e', type=float, required=True, help="The ending time (in seconds) of the snippet")
@click.option('--output', '-o', type=click.Path(exists=False), required=True, help="The name of the output file")
@click.option('--max-dimension', '-m', type=int, help="The maximum dimension of the output file")
@click.option('--loops', '-l', type=int, help="The number of loops the gif should play defaults to infinite", default=0)
def giffer(input, start, end, output, max_dimension, loops):
    """
    Takes a video file, extracts the frames from start to end and saves them as
    a gif. It reads the fps from the input file and uses that to determine
    where to extract the frames
    """
    start_frame, end_frame = get_start_and_end_frame(input, start, end)
    duration = end - start 
    output_dim = None
    if max_dimension:
        output_dim = get_output_dimensions(input, max_dimension)
    frames = get_frames(input, start_frame, end_frame, output_dim)
    write_gif(frames, loops, duration, output)


if __name__ == '__main__':
    giffer()