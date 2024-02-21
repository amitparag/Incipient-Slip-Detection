

"""
__author__          ==  Amit Parag
__organization__    ==  Sintef Ocean
__date__            ==  18th January, 2024
__description__     ==  A helper script to initialize directories and manage video dataloaders

"""



from pathlib import Path
import os
import subprocess
import cv2
import numpy as np
import imageio

from utils import colored_print


def get_videos_info(directory, extensions):
    """
    Retrieve information about videos in a directory.

    Parameters:
        directory (str): The directory to search for videos.
        extensions (list): List of video file extensions to search for.

    Returns:
        list: A list of dictionaries containing information about each video found.
    """
    videos_info = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                videos_info.append({
                    'name': file,
                    'path': os.path.join(root, file),
                    'directory': root
                })

    return videos_info



def add_gaussian_noise(image, mean=0, std=15):
    noise = np.random.normal(mean, std, image.shape).astype(np.uint8)
    noisy_image = cv2.add(image, noise)
    return noisy_image




def transform(input_video_path:str, 
              output_video_path:str,
              noise_intensity:int=0.2):
    """
    Transform a video by adding noise, swapping red and blue channels,
    and horizontally flipping frames.

    Parameters:
        input_video_path (str): Path to the input video file.
        output_video_path (str): Path to save the transformed video.
        noise_intensity (int): Intensity of noise to add (default is 15).

    Returns:
        None
    """
    # Open the input video file
    cap = cv2.VideoCapture(input_video_path)

    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get video metadata
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Iterate over frames and apply transformations
    while True:
        ret, frame = cap.read()

        if not ret:
            break


        noisy_frame = add_gaussian_noise(frame, std=noise_intensity)


        # Swap red and blue channels
        swap_frame = cv2.cvtColor(noisy_frame, cv2.COLOR_BGR2RGB)

        # Horizontally flip frames
            # Flip the frame horizontally
        flipped_frame = cv2.flip(swap_frame, 1)
     



        # Write the transformed frame to the output video
        out.write(flipped_frame)

    # Release video objects
    cap.release()
    out.release()


def transform_videos(videos_info):
    """
    Transform multiple videos using the specified information.

    Parameters:
        videos_info (list): A list of dictionaries containing information about each video.

    Returns:
        None
    """
    for video in videos_info:
        name = video['name']
        path = video['path']
        dir  = video['directory']
        
        print("Processing:", path)

        # Generate the path for the transformed video
        transformed_video_path = dir + f'/aug_{name}'
        
        # Transform the video
        transform(input_video_path=path, output_video_path=transformed_video_path)

        print("=" * 40)

    print("Complete")





if __name__=='__main__':

    videos = ['./datasets/for_training/wriggle','./datasets/for_training/slip','./datasets/validation/slip','./datasets/validation/wriggle']

    for v in videos:

        videos_info = get_videos_info(v, 'avi')
        transform_videos(videos_info)
