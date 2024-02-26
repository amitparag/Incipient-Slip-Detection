# Camera Calibration

Below follows instructions for intrinsic and extrinsic camera calibration with VISP + FRANKA + Realsense. VISP already comes with built-in parameters for (most or all?) realsense cameras, so it is mainly the extrinsic one we have to work for.

## References

Visp PBVS with franka: https://visp-doc.inria.fr/doxygen/visp-daily/tutorial-franka-pbvs.html#franka_prereq_libfranka
Visp extrinsic calibration tutorial: https://visp-doc.inria.fr/doxygen/visp-daily/tutorial-calibration-extrinsic.html
OpenCV chessboard: https://visp-doc.inria.fr/download/calib-grid/OpenCV_Chessboard.pdf
AprilTag marker: https://visp-doc.inria.fr/download/apriltag/tag36_11_00000-120x120.pdf

## The extrinsic transform 

We want to estimate the extrinsic transform, i.e. the one that maps from the robot base frame to the current pose of the camera (T(f, c))
Since the camera is mounted on the wrist of the end effector, and we can get the transform from the base of the robot to the end effector (T(f, e)), with libfranka and forward kinematics, we actually want to find the static transform from the end effector and to the camera (T(e, c))

To do this, we will sample a bunch of different arm poses (T(f ,e)), and take pictures of an object that is easy to recognize (the OpenCV chessboard). Since the object is easy to recognize from many angles (and we already know the intrinsics of the camera), we can easily estimate the transform from the camera and to the object (T(c, o)). Finally, since we don't move the object, we also know that the transform from the robot base and to the object (T(f, o)) remains fixed (but unknown), since we don't move either through the sampling process.

This leaves us with N (=8 recommended) samples of:
- T(f, e) - varies, but known 
- T(c, o) - varies, but known 
- T(e, c) - fixed, but unknown 
- T(f, o) - fixed, but unknown 

And the equality T(f, o) = T(f, e) @ T(e, c) @ T(c, o), which holds for all samples 

Given enough samples (from sufficiently diverse poses), we can solve and find a constant T(f, o), T(e, c) that satisfies the equality (or minimizes residuals, most likely).

## Setup

We will be using provided binaries from the visp installation for this. However, the program generates a bunch of files in the current working directory, so it is nice to prepare a dedicated folder for all output.

```bash
mkdir -p $VISP_WS/calibration/franka_realsense
cd $VISP_WS/calibration/franka_realsense
```

Make sure the robot is turned on, the camera is connected, the joints are unlocked, FCI is enabled (so we can talk to it from visp), and it is currently in "Programming" mode (so we can move it around).

Print out the OpenCV chessboard and tape it to a rigid surface (like a flat piece of cardboard). It should have a 9x6 grid (if you count the inner intersections, it's 10x7 if you count the tiles).

## Capture data

Visp has a single program that will help us capture all the data we need. Run:
```bash
../../visp-build/tutorial/calibration/tutorial-franka-acquire-calib-data --ip <ROBOT-IP>
```

This should open a window that displays what the realsense camera input. Also, if you inspect the folder we just created (`$VISP_WS/calibration/franka_realsense`), you should see that the file `franka_camera.xml` now exists. It was automatically created at startup and contains camera intrinsic parameters.

Next, put the chessboard down in the middle of the robot's workspace. Use the franka pilot grip to move the robot to a pose where the entire chessboard is visible (ideally at an oblique angle), and as many corners as possible is just at the edge of the image.

Left click the display window to take a snapshot. This should save two new files to the directory.
- franka_pose_fPe_1.yml: the T(f,e) transform which was captured through libfranka
- franka_image-1.png: a snapshot from the camera taken at the same time (will be used to compute T(c, o) later)

Repeat the process N (=8) times. Make sure to move the robot pose in between. Ideally, you should try to pick poses that are uniformely distributed in a hemisphere over the chessboard.

## Estimate cPo

Next we will estimate T(c, o); the transform from the camera to the object.

```bash
../../visp-build/tutorial/calibration/tutorial-chessboard-pose --square_size 0.0262 -w 9 -h 6 --input franka_image-%d.png --intrinsic franka_camera.xml --output franka_pose_cPo_%d.yaml
```
NOTE: check that your chessboard matches this (0.0262 meters, 9 rows, 6 cols). If not, alter the arguments.

For each of the N images you captured, this should generate a cPo yaml file with the estimated T(c,o) transform.

## Estimate eMc 

Finally, we will estimate T(e, c). For this we will use the fPe transforms we captured earlier, and the cPo transforms we just estimated.

```bash
../../visp-build/tutorial/calibration/tutorial-hand-eye-calibration --data-path . --fPe franka_pose_fPe_%d.yaml --cPo franka_pose_cPo_%d.yaml --output franka_eMc.yaml
```

This should generate the file "franka_eMc.yaml", which contains the 6 floats representing the rigid trasnform from the end effector to the camera. It should also save a "franka_eMc.txt" file, which (I assume) contains the same transform as a 4x4 homogenous matrix.

The calibration program outputs some stats. Among these is a residual from the fitting process. The reference output from the VISP tutorial got:
- Mean residual rMo(8) - rotation (deg) = 0.596712
- Mean residual rMo(8) - translation (m) = 0.00114835
- Mean residual rMo(8) - global = 0.00740886

We got global residual a bit above (0.008X) the VISP tutorial the first time we tried, and a bit below (0.007X) the second time. In both cases, the camera calibration seemed to work well.

## Test 

If you want to test everything, the Franka tutorial shows how you can do PBVS with an april tag marker.
Print out the apriltag marker (put in on a rigid surface), make sure the franka is in execution mode (in Desk), and run:

```bash
../../visp-build/examples/servo-franka/servoFrankaPBVS --eMc franka_eMc.yaml --plot --adaptive_gain --task_sequencing --no-convergence-threshold"
```

This should open a window, and you can start the controller by left clicking it. The robot arm should now move to a fixed pose relative to the april tag marker. Try moving the marker, the robot should move with it (indefinitely since we set `--no-convergence-threshold`)