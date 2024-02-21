# Attention-Classification

**Slip detection** with [Franka Emika](https://www.franka.de/) and [GelSight Sensors](https://www.gelsight.com/gelsightmini/).

**Author** - [Amit Parag](https://scholar.google.com/citations?user=wsRIfL4AAAAJ&hl=en)

**Instructor** - [Ekrem Misimi](https://www.sintef.no/en/all-employees/employee/ekrem.misimi/)

## Précis

The aim of the experiments is to learn the difference between slip and wriggle (and predict the onset of slip) through videos by training a Video-Vision Transformer model.

![vvt_srchitecture](./docs/architecture.jpg)

Video Vision Transformers were initially proposed in this [paper](https://arxiv.org/abs/2103.15691).

We use the first variant - spatial transformer followed by a temporal one - in our experiments.

The training dataset was collected by performing the wriggling motion.

We define "wriggle" as a sequence of motions that involve:

- **Perpendicular Shake**: This type of shake involves applying a perturbation perpendicular to the surface or direction of motion. It induces movement in a direction perpendicular to the end-effector's current orientation or path.

- **Rotation Shake**: Rotation shake applies a perturbation that causes the end-effector to rotate around its axis. This rotation can be clockwise or counterclockwise, altering the orientation of the end-effector.

- **Tangential Shake**: Tangential shake induces movement along a tangent to the end-effector's path or surface. It applies a perturbation parallel to the direction of motion, causing lateral movement without altering the orientation.

- **Vertical Shake**: Vertical shake involves applying a perturbation that induces movement along the vertical axis of the end-effector. This perturbation causes the end-effector to oscillate or move vertically, either upward or downward, relative to its current position.



Two examples are shown below:

- ![Example 1](./docs/coffee_mug.mp4)
- ![Example 2](./docs/rubicks_cube.mp4)

The occurrence of slip is usually characterized by the properties of the object in question such as its weight, elasticity, orientation of grip.

Two example of slip are shown below:

![Slip Example 1](./docs/slip.mp4)
![Slip Example 2](./docs/slow_motion.mp4)


This motion is repeated for a number of objects to gather data.

The resulting (slip) video (from one of the experiments) from the sensor attached to the gripper is shown below:

- ![Slip Video 1](./docs/slip1.mp4)
- ![Slip Video 2](./docs/slip2.mp4)

An example of wriggle is:

- ![Wriggle Example](./docs/wriggle.mp4)

After the data has been collected, we augment the data by adding noise and swapping channels in each video.

A transformed video of 5 frames would look like:

- ![Transformed Video](./docs/aug_1.avi)


## Training

For training, the data folder needs to be arranged like so:



      root_dir/
      
        ├── train/
    
         ├── slip/
      
             ├── video1.avi
      
             ├── video2.avi
      
             └── ...
       
        └── wriggle/
         
            ├── video1.avi
      
            ├── video2.avi
      
            └── ...
  
        
      ├── test/
    
         ├── slip/
      
             ├── video1.avi
      
             ├── video2.avi
      
             └── ...
       
        └── wriggle/
         
            ├── video1.avi
      
            ├── video2.avi
      
            └── ...
  
  
              
      ├── validation/
    
         ├── slip/
      
             ├── video1.avi
      
             ├── video2.avi
      
             └── ...
       
        └── wriggle/
         
            ├── video1.avi
      
            ├── video2.avi
      
            └── ...
    



## Model Architecture

- `image_size`: (240,320), # image size
- `frames`: 5, # number of frames
- `image_patch_size`: (40,40), # image patch size
- `frame_patch_size`: 5, # frame patch size
- `num_classes`: 2,
- `dim`: 8,
- `spatial_depth`: 2, # depth of the spatial transformer
- `temporal_depth`: 2, # depth of the temporal transformer
- `heads`: 2,
- `mlp_dim`: 2

Training a bigger model on 16 or 32 Gb RAM leads to the script getting automatically killed. So, if you want to try it, make sure you have access to compute clusters and adapt the code for GPU. Should be fairly straightforward. This architecture took 17.35 hours to train for 250 epochs.

## Certain problems you may face

1. **Installing real-time kernel**: See requirements below.

2. **Marker Tracking**:
    Marker tracking algorithms may fail to converge or end up computing absurd vector fields. We experimented with marker tracking but ended up not using them.

3. **Sensors**:
    The Gelsight sensors are susceptible to damage. After a few experiments, the gel pad on one of the sensors started to leak gel while the second one somehow got scrapped off. We initially started with 2 sensors but then discarded the data from one of the sensors.

4. **Low Batch Size**:
    The training script uses a batch size of 4. While it is generally preferable to have a higher batch size, restrictions due to compute capabilities still apply.

5. **Minor Convergence issues in the initial epochs**:
    Sometimes, the network gets stuck in local minima. Either restart the experiment with a different learning rate or let it run for a few more epochs. For example, in one of the experiments, the network was trapped in a local minima - the validation accuracy score remained unchanged for 100 epochs for a learning rate of 1e-3. The usual irritating local minima stuff - change some parameter slightly.

6. **OpenCV issues**:
    There are a few encoding issues with OpenCV something to do with how it compresses and encodes data.

## Requirements

See [requirements.txt]
Numpy, preferably 1.20.0. Higher versions have changed numpy.bool to bool. Might lead to clashes.

See [notes](https://github.com/amitparag/Attention-Classification/tree/main/notes) for instructions on installing real-time kernel and libfranka.

## Acknowledgements


