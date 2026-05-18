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
