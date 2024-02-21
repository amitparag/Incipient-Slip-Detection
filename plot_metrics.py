
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix



plt.rc('font', family='Times New Roman')

# Define legend names
legend_names = {
    '5_Frames_VVT': '5 Frames',
    '4_Frames_VVT': '4 Frames',
    '3_Frames_VVT': '3 Frames',
    '2_Frames_VVT': '2 Frames',
    '5_Frames_Resnet': 'ResNet - 5 Frames',
    '4_Frames_Resnet': 'ResNet - 4 Frames',
    '3_Frames_Resnet': 'ResNet - 3 Frames',
    '2_Frames_Resnet': 'ResNet - 2 Frames'
    # Add more legend names as needed
}

# Set custom color palette for VVT and Resnet classes
custom_palette_vvt = sns.color_palette('tab10', 4)
custom_palette_resnet = sns.color_palette('husl', 4)

# Set custom style
sns.set_style("whitegrid")

# Set font size
sns.set_context("notebook")

def save_figure(metric, models='both'):
    """
    Save the figure according to the metric name.

    Args:
    - metric (str): Name of the metric.
    - models (str): Specify which models to include. Options: 'both', 'VVT', 'Resnet'. Default is 'both'.
    """
    if not os.path.exists('./assets'):
        os.makedirs('./assets')
    plt.savefig(f'./assets/{metric}_{"_".join(models.split())}.png')


def print_training_times(losses_path):
    """
    Print the training times for each model.

    Args:
    - losses_path (str): Path to the losses.json file.
    """
    # Load losses dictionary from file
    with open(losses_path, 'r') as f:
        losses_dict = json.load(f)

    # Extract and print training times
    print("Training Times:")
    for model_name, metrics in losses_dict.items():
        training_times = metrics['Training Time']
        minutes = training_times // 60
        seconds = training_times % 60
        seconds_formatted = "{:.2f}".format(seconds)
        print(f"\t\t{model_name}\t\t: {minutes} minutes, {seconds_formatted} seconds")
    print()


def plot_metrics(losses_path, models='both'):
    """
    Plot metrics from the losses dictionary stored in the losses.json file.

    Args:
    - losses_path (str): Path to the losses.json file.
    - models (str): Specify which models to include. Options: 'both', 'VVT', 'Resnet'. Default is 'both'.
    """
    # Load losses dictionary from file
    with open(losses_path, 'r') as f:
        losses_dict = json.load(f)

    # Define the metrics to plot
    metrics_to_plot = ['Loss', 'Accuracy']

    # Determine custom palette based on models
    if models == 'both':
        custom_palette = custom_palette_vvt + custom_palette_resnet
    elif models == 'VVT':
        custom_palette = custom_palette_vvt
    elif models == 'Resnet':
        custom_palette = custom_palette_resnet

    # Iterate through each metric
    for metric in metrics_to_plot:
        plt.figure(figsize=(19.2, 10.8))  

        # Plot train, test, and validation subsets
        for i, subset in enumerate(['Train', 'Test', 'Validation'], start=1):
            plt.subplot(1, 3, i)
            if subset == 'Validation':
                plt.title(f'{subset} (Unseen Objects) ', fontsize=16)
            else:
                plt.title(f'{subset}', fontsize=16)


            
            
            plt.xlabel('Epoch', fontsize=14)
            plt.grid(True)

            # Set y-axis label only for the left subplot
            if i == 1:
                plt.ylabel(metric, fontsize=14)

            # Plot each main key's metric for the current subset
            for j, (main_key, sub_dict) in enumerate(losses_dict.items()):
                if main_key == 'Training Time':
                    continue
                # Check if the current model is included based on the 'models' parameter
                if models == 'both' or (models == 'VVT' and main_key.endswith('_VVT')) or (
                        models == 'Resnet' and main_key.endswith('_Resnet')):
                    if main_key.endswith('_VVT'):
                        palette = custom_palette_vvt
                    elif main_key.endswith('_Resnet'):
                        palette = custom_palette_resnet
                    else:
                        palette = custom_palette
                    legend_label = legend_names.get(main_key, main_key)  # Get legend name from dictionary
                    color_index = j % len(palette)  # Ensure index doesn't go out of range
                    plt.plot(sub_dict[subset][metric], label=legend_label, color=palette[color_index], alpha=0.8,
                             linewidth=2)




        plt.legend(fontsize=12)
        plt.tight_layout()
        save_figure(metric, models)

        plt.show()




def plot_precision_scores(losses_path, models='both'):
    """
    Plot metrics from the losses dictionary stored in the losses.json file.

    Args:
    - losses_path (str): Path to the losses.json file.
    - models (str): Specify which models to include. Options: 'both', 'VVT', 'Resnet'. Default is 'both'.
    """
    # Load losses dictionary from file
    with open(losses_path, 'r') as f:
        losses_dict = json.load(f)

    # Define the metrics to plot
    metrics_to_plot = ['Precision', 'Recall', 'F1-Score']

    # Determine custom palette based on models
    if models == 'both':
        custom_palette = custom_palette_vvt + custom_palette_resnet
    elif models == 'VVT':
        custom_palette = custom_palette_vvt
    elif models == 'Resnet':
        custom_palette = custom_palette_resnet

    # Iterate through each metric
    for metric in metrics_to_plot:
        plt.figure(figsize=(19.2, 10.8))  
        plt.suptitle(f'{metric}', fontsize=16)

        # Plot test and validation subsets
        for i, subset in enumerate(['Test', 'Validation'], start=1):
            plt.subplot(1, 2, i)
            if subset == 'Validation':
                plt.title(f'{subset} (Unseen Objects) ', fontsize=16)
            else:
                plt.title(f'{subset}', fontsize=16)
            plt.xlabel('Epoch', fontsize=14)
            plt.grid(True)

            # Set y-axis label only for the left subplot
            if i == 1:
                plt.ylabel(metric, fontsize=14)

            # Plot each main key's metric for the current subset
            index = 0
            for main_key, sub_dict in losses_dict.items():
                if main_key == 'Training Time':
                    continue
                # Check if the current model is included based on the 'models' parameter
                if models == 'both' or (models == 'VVT' and main_key.endswith('_VVT')) or (
                        models == 'Resnet' and main_key.endswith('_Resnet')):
                    if main_key.endswith('_VVT'):
                        palette = custom_palette_vvt
                    elif main_key.endswith('_Resnet'):
                        palette = custom_palette_resnet
                    else:
                        palette = custom_palette
                    legend_label = legend_names.get(main_key, main_key)  # Get legend name from dictionary
                    plt.plot(sub_dict[subset][metric], label=legend_label, color=palette[index], alpha=0.8,
                             linewidth=2)
                    index = (index + 1) % len(palette)

        plt.legend(fontsize=12)
        plt.tight_layout()
        save_figure(metric, models)

        plt.show()














losses_path = './trained_models/losses.json'
print_training_times(losses_path)
plot_metrics(losses_path, models='VVT')  # Specify which models to plot: 'both', 'VVT', or 'Resnet'
plot_precision_scores(losses_path, models='VVT')  # Specify which models to plot: 'both', 'VVT', or 'Resnet'
