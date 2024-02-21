import os
import torch
import torch.nn as nn
import json

from vit_pytorch.vivit import ViT
import pytorchvideo.models.resnet
from dataset_manager import VideoDataLoader
from trainer import VideoTraining
from utils import seed_everything, check_cuda_availability, colored_print

# Wrapper to train a Video Vision Transformer model
def train_video_vision_transformer(project_name, root_dir, num_epochs=100, batch_size=16, lr=3e-4, weight_decay=0.0, device='cpu', vvt_params=None):
    # Default ViT parameters
    if vvt_params is None:
        vvt_params = {
            'image_size': (240, 320),
            'image_patch_size': (40, 40),
            'num_classes': 2,
            'dim': 8,
            'spatial_depth': 2,
            'temporal_depth': 2,
            'heads': 2,
            'mlp_dim': 8
        }

    dataset_name = project_name.split('_')[0]  
    vvt_params['frames'] = int(dataset_name[0]) 
    vvt_params['frame_patch_size'] = vvt_params['frames']

    vvt_model = ViT(**vvt_params)

    print("\n\n")

    train_loader, test_loader, val_loader = VideoDataLoader.create_loaders(os.path.join(root_dir, project_name), batch_size, num_workers=8)

    criterion = torch.nn.CrossEntropyLoss()

    vvt_optimizer = torch.optim.Adam(vvt_model.parameters(), lr=lr, weight_decay=weight_decay)

    vvt_trainer = VideoTraining(
        model=vvt_model,
        model_name='vvt',
        train_loader=train_loader,
        test_loader=test_loader,
        validation_loader=val_loader,
        num_epochs=num_epochs,
        criterion=criterion,
        optimizer=vvt_optimizer,
        device=device,
        project_name=project_name,
        weight_decay=weight_decay
    )

    # Train the model and get losses
    vvt_losses = vvt_trainer.train()
    vvt_trainer.cleanup()

    return vvt_losses

# Wrapper to train a Video Resnet model
def train_resnet(project_name, root_dir, num_epochs=100, batch_size=16, lr=3e-4, weight_decay=0.0, device='cpu'):
    model =  pytorchvideo.models.resnet.create_resnet(
        input_channel=3, 
        model_depth=50, 
        model_num_class=2,
        norm=nn.BatchNorm3d,
        activation=nn.ReLU,
    )

    print("\n\n")

    train_loader, test_loader, val_loader = VideoDataLoader.create_loaders(os.path.join(root_dir, project_name), batch_size, num_workers=8)

    criterion = torch.nn.CrossEntropyLoss()

    resnet_optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    resnet_trainer = VideoTraining(
        model=model,
        model_name='resnet',
        train_loader=train_loader,
        test_loader=test_loader,
        validation_loader=val_loader,
        num_epochs=num_epochs,
        criterion=criterion,
        optimizer=resnet_optimizer,
        device=device,
        project_name=project_name,
        weight_decay=weight_decay
    )

    # Train the model and get losses
    resnet_losses = resnet_trainer.train()
    resnet_trainer.cleanup
    return resnet_losses

# Check if the losses file exists, if not, create it
def create_losses_file(losses_file):
    directory = os.path.dirname(losses_file)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(losses_file):
        with open(losses_file, 'w') as f:
            json.dump({}, f)

if __name__ == '__main__':
    seed_everything(10000000)
    root_dir = './datasets'
    #projects = ['5_Frames', '4_Frames', '3_Frames', '2_Frames']
    projects = ['2_Frames']

    experiment_name = 'Data Collection 1'
    all_losses = {}

    for project_name in projects:
        print()
        colored_print(f"Training VVT on {project_name}", color_code=36)
        num_epochs = 75
        batch_size = 64
        lr = 4e-4
        weight_decay = 1e-4
        device = 'cpu'
        losses_file = f"./trained_models/losses.json"
        create_losses_file(losses_file)  
        vvt_losses = train_video_vision_transformer(project_name=project_name, root_dir=root_dir, num_epochs=num_epochs, batch_size=batch_size, lr=lr, weight_decay=weight_decay, device=device)
        all_losses[f"{project_name}_VVT"] = vvt_losses
        with open(losses_file, 'r') as f:
            all_experiment_losses = json.load(f)
            all_experiment_losses[f"{project_name}_VVT"] = vvt_losses
        with open(losses_file, 'w') as f:
            json.dump(all_experiment_losses, f)

        print("----------------------------------------------------------")

    """
    projects = ['5_Frames']

    for project_name in projects:
        print()
        colored_print(f"Training ResNet on {project_name}", color_code=36)
        num_epochs = 10
        batch_size = 8
        lr = 1e-3
        weight_decay = 1e-4
        device = 'cpu'
        losses_file = f"./trained_models/losses.json"
        create_losses_file(losses_file)  
        resnet_losses = train_resnet(project_name=project_name, root_dir=root_dir, num_epochs=num_epochs, batch_size=batch_size, lr=lr, weight_decay=weight_decay, device=device)
        all_losses[f"{project_name}_Resnet"] = resnet_losses
        with open(losses_file, 'r') as f:
            all_experiment_losses = json.load(f)
            all_experiment_losses[f"{project_name}_Resnet"] = resnet_losses
        with open(losses_file, 'w') as f:
            json.dump(all_experiment_losses, f)

        print("----------------------------------------------------------")
        """