# Visp Setup 

Below follows instruction for building and installing visp with libfranka and intel realsense support (the way that worked for us).

## References

We more or less follow the visp docs: https://visp-doc.inria.fr/doxygen/visp-daily/tutorial-franka-pbvs.html#franka_pbvs_known_issue_activate_FCI
Librealsene: https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md

## Preparations

Set aside a folder for the installation and 3rd party binaries (we used `~/DEVEL/visp_ws`)
```bash
mkdir -p /path/to/visp_ws
cd /path/to/visp_ws
```

Also, let visp know about this path through the environment variable "$VISP_WS":
```bash
echo "export VISP_WS=$(pwd)" >> ~/.bashrc
source ~/.bashrc
```

Create a sub-directory where we will install 3rd-party libraies 
```bash
mkdir $VISP_WS/3rdparty
```


## Intel Realsense 


First we build and install the librealsense binaries. Begin by stinalling dependencies:
```bash
sudo apt-get install git libssl-dev libusb-1.0-0-dev pkg-config libgtk-3-dev cmake-curses-gui
sudo apt-get install libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev at
sudo apt install -y qtcreator qtbase5-dev qt5-qmake cmake   # It failed to compile without this too (cmake is probably redundant, though)
```

### Problem with opengl 
On one machine, we struggled a bit with OpenGL. 
- We suspect the problem is that this computer had a Xeon CPU (for servers), which does not have integrated graphics.
    - Since the realtime kernel doesn't play well with the nvidia card, this meant that we essentially had no graphics
    - That caused issues when compiling the graphical examples for librealsense, which needs opengl 
- We ended up messing around a lot, running `ubuntu-drivers autoinstall`, rebooting a bunch, and changing the settings in "additional drivers". We thought that if we could get the screen resolution up, it would fix it. We never managed to increase the resolution, but, in the end when we tried to just build again (as a last hail mary), it actually compiled.
- Sorry, we don't have a good description of how we made this work. 
    - After all the messing around, running `glxinfo -B` shows that the graphics device is now `llvmpipe`, the vendor is `Mesa/X.org`, version is `22.2.0` The command also outputs a buch of information about OpenGL, which now seems to work.
    - sudo ubuntu-drivers autoinstall should fix it. Maybe try downgrading from nvidia-proprietary and tested to nvidia-proprietary or Xorg

Clone and cd into repository
```bash
cd $VISP_VS/3rdparty
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
```

Run the permission script 
```bash
./scripts/setup_udev_rules.sh
```

Build and install ( possibly needs sudo before make -j)
```bash
mkdir build
cd build
cmake .. -DBUILD_EXAMPLES=ON -DCMAKE_BUILD_TYPE=Release
make -j <NPROC>
sudo make install
```

Connect a realsense camera and test that things are working 
```bash
./examples/capture/rs-capture
```

## Franka library 

Next we build and install the libfranka binaries. Begin by isntalling dependencies 
```bash
sudo apt install build-essential cmake git libpoco-dev libeigen3-dev
```

Clone and cd into repository 
```bash
cd $VISP_WS/3rdparty
git clone --recursive https://github.com/frankaemika/libfranka --branch 0.10.0
cd libfranka 
```
NOTE: becuase we have the FR3 robot, we need to pull the 0.10.0 branch (or newer, I think). We first used 0.9.0, which didn't end up working.

Build and install ( if it fails, delete build and run everything again with sudo cmake and make)
```bash 
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j <NPROC>
sudo make install
```

Test that things are working with e.g.
```bash
./examples/echo_robot_state <ROBOT-IP>
```
It should print out the state of the robot to the terminal. If it hangs, it could be because:
- You haven't configured network yet
- The franka is not in FCI mode (enable from menu in top right corner)
- You specified the wrong ROBOT-IP (should be the one you put in the C2 netowrk in Franka desk)

## VISP

Finally, we build and install VISP. Begin by installing dependencies
```bash
sudo apt-get install build-essential cmake-curses-gui git subversion wget
```

Clone repo
```bash
cd $VISP_WS
git clone https://github.com/lagadic/visp.git
```

Setup build folder 
```bash 
mkdir visp-build
cd visp-build 
cmake ../visp
```
NOTE 1: `./visp` (source) and `./visp-build` (build) are (per instructions from tutorial) both in the top level of `$VISP_WS`
NOTE 2: ensure that `USE_FRANKA` and `USE_LIBREALSENSE2` shows up as enabled in the output of cmake (this happened automatically for us).

Build
```bash
make -j <NPROC>
```

To test that it works, try something like:
```language
mkdir $VISP_WS/testing   # becuase we are about the generate files in CWD
cd $VISP_WS/testing
./tutorial/calibration/tutorial-franka-acquire-calib-data --ip <ROBOT-IP>
```
It should pop up a window that displays what the camera sees. It should also have written a file to the current working directory with camera intrinsics. If you left click the window, it should take a snapshot of the camera and a snapshot of the robot end-effector pose and save both the the current working directory.
