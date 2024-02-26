"""
__author__          ==  Amit Parag
__organization__    ==  Sintef Ocean
__date__            ==  18th January, 2024
__description__     ==  A helper script to initialize directories.
"""

from pathlib import Path
import os
import subprocess
import cv2




def colored_print(message, color_code):
    print(f"\033[{color_code}m{message}\033[0m")





def get_video_info(video_path):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Unable to open video '{video_path}'")
        return None, None
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    cap.release()
    
    return width, height, fps





def get_camera_count():
    try:
        # Run v4l2-ctl to get the number of connected cameras
        result = subprocess.run("v4l2-ctl --list-devices", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        devices = result.stdout.split('\n')
        camera_count = sum("video" in device for device in devices)
        return camera_count
    except subprocess.CalledProcessError as e:
        # Handle errors (e.g., v4l2-ctl not installed)
        error_message = f"Error: {e.stderr}\n----------------------"
        colored_print(error_message, "31")  # Print error message in red
        return 0





def get_camera_info():
    # Get the number of connected cameras
    num_cameras = get_camera_count()

    if num_cameras == 0:
        colored_print("No cameras found.", "31")  # Print error message in red
        return

    # Create the 'assets' folder if it doesn't exist
    assets_folder = 'assets'
    os.makedirs(assets_folder, exist_ok=True)

    camera_info = []

    # Iterate through the number of connected cameras
    for camera_index in range(num_cameras):
        command = f"v4l2-ctl --device=/dev/video{camera_index} --list-formats-ext"

        try:
            # Run the v4l2-ctl command and capture the output
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

            # Append camera information to the list
            camera_info.append(f"Camera {camera_index + 1}:\n{result.stdout}\n----------------------")
        except subprocess.CalledProcessError as e:
            # Handle errors (e.g., if the camera doesn't exist)
            error_message = f"Error: {e.stderr}\n----------------------"
            camera_info.append(f"Camera {camera_index + 1}:\n{error_message}")
            colored_print(error_message, "31")  # Print error message in red

    file_path = os.path.join(assets_folder, 'camera_info.md')
    with open(file_path, 'w') as file:
        file.write('\n'.join(camera_info))  # Write camera information to the file

    # Print success message in green
    success_message = f"Camera information written to {file_path}"
    colored_print(success_message, "32")


    # Print success message in green
    success_message = f"Camera information written to {file_path}"
    colored_print(success_message, "32")






def check_videos_info(folder_path):
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    video_files = [f for f in os.listdir(folder_path) if f.endswith('.avi') or f.endswith('.mp4')]

    if not video_files:
        print(f"No video files found in '{folder_path}'.")
        return
    
    print("Video Information:")
    print("------------------")

    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)
        width, height, fps = get_video_info(video_path)

        if width is not None and height is not None and fps is not None:
            print(f"File: {video_path}")
            print(f"Resolution: {width}x{height}")
            print(f"FPS: {fps}\n")






def check_videos_recursive(folder_path):
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    print("Video Information:")
    print("------------------")

    video_info_dict = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.avi') or file.endswith('.mp4'):
                video_path = os.path.join(root, file)
                width, height, fps = get_video_info(video_path)

                if width is not None and height is not None and fps is not None:
                    video_info_dict[video_path] = {'width': width, 'height': height, 'fps': fps}

    check_resolution = len(set(info['width'] for info in video_info_dict.values())) > 1 or len(set(info['height'] for info in video_info_dict.values())) > 1
    check_fps = len(set(info['fps'] for info in video_info_dict.values())) > 1

    if check_resolution or check_fps:
        print("Some videos have different resolutions or fps.")
        for video_path, info in video_info_dict.items():
            print(f"\nFile: {video_path}")
            if check_resolution:
                print(f"Resolution: {info['width']}x{info['height']}")
            if check_fps:
                print(f"FPS: {info['fps']}")
    else:
        print("All videos have the same resolution and fps.")






class DatasetManager:


    @staticmethod
    def create_dataset_directories(object_name: str, exp_number: int, base_dir: str = './datasets/'):
        """
        Create dataset directories based on parameters.

        Args:
        - base_dir (str): The base directory for the dataset.
        - object_name (str): The name of the object (e.g., apple, salmon, etc.).
        - exp_number (int): The experiment number.

        Directory structure:
        - ./datasets/{object_name}/exp_num_{exp_number}/
        """

        # Build the path for the dataset
        save_path = f'./datasets/{object_name}/exp_num_{exp_number}/'

        # Check if the directory already exists
        if Path(save_path).is_dir():
            print(f"\033[1;33;40mWarning:\033[0m Directories '{save_path}' already exist.")
        else:
            # Create the directory if it doesn't exist
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            print(f"\033[1;32;40mSuccess:\033[0m Created dataset directories at '{save_path}'\n")



    @staticmethod
    def get_dataset_path(object_name: str, exp_number: int, base_dir: str = './datasets/'):
        """
        Get the dataset path based on parameters.

        Args:
        - base_dir (str): The base directory for the dataset (default is './datasets/').
        - object_name (str): The name of the object (e.g., apple, salmon, etc.).
        - exp_number (int): The experiment number.

        Returns:
        - str: The dataset path.
        """

        # Get the path for the dataset
        save_path = f'./datasets/{object_name}/exp_num_{exp_number}/'

        if Path(save_path).is_dir():
            return save_path

        else:
            # Create the directory if it doesn't exist
            print(f"\033[1;33;40mWarning:\033[0m Directories '{save_path}' does not exist.")
            return







if __name__ == "__main__":

    
    # Specify the parameters for dataset creation
    base_dir = './datasets/'
    object_name = 'apple'
    experiment_number = 1


    # Instantiate the DatasetManager class for creation of data directories. The default base dir is './datasets'
    dataset_manager = DatasetManager()




    # Create dataset directories
    dataset_manager.create_dataset_directories(object_name, experiment_number, base_dir)




    # Get dataset path
    dataset_path = dataset_manager.get_dataset_path(object_name, experiment_number, base_dir)
    print(f"\033[1;36;40mInfo:\033[0m The dataset path is '{dataset_path}'")





    folder_path = "./"  
    check_videos_info(folder_path)
    check_videos_recursive(folder_path)

    get_camera_info()