import torch
import torch.nn as nn
import torchvision.models as models
import pytorchvideo.models.resnet

if __name__=='__main__':

    model =  pytorchvideo.models.resnet.create_resnet(
        input_channel=3, 
        model_depth=3, 
        model_num_class=1, 
        norm=nn.BatchNorm3d,
        activation=nn.ReLU,
    )
    # Define the input tensor shape
    batch_size = 4
    num_channels = 3
    num_frames = 5
    height = 240
    width = 320

    # Create a random input tensor (batch, channels, frames, height, width)
    video = torch.randn(batch_size, num_channels, num_frames, height, width)

    # Initialize the VideoResNet model

    # Forward pass through the model
    outputs = model(video)

    # Display the shape of the output tensor
    print("Output shape:", outputs)
