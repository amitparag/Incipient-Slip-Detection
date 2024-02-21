import torch
import time
import torch.nn as nn
from vit_pytorch.vivit import ViT
import pytorchvideo.models.resnet

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def measure_inference_time(model, input_size):
    input_tensor = torch.randn(*input_size)
    model.eval()
    with torch.no_grad():
        start_time = time.time()
        output = model(input_tensor)
        end_time = time.time()
        inference_time = end_time - start_time
    return inference_time

# Define ViT parameters
vivit_params = {
    'image_size': (240, 320),
    'image_patch_size': (40, 40),
    'num_classes': 2,
    'dim': 8,
    'spatial_depth': 2,
    'temporal_depth': 2,
    'heads': 2,
    'mlp_dim': 8
}

vivit_params['frames'] = 5
vivit_params['frame_patch_size'] = 5

# Create ViT model
vivit_model = ViT(**vivit_params)

# Create ResNet model
resnet_model =  pytorchvideo.models.resnet.create_resnet(
    input_channel=3, 
    model_depth=50, 
    model_num_class=2,
    norm=nn.BatchNorm3d,
    activation=nn.ReLU)

# Print number of learnable parameters and inference time for ViT model
vivit_num_params = count_parameters(vivit_model)
vivit_input_size = (1, 3, 5, 240, 320)  # (batch_size, num_channels, num_frames, height, width)
vivit_inference_time = measure_inference_time(vivit_model, vivit_input_size)
print("ViT - Number of learnable parameters:", vivit_num_params)
# Calculate inference rate in Hertz for ViT model
vivit_inference_rate = 1 / vivit_inference_time
print("ViT - Inference rate:", vivit_inference_rate, "Hertz")

# Print number of learnable parameters and inference time for ResNet model
resnet_num_params = count_parameters(resnet_model)
resnet_input_size = (1, 3, 5, 240, 320)  # (batch_size, num_channels, num_frames, height, width)
resnet_inference_time = measure_inference_time(resnet_model, resnet_input_size)
print("ResNet - Number of learnable parameters:", resnet_num_params)
resnet_inference_rate = 1 / resnet_inference_time
print("ResNet - Inference rate:", resnet_inference_rate, "Hertz")