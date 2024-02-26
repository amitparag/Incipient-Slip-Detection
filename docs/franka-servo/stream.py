"""
__author__          ==  Amit Parag
__organization__    ==  Sintef Ocean
__date__            ==  18th January, 2024
__description__     ==  A helper script to initialize cameras and record videos.
"""

import os
import cv2
import gsdevice
from utils import colored_print




def record_and_save_videos(cam1_id, cam2_id, save_path='./videos/'):
    """
    Record and save videos from two GelSight cameras.

    Params:
    - cam1_id (int): Camera ID for the first camera.
    - cam2_id (int): Camera ID for the second camera.
    - save_path (str): Save path for the videos.
    """

    # Check if the specified save path is a valid folder
    assert os.path.isdir(save_path), f"\033[91mError:\033[0m '{save_path}' is not a valid folder or doesn't exist."

    
    
    # Create instances of GelSight Cameras
    dev1 = gsdevice.Camera(f"Camera 1 - ID {cam1_id}")
    dev2 = gsdevice.Camera(f"Camera 2 - ID {cam2_id}")



    # Connect to the cameras
    dev1.dev_id = cam1_id
    dev1.connect()

    dev2.dev_id = cam2_id
    dev2.connect()



    # Set up VideoWriters for saving videos
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Change the codec to MJPG



    # Construct save paths with camera names
    save_path1 = f'{save_path}camera_{dev1.dev_id}.avi'
    save_path2 = f'{save_path}camera_{dev2.dev_id}.avi'



    # Initialize VideoWriters
    out1 = cv2.VideoWriter(save_path1, fourcc, 25, (dev1.imgh, dev1.imgw), isColor=True)
    out2 = cv2.VideoWriter(save_path2, fourcc, 25, (dev2.imgh, dev2.imgw), isColor=True)



    # Display information about video saving paths
    colored_print(f"Info: Saving videos to '{save_path1}' and '{save_path2}'", "96")  # Cyan color for info



    try:
        # Create named window for displaying frames
        cv2.namedWindow('Dual Camera View')

        # Main video recording loop
        while dev1.while_condition and dev2.while_condition:
            # Get frames from both cameras
            frame1 = dev1.get_image()
            frame2 = dev2.get_image()

            # Add camera ID labels to frames
            frame1_display = cv2.putText(frame1.copy(), f'Camera {dev1.dev_id}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            frame2_display = cv2.putText(frame2.copy(), f'Camera {dev2.dev_id}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # Combine frames horizontally
            combined_frame = cv2.hconcat([frame1_display, frame2_display])

            # Display combined frame
            cv2.imshow('Dual Camera View', combined_frame)

            # Crop and resize frames
            frame1_cropped = gsdevice.resize_crop_mini(img=frame1, imgw=dev1.imgh, imgh=dev1.imgw)
            frame2_cropped = gsdevice.resize_crop_mini(img=frame2, imgw=dev2.imgh, imgh=dev2.imgw)

            # Save cropped frames to videos
            out1.write(frame1_cropped)
            out2.write(frame2_cropped)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                colored_print('Interrupted!. Writing video', "96")
                break


    except KeyboardInterrupt:
        colored_print('Interrupted!', "91")  # Red color for error


    finally:
        # Release VideoWriters and close cameras
        out1.release()
        out2.release()
        dev1.stop_video()
        dev2.stop_video()

        # Close all OpenCV windows
        cv2.destroyAllWindows()








if __name__ == "__main__":
    # Specify the camera IDs directly
    cam1_id = 0  
    cam2_id = 2  

    # Call the function to record and save videos
    record_and_save_videos(cam1_id, cam2_id, save_path='./')
