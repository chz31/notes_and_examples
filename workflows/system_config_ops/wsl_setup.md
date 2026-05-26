In wsl, more memory might need to be assigned. The default is only 8.

In Power Shell, type:
```
notepad C:\Users\user_name\.wslconfig
```
or
```
notepad $env:USERPROFILE\.wslconfig
```

If the file is not existed, Win will try to create a one.

In the opened .wslconfig file, add the desired RAM information, seperated by lines
```
[wsl2]
memory=48GB
processors=8
swap=48GB
```

Save and Close it.

Close the wsl terminal
```
wsl --shutdown
```

Reopen WSL, and check the memory:
```
free -h
```

Install necessary dependencies including g++
```
sudo apt update
sudo apt install -y build-essential
```

Check installation
```
which gcc
gcc --version
which g++
g++ --version
```

Return to `/home/your_user_name/` in the terminal 
```
cd ~
```

Go to `C:Users` in Windows
```
cd c /mnt/c/Users/your_user_name/
```

copy-paste between Windowsn & WSL
```
# copy a file
cp /mnt/c/Users/chi.zhang/Documents/example.txt ~/target/

# copy a folder
cp -r /mnt/c/Users/chi.zhang/Documents/myfolder ~/target/

# example
cp -r /mnt/c/Users/chi.zhang/Downloads/SOFA_v25.12.99-full_Linux/SOFA_v25.12.99_Linux ~/sofa/
```

## Issues

Missing libgl libraries when trying to load `pygmsh` in python in a pixi env
```
OSError: libGLU.so.1: cannot open shared object file: No such file or directory
OSError: libXft.so.2: cannot open shared object file: No such file or directory
```
Solution:
```
sudo apt update
sudo apt install -y libglu1-mesa
sudo apt install -y libxft2 libxrender1 libx11-6 libxext6 fontconfig
```

