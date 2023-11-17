## Step by step, how to compile Streamlit Stand alone .exe
## Note: When the .exe is running, The my_exe_App_V1.2.py could be changed an upgrade on the fly (with the local server running)

Reference:
[using-pyinstaller-or-similar-to-create-an-executable Post #73](https://discuss.streamlit.io/t/using-pyinstaller-or-similar-to-create-an-executable/902/73)

## Screenshots
 
![alt text](https://github.com/axisSN01/Streamlit.exe/blob/main/static/Captura.PNG "exec file")

![alt text](https://github.com/axisSN01/Streamlit.exe/blob/main/static/Captura2.PNG "running app")

![alt text](https://github.com/axisSN01/Streamlit.exe/blob/main/static/Captura3.PNG "running app")

![alt text](https://github.com/axisSN01/Streamlit.exe/blob/main/static/Captura4.PNG "running app")



1. Folders structure (If you see more folder than here, dont worry): 
```sh
./my_exe_App_V1.2-Python-Streamlit/
    my_exe_App_V1.2.py
    run_main.py
    run_main.spec
    REAMDE.md
    app.ico
    .gitignore
    logo.png
    requirements.txt
    .streamlit/
        config.toml

    hooks/
        hook-streamlit.py
```

2. install Python interpreter 3.11.3  (🚨<mark>There is a BUG with V 3.11.4 that is not resolved yet</mark>🚨)

3. In the folder Compile (datailed in step 1), open CMD an type: 
```py 
    python3.11 -m venv venv
```
4. In the same console as step 3, activate the virtual enviroment, type:
```sh 
    venv\Scripts\activate
```
You should view the (venv) in the prompt: i.e.: ```(venv) PS C:\Users\alexis_ibarra\Desktop\my_exe_App_V1.2-Python-Streamlit\>```

5. type:  
```sh
    pip install -r requirements.txt
```

6. Compile the executable, type:
```sh
    pyinstaller run_main.spec --clean
```
9. The executable file will be saved in the DIST folder: 
```sh
./my_exe_App_V1.2-Python-Streamlit/
    dist/
        my_exe_App_V1.2.exe
```

10. to check it propertly, cut and paste the my_exe_App_V1.2.exe to another folder.

11. Double click as ADMIN on my_exe_App_V1.2.exe and Enjoy !!


## How to DEBUG? : 

12. 
```
    streamlit run .\my_exe_App_V1.2.py
```

