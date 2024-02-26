# Franka Setup 

Below follows instructions for setting up the franka, installing the latest firmware, and enabling the Franka Control Interface (FCI)

## Physical setup

- Empty the boxes and set up the robot as described in the manual
- Mount the robot securely on a level, rigid platform
- Connect emergency stop button 
- Connect robot to control box 
- Control control box to power 
- Connect ethernet cable from desktop and DIRECTLY to robot (for now)

## Software setup 

- Go to the web interface hosted at robot.franka.de 
- Create an admin account 
- Connect to franka world (can be done directly if robot is connected to the internet, but we did it the manual way)
    - Go to settings -> franka world
    - Download the "register-..." registration file (json with a token) 
    - Sign in to franka world (whoever bought the robot should have credentials)
    - Navigate to the robot and upload the registration file 
    - You will get an "update-" file back as a download 
    - Go back to the franka desk interface and upload the "update-file" (we got one for system version 5.3.0)
    - Wait for it to complete and restart the robot 

## FCI setup 

To control the robot directly from the PC (with libfranka), we need 
to enable FCI. 

- In the web inteface, go to setting->network
- There should be two networks listed here:
    - X5 - Robot network (the one we're connected to right now through the direct ethernet in the X5 port)
    - C2 - Shop floor network (the one we will connect to soon with an ethernet cable in the C2 port on the control box)
- Under the C2/Shop Floor network, deselect the checkbox for DHCP Client and enter the IP address and submask you want to use (we used ip=172.16.0.2, mask=255.255.255.0)
- Hit apply and unplug the ethernet cable from the robot (X5) and plug it into the control box (C2).
- Now, go to network settings on your desktop and configure a static IP for the network interface that is connected to the control box. 
    - On ubuntu, go to Settings->Network and hit the gear icon on the interface that is connected to the robot control 
    - Then go to IPv4, change the Method to "Manual" and under "addresses" configure a valid (but unused) address on the same subnet you set up for the robot (we used 172.16.0.1)
    - Verify that it is set up correctly by e.g. pinging the robot (ping 172.16.0.2)