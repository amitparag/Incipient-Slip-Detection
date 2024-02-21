

"""
__author__          ==  Amit Parag
__organization__    ==  Sintef Ocean
__date__            ==  18th January, 2024
__description__     ==  A helper script to initialize directories and manage video dataloaders

"""


import os
import cv2

class VideoBlackBorderRemover:
    """
    A class to transform videos by removing black borders.
    """

    @staticmethod
    def transform_videos_in_folder(folder_path, target_width=320, target_height=240):
        """
        Transform all videos in a folder by removing black borders.

        Parameters:
            folder_path (str): The path to the folder containing the input video files.
            target_width (int): The target width of the transformed video. Default is 320.
            target_height (int): The target height of the transformed video. Default is 240.

        Returns:
            None
        """
        processed_videos = set()  # Keep track of processed video paths

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.avi', '.mp4', '.mkv')):
                    video_path = os.path.join(root, file)
                    output_path = os.path.join(root, f"transformed_{file}")

                    # Check if the video has already been processed
                    if video_path in processed_videos:
                        print(f"Skipping already processed video: {video_path}")
                        continue

                    # Process the video
                    VideoBlackBorderRemover.remove_black_borders(input_video_path=video_path,
                                                                  output_path=output_path,
                                                                  target_width=target_width,
                                                                  target_height=target_height)

                    # Add the processed video to the set
                    processed_videos.add(video_path)

    @staticmethod
    def remove_black_borders(input_video_path, output_path, target_width=320, target_height=240):
        """
        Remove black borders from a video.

        Args:
            input_video_path (str): The path to the input video file.
            output_path (str): The path to save the transformed video.
            target_width (int): The target width of the transformed video. Default is 320.
            target_height (int): The target height of the transformed video. Default is 240.

        Returns:
            None
        """
        video = cv2.VideoCapture(input_video_path)
        
        # Check if the video file was opened successfully
        if not video.isOpened():
            print(f"Error: Could not open input video file '{input_video_path}'.")
            return

        # Get the frame dimensions
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 25.0, (target_width, target_height))

        while True:
            ret, frame = video.read()
            if not ret:
                break

            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply an adaptive threshold to detect black borders
            _, thresh = cv2.threshold(gray_frame, 1, 255, cv2.THRESH_BINARY)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check if any contours are found
            if contours:
                # Get the bounding box of the largest contour
                cnt = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(cnt)

                # Crop the frame to the bounding box
                cropped_frame = frame[y:y+h, x:x+w]

                # Resize the frame to the target width and height
                resized_frame = cv2.resize(cropped_frame, (target_width, target_height))

                # Write the resized frame to the output video
                out.write(resized_frame)
            else:
                print(f"No contours found in frame. Skipping...")

        video.release()
        out.release()
        print(f"Transformation completed for '{input_video_path}'.")


class ResolutionChecker:
    """
    A class to check the resolution of videos.

    Args:
        None

    Attributes:
        None
    """

    @staticmethod
    def check_resolution(video_path, target_width, target_height):
        """
        Checks if the resolution of a video matches the target resolution.

        Args:
            video_path (str): The path to the video file.
            target_width (int): The target width of the video.
            target_height (int): The target height of the video.

        Returns:
            bool: True if the resolution matches the target, False otherwise. None if the video file could not be opened.
        """
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None  # Video file could not be opened

        # Get the width and height of the video
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Check if the resolution matches the target
        if width == target_width and height == target_height:
            return True  # Resolution is as expected
        else:
            return False  # Resolution is different


    @staticmethod
    def check_videos_in_folder(folder_path, target_width, target_height):
        """
        Checks the resolution of all videos in a folder and its subfolders.

        Args:
            folder_path (str): The path to the folder containing the videos.
            target_width (int): The target width of the videos.
            target_height (int): The target height of the videos.

        Returns:
            None
        """
        # List all files in the folder, including subfolders
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.avi', '.mp4', '.mkv')):
                    video_path = os.path.join(root, file)
                    result = ResolutionChecker.check_resolution(video_path, target_width, target_height)
                    if result is None:
                        print(f"Error: Could not open video file: {video_path}")
                    elif result:
                        print(f"Video resolution is correct: {video_path}")
                    else:
                        print(f"Video resolution is not {target_width}x{target_height}: {video_path}")


if __name__ == "__main__":
    videos = ['./datasets/for_training/wriggle','./datasets/for_training/slip','./datasets/validation/slip','./datasets/validation/wriggle']

    for videos_path in videos:
        VideoBlackBorderRemover.transform_videos_in_folder(videos_path)


