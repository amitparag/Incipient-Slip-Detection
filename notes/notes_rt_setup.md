# Realtime Kernel Setup 

Below follows a summary of what we found to work through trial and error when installing a realtime kernel. It is not entirely clear which steps or settings that was the magic bullet, but this is what we did the time it worked.


## Our system and versions 

OS Version: Ubuntu 20.04.5 
Original kernel (that came with the os): Linux 5.15.72
Realtime kernel/patch 5.15.111-rt63

NOTE 1: we also unsuccessfully tried Ubuntu 20.04.06 (kernel 5.15.72)
NOTE 2: we also unsuccessfully tried realtime kernel/patch 5.9.1-rt20 

Note that we tried with a fresh installation of Ubuntu 20.04.05 everytime. If something went wrong, we just reinstalled Ubuntu 20.04.05. Seemed the safest approach.

Download desktop version of Ubuntu from: http://old-releases.ubuntu.com/releases/20.04.5/
## References 

General approach from: https://frankaemika.github.io/docs/installation_linux.html#setting-up-the-real-time-kernel
Config from: https://github.com/2b-t/docker-realtime/blob/main/doc/PreemptRt.md
See also: https://visp-doc.inria.fr/doxygen/visp-daily/tutorial-franka-pbvs.html#franka_pbvs_known_issue_activate_FCI

## Install dependencies 

The following dependencies should be sufficient:
```bash
sudo apt-get install build-essential bc curl ca-certificates gnupg2 libssl-dev lsb-release libelf-dev bison flex dwarves zstd libncurses-dev
```

## Downlaod and extract code 

Download the kernel and patch from official repositories (unofficial ones seems to exist too if you need a version that is not in the mainstream, but we didn't try that).

```
curl -SLO https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.15.111.tar.xz
curl -SLO https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/5.15/patch-5.15.111-rt63.patch.xz

xz -d *.xz
```

Strongly consider also downloading corresponding `.sign` files and verify file integrity with pgp (we didn't that one time everything worked, though).

Once you're sufficiently confident that you downloaded the correct bits, unpack the source code and apply the patch.
```bash
tar xf linux-*.tar
cd linux-*/
patch -p1 < ../patch-*.patch
```

## Configure 

Copy the config from your current active kernel to use as a starting point (should be fine if the current kernel and the realtime kernel you downloaded are sufficiently close).
```bash
cp -v /boot/config-$(uname -r) .config
```

Then initialize the config. (NOTE: `make olddefconfig` is the same as `make oldconfig` if you accept all the defaults in `oldconfig`)
```bash 
make olddefconfig
make menuconfig  # General Setup -> Preemption Model -> Select: Fully Preemptible Kernel (Real-Time)

```
The last command should give you a GUI where you can edit all the config for the build. We only changed the preemption model here (which is IMPORTANT, since franka recommends using the most hardcore / real-time preemption config). 

To set the correct preemption model. Navigate the GUI:
- General Setup
    - Preemption Model
        - And select: "Fully Preemptivle Kernel (Real-Time)"

NOTE: remember to save the config before exiting (use left/right arrow keys).

The rest of the config, we changed by directly modifying the `.config` file with a text editor (since it was faster to search around that way).

```
CONFIG_SYSTEM_TRUSTED_KEYS=""
CONFIG_SYSTEM_REVOCATION_KEYS=""
CONFIG_MODULE_SIG=n
CONFIG_MODULE_SIG_ALL=n
CONFIG_MODULE_SIG_FORCE=n
CONFIG_MODULE_SIG_KEY=""
```

NOTE: we don't know 100% whether all of these options are necessary, but these are the only changes we made to the defaults the time it worked.

## Build and install 

You should now be ready to build the realtime kernel. Run the following command where `<NPROC>` is set equal to the number of cores you have (for speed, we used -j 24).
```bash
sudo make -j <NPROC> deb-pkg
```

NOTE 1: `sudo` seems to be important here (but omitting it didn't give a typical "permission denied" error). 
NOTE 2: `make clean` didn't seem to work completely. Better to delete everything and start again if you have to recompile for some reason.

Assuming, the build was successfull, you should now have a bunch of new files in the parent folder. Of special interest are the `linux-headers` and `linux-image` debian files that you can now install with `dpkg`.

```bash
sudo dpkg -i ../linux-headers-*.deb ../linux-image-*(NOT dbg)*.deb
```

NOTE: there might be two `linux-image-*.deb` files present. If so, do NOT install the one with `dbg` in its name.

## Boot into the new kernel

You should now be ready to boot into the new kernel. However, before you do so, make sure that you have configured the boot loader so that you can easily select it on startup.

Assuming you use `grub`, edit the file `/etc/default/grub` with:
```bash
GRUB_TIMEOUT=15
GRUB_TIMEOUT_STYLE=menu
```
And update grub with 
```bash
sudo update-grub
```

Now, reboot and cross your fingers. You should be able to select the newly installed kernel from the advanced settings in the grub boot menu.

The two times it didn't work for us (but we got this far), all networking was gone after startup and we got a bunch of bugs relating to "smp_processor_id()".

## Set up realtime groups

Assuming you booted into a non-broken system. Finalize the installation by setting up a realtime grouop and add the current user to it

```bash
sudo addgroup realtime 
sudo usermod -a -G realtime $(whoami)

```

Also, the franka tutorial recommends configuring the following limits to `/etc/security/limits.conf`:
```
@realtime soft rtprio 99
@realtime soft priority 99
@realtime soft memlock 102400
@realtime hard rtprio 99
@realtime hard priority 99
@realtime hard memlock 102400
```

Finally, log out and back in again and consider highfiving yourself.
