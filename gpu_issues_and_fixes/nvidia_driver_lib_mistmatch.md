## Issue: 
```
nvidia-smi
#print out
Failed to initialize NVML: Driver/library version mismatch
NVML library version: 580.159
```

## Check versions:
```
cat /proc/driver/nvidia/version
modinfo nvidia | grep '^version'
dpkg -l | grep -E 'nvidia-driver|libnvidia|nvidia-dkms'
```

## Problem pattern:
```
/proc/driver/nvidia/version  -> older loaded kernel module
modinfo nvidia               -> newer module installed on disk
libnvidia / nvidia-driver    -> newer user-space packages

#example:
NVRM version: NVIDIA UNIX x86_64 Kernel Module  580.142  Tue Mar  3 20:04:04 UTC 2026
GCC version:  gcc version 12.3.0 (Ubuntu 12.3.0-1ubuntu1~22.04.3) 
version:        580.159.03
ii  libnvidia-cfg1-580:amd64                   580.159.03-0ubuntu0.22.04.1                      amd64        NVIDIA binary OpenGL/GLX configuration library
ii  libnvidia-common-580                       580.159.03-0ubuntu0.22.04.1                      all          Shared files used by the NVIDIA libraries
rc  libnvidia-compute-550:amd64                550.144.03-0ubuntu0.22.04.1                      amd64        NVIDIA libcompute package
ii  libnvidia-compute-580:amd64                580.159.03-0ubuntu0.22.04.1                      amd64        NVIDIA libcompute package
ii  libnvidia-compute-580:i386                 580.159.03-0ubuntu0.22.04.1                      i386         NVIDIA libcompute package
ii  libnvidia-decode-580:amd64                 580.159.03-0ubuntu0.22.04.1                      amd64        NVIDIA Video Decoding runtime libraries
ii  libnvidia-decode-580:i386                  580.159.0

/proc/driver/nvidia/version: 580.142
modinfo nvidia:              580.159.03
installed packages:          580.159.03
NVML library:                580.159
```

## Lightweight fix
```
sudo dkms status
#inspected whether the NVIDIA DKMS kernel module was built for your installed kernel.

sudo update-initramfs -u
# Rebuilt the boot-time initramfs image. That image contains early-boot kernel modules and metadata. Before the fix, the system from the above example had NVIDIA user-space libraries at 580.159.03, but boot was still loading an older NVIDIA kernel module, 580.142. Rebuilding initramfs made the boot process pick up the correct 580.159.03 module.

sudo reboot
```

## Verify after reboot
```
cat /proc/driver/nvidia/version
modinfo nvidia | grep '^version'
nvidia-smi
```
Expected result: all versions match, and nvidia-smi opens normally.<br>
Why it works: update-initramfs -u refreshes the boot image so Linux loads the current NVIDIA kernel module instead of an older cached module during startup.


## If the lightweigthfix falls:
```
sudo apt install --reinstall nvidia-dkms-580 nvidia-driver-580
sudo dkms autoinstall
sudo update-initramfs -u
sudo reboot
```
Replace 580 with the driver branch installed on the system.



