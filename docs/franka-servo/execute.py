"""
__author__          ==  Amit Parag
__organization__    ==  Sintef Ocean
__date__            ==  18th January, 2024
__description__     ==  A helper script to initialize cameras and record videos. This script generates datasets.
                        There is no preprocessing done here. The image is downscaled, since the default resolution is 4k,
                        which leads to huge video files.
                        Use v4l2-ctl --list-devices in the shell to get stream IDs.
                        v4l2-ctl -d /dev/video3 --list-formats-ext to get fps and resolution.

                        An important point to note here is that opencv compresses the video in a peculiar way. For instance, 
                        if you use your mobile phone clock to record the duration of wriggle, you will get something like 37 seconds.
                        Opencv will compress 37s worth of movement into a movie where the movement only occurs for 10~13 seconds and 
                        the rest of the video is just the camera collecting images even after the robot has stopped moving.

                        Therefore the capture duration should be set to 15 seconds.
                        I'm guessing this is happening because of some internal clock or compression.
                        That will capture the video of the movement. Or, we can stop capture when the 'q' key is pressed. 
                        In this script, we are stopping capture when the key is pressed.
"""

import os
import subprocess
import sys
import time

import cv2

from stream import record_and_save_videos
from utils import DatasetManager
from utils import colored_print






def execute_robotic_motion(exp_number: int, object_name: str, motion: str = 'wriggle', base_dir: str = './datasets', cam1_id: int = 3, cam2_id: int = 4):
    """
    Execute robotic motion and record videos.

    Parameters:
    - exp_number (int): The experiment number.
    - object_name (str): The name of the object.
    - motion (str): The type of robotic motion to perform (default is 'wriggle', the other is 'drop'. See drop.sh for more details).
    - base_dir (str): The base directory for saving datasets (default is './datasets').
    - cam1_id (int): Camera ID for the first camera (default is 3).
    - cam2_id (int): Camera ID for the second camera (default is 4).
    """

    dataset_manager = DatasetManager()

    # Create dataset directories
    dataset_manager.create_dataset_directories(object_name, exp_number, base_dir)

    # Get the dataset path
    dataset_path = dataset_manager.get_dataset_path(object_name, exp_number, base_dir)

    ## Execute the motion
    if motion == 'drop':
        colored_print("Executing drop after wriggle ...", "94")  # Blue color for info
        subprocess.call("./lift_drop_at_top.sh &", shell=True)
    elif motion == 'wriggle':
        colored_print("Execute wriggle ...", "94")  # Blue color for info
        subprocess.call("./wriggle.sh &", shell=True)
    else:
        colored_print("You have most probably misspelled the motion", "91")  # Red color for error
        colored_print("The motions are \n lift \n perp_shake \n vert_shake \n tan_shake \n rot_shake \n", "91")

    # Call the function to record and save videos
    record_and_save_videos(cam1_id=cam1_id, cam2_id=cam2_id,save_path=dataset_path)





def homing():
    colored_print("\nGripper homing. \nMake sure that homing is enabled in the corresponding shell file\n", "94")  # Blue color for info
    subprocess.call("./homing.sh &", shell=True)
    sys.exit(1)




def open_gripper():
    colored_print("\nGripper Opening. \n", "94")  # Blue color for info
    subprocess.call("./open_gripper.sh &", shell=True)
    sys.exit(1)





if __name__ == '__main__':



    base_dir    = './datasets' 


    # Specify the camera IDs directly
    cam1_id = 0  
    cam2_id = 2



    object_name = 'wire3D'
    exp_number  = 2


    # Homing. No need to save any video
    # homing()
    #open_gripper()


    execute_robotic_motion(exp_number=exp_number,object_name=object_name,motion='wriggle',base_dir=base_dir,cam1_id=cam1_id,cam2_id=cam2_id)

    # open_gripper()
