## Use the binary
Install SOFA binary

Install python3.12 and add python.exe to path. No need to use admin.

Open environment variables in admin mode
[Tutorial]()


Create new system variables:
```
SOFA_ROOT: C:\Users\chi.zhang\SOFA\v25.12.00
PYTHON_ROOT: C:\Users\user_name\AppData\Local\Programs\Python\Python312
PYTHONPATH: %SOFA_ROOT%\plugins\SofaPython3\lib\python3\site-packages
```

In Edit Environments, open path, and add these row by row by hitting New each time, instead of just attaching one line separeted by `;` as in the tutorial
```
%PYTHON_ROOT%
%PYTHON_ROOT%\DLLs
%PYTHON_ROOT%\Lib
%PYTHON_ROOT%\Scripts
%SOFA_ROOT%\bin
```
Full path might be needed, for example
```
C:\Users\chi.zhang\AppData\Local\Programs\Python\Python312
C:\Users\chi.zhang\AppData\Local\Programs\Python\Python312\DLLs
C:\Users\chi.zhang\AppData\Local\Programs\Python\Python312\Lib
C:\Users\chi.zhang\AppData\Local\Programs\Python\Python312\Scripts
C:\Users\chi.zhang\SOFA\v25.12.00\bin
```

In a cmd.exe, test
```
where python
python -V
python -m pip install numpy scipy
where runSofa
runSofa -lSofaPython3
```


Python install path is usually in:
```
C:\Users\user_name\AppData\Local\Programs\Python\Python312
```


Test runSOFA
```
runSofa -lSofaPython3 C:\Users\chi.zhang\Documents\chi_vs_workspace\slicersofa_sofa_scratches\sofa_experiments\sofa_retraction_scene_debug.py
```


