import os
import random
import torch
import shutil  # Added import for shutil
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import Compose, ToTensor
import imageio

class MakeDatasets:

    @staticmethod
    def make_training_datasets(root_dir='./datasets'):

        source_slip_videos = os.path.join(root_dir, 'learning', 'slip')  # Modified path using os.path.join
        source_wriggle_videos = os.path.join(root_dir, 'learning', 'wriggle')  # Modified path using os.path.join

        classes = ['slip', 'wriggle']

        subsets = ['train', 'test']
        split_ratios = [0.9, 0.1]

        # Create root directory
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        # Create subsets directories and copy videos
        for subset in subsets:
            subset_dir = os.path.join(root_dir, subset)
            if not os.path.exists(subset_dir):
                os.makedirs(subset_dir)

            for class_name in classes:
                class_dir = os.path.join(subset_dir, class_name)
                if not os.path.exists(class_dir):
                    os.makedirs(class_dir)

                source_videos = source_slip_videos if class_name == 'slip' else source_wriggle_videos
                video_files = [f for f in os.listdir(source_videos) if f.endswith('.avi')]
                random.shuffle(video_files)  # Shuffle video files

                split_ratio = split_ratios[subsets.index(subset)]
                num_videos = int(len(video_files) * split_ratio)

                for video_file in video_files[:num_videos]:
                    src_path = os.path.join(source_videos, video_file)
                    dest_path = os.path.join(class_dir, video_file)
                    shutil.copy(src_path, dest_path)

        print("Directory structure and video copying completed.")

    @staticmethod
    def make_validation_datasets(root_dir):

        source_slip_videos = os.path.join(root_dir, 'unseen_data', 'slip')  # Modified path using os.path.join
        source_wriggle_videos = os.path.join(root_dir, 'unseen_data', 'wriggle')  # Modified path using os.path.join

        classes = ['slip', 'wriggle']
        subsets = ['validation']
        split_ratios = [1.0]  # Train, validation, test split ratios

        # Create root directory
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        # Create subsets directories and copy videos
        for subset in subsets:
            subset_dir = os.path.join(root_dir, subset)
            if not os.path.exists(subset_dir):
                os.makedirs(subset_dir)

            for class_name in classes:
                class_dir = os.path.join(subset_dir, class_name)
                if not os.path.exists(class_dir):
                    os.makedirs(class_dir)

                source_videos = source_slip_videos if class_name == 'slip' else source_wriggle_videos
                video_files = [f for f in os.listdir(source_videos) if f.endswith('.avi')]
                random.shuffle(video_files)  # Shuffle video files

                split_ratio = split_ratios[subsets.index(subset)]
                num_videos = int(len(video_files) * split_ratio)

                for video_file in video_files[:num_videos]:
                    src_path = os.path.join(source_videos, video_file)
                    dest_path = os.path.join(class_dir, video_file)
                    shutil.copy(src_path, dest_path)

        print("Directory structure and video copying completed.")

class VideoDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        """
        Custom dataset for loading video data.

        Args:
            data_dir (str): Path to the directory containing video data.
            transform (callable, optional): A function/transform to apply to each video frame.
        """
        self.data_dir = data_dir
        self.classes = sorted(os.listdir(data_dir))
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        self.videos = self._load_videos()
        self.transform = transform

    def _load_videos(self):
        videos = []
        for class_name in self.classes:
            class_dir = os.path.join(self.data_dir, class_name)
            for video_file in os.listdir(class_dir):
                if video_file.endswith('.avi'):
                    video_path = os.path.join(class_dir, video_file)
                    videos.append((video_path, self.class_to_idx[class_name]))
        return videos

    def __len__(self):
        return len(self.videos)

    def __getitem__(self, idx):
        video_path, label = self.videos[idx]

        video = imageio.get_reader(video_path, 'ffmpeg')

        frames = [frame[:, :, :3] for frame in video]  # Keep only the first three channels (RGB)
        video.close()

        if self.transform:
            frames = [self.transform(frame) for frame in frames]
            video_tensor = torch.stack(frames)

        return video_tensor.permute(1, 0, 2, 3), label  # Permute to (batch, channels, frames, height, width)

class VideoDataLoader:
    @staticmethod
    def create_loaders(root_dir, batch_size, num_workers=16):
        """
        Static method for creating training, testing, and validation loaders.

        Args:
            root_dir (str): Root directory containing the dataset folders.
            batch_size (int): Number of samples per batch.
            num_workers (int): Number of subprocesses to use for data loading.

        Returns:
            tuple: A tuple containing the training, testing, and validation loaders.
        """
        data_transform = Compose([
            ToTensor(),
        ])

        # Create training dataset loader
        train_data_dir = os.path.join(root_dir, 'train')
        train_dataset = VideoDataset(train_data_dir, transform=data_transform)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)

        # Create testing dataset loader
        test_data_dir = os.path.join(root_dir, 'test')
        test_dataset = VideoDataset(test_data_dir, transform=data_transform)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)

        # Create validation dataset loader
        val_data_dir = os.path.join(root_dir, 'validation')
        val_dataset = VideoDataset(val_data_dir, transform=data_transform)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)

        return train_loader, test_loader, val_loader

if __name__ == '__main__':
    root_directory = './datasets'
    batch_size = 32
    num_workers = 4

    # Create datasets
    MakeDatasets.make_training_datasets(root_directory)
    MakeDatasets.make_validation_datasets(root_directory)

    # Create loaders
    train_loader, test_loader, val_loader = VideoDataLoader.create_loaders(root_directory, batch_size, num_workers)

    # Print information about the loaders
    print("Training Loader:")
    print(f"Number of samples: {len(train_loader.dataset)}")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {len(train_loader)}")

    print("\nTesting Loader:")
    print(f"Number of samples: {len(test_loader.dataset)}")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {len(test_loader)}")

    print("\nValidation Loader:")
    print(f"Number of samples: {len(val_loader.dataset)}")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {len(val_loader)}")
