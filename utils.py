import os
import random
import cv2
import torch
import numpy as np

def colored_print(message, color_code):
    # Utility function for printing colored text to the console
    print(f"\033[{color_code}m{message}\033[0m")


class VideoProperties:
    def __init__(self, base_folder:str, expected_values:dict):
        self.base_folder = base_folder
        self.expected_values = expected_values

    def get_video_info(self, video_path:str):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Unable to open video '{video_path}'")
            return None, None, None, None, ["Unable to open video"]

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        cap.release()

        return width, height, fps, frame_count

    def check_videos(self, folder_path):
        properties = ['Width', 'Height', 'FPS', 'Frame_Count']
        errors  = 0
        error_path = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                video_path = os.path.join(root, file)

                if file.endswith(('.avi')) and os.path.isfile(video_path):
                    colored_print(f"\nEntering {root}. Checking properties of {file}", "34")
                    info = self.get_video_info(video_path)


                    expected_values = [self.expected_values.get(f'expected_{prop.lower()}') for prop in properties]
                    actual_values = info[:4]

                    for prop, expected, actual in zip(properties, expected_values, actual_values):
                        try:
                            print(f"  - {prop}: {actual}, Expected {prop}: {expected}")
                            assert actual == expected
                        except AssertionError:
                            colored_print(f"Video: {video_path} does not satisfy the expected {prop}:", "31")
                            errors += 1
                            error_path.append(video_path)
                            continue
        
        if errors != 0:
            colored_print(f"{errors} videos do not satisfy the expected properties", "31")
            colored_print(f"Video: {path} does not satisfy the expected {prop}:", "31")
        else:
            colored_print(f"\nAll videos satisfy the expected properties.", "32")



    def check_all_videos(self):
        self.check_videos(self.base_folder)

    def write_dataset_info(self):
        # Create the ./assets/ directory outside the base_folder if it doesn't exist
        assets_directory = os.path.join(os.path.dirname(self.base_folder), 'assets')
        os.makedirs(assets_directory, exist_ok=True)

        # Create or append to the ./assets/dataset_info.md file
        output_file_path = os.path.join(assets_directory, 'dataset_info.md')
        with open(output_file_path, 'w') as file:
            # Write the directory structure in a Markdown form
            file.write("# Directory Structure\n\n")
            file.write("```\n")
            for root, dirs, files in os.walk(self.base_folder):
                level = root.replace(self.base_folder, '').count(os.sep)
                indent = ' ' * 4 * (level)
                file.write('{}{}/\n'.format(indent, os.path.basename(root)))
            file.write("```\n")

            # Call the function to count slip and wriggle videos
            total_slip_train, total_wriggle_train, total_slip_validation, total_wriggle_validation = self.count_slip_wriggle_videos()

            # Write the count of slip and wriggle videos at the bottom of the file
            file.write("\n")
            file.write("## Videos Count\n\n")
            file.write("| Category | Training | Validation |\n")
            file.write("|----------|----------|------------|\n")
            file.write(f"| Slip     | {total_slip_train}      | {total_slip_validation}        |\n")
            file.write(f"| Wriggle  | {total_wriggle_train}   | {total_wriggle_validation}        |\n")

        colored_print(f"\nDataset information with totals written to {output_file_path}\n", "32")

    def count_slip_wriggle_videos(self):
        total_slip_train = 0
        total_wriggle_train = 0
        total_slip_validation = 0
        total_wriggle_validation = 0

        for split_folder in ["training", "validation"]:
            split_path = os.path.join(self.base_folder, split_folder)

            for category_folder in ["slip", "wriggle"]:
                category_path = os.path.join(split_path, category_folder)

                for video_file in os.listdir(category_path):
                    video_path = os.path.join(category_path, video_file)

                    if video_file.endswith(('.avi', '.mp4')) and os.path.isfile(video_path):
                        info = dict(zip(['Width', 'Height', 'FPS', 'Frame_Count'], self.get_video_info(video_path)))

                        expected_values = [self.expected_values.get(f'expected_{prop.lower()}') for prop in ['Width', 'Height', 'FPS', 'Frame_Count']]
                        actual_values = [info[prop] for prop in ['Width', 'Height', 'FPS', 'Frame_Count']]

                        if all(info.values()):
                            if category_folder == "slip":
                                if split_folder == "training":
                                    total_slip_train += 1
                                elif split_folder == "validation":
                                    total_slip_validation += 1
                            elif category_folder == "wriggle":
                                if split_folder == "training":
                                    total_wriggle_train += 1
                                elif split_folder == "validation":
                                    total_wriggle_validation += 1

        return total_slip_train, total_wriggle_train, total_slip_validation, total_wriggle_validation


def check_cuda_availability():
    if torch.cuda.is_available():
        print("CUDA is available.")
        print("GPU device count:", torch.cuda.device_count())
        print("Current GPU:", torch.cuda.current_device())
        print("GPU name:", torch.cuda.get_device_name(0))
    else:
        print("CUDA is not available.")

def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True


if __name__ == '__main__':
    base_dir = "./datasets"
    expected_values_dict = {
        'expected_width': 320, 'expected_height': 240, 'expected_fps': 25, 'expected_frame_count': 7
    }

    video_properties = VideoProperties(base_dir, expected_values_dict)
    video_properties.check_all_videos()
    video_properties.write_dataset_info()
