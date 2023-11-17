import streamlit.web.bootstrap
import os, sys, time, pdb

import shutil


# #Definir la función que se ejecutará cuando se reciba la señal de cierre de la ventana
# def handler_exit():
#     try:
#         pdb.set_trace()
#         global server
#         server.stop()
#         # Obtener la lista de directorios en /temp_folder
#         directorios = [nombre for nombre in os.listdir("./tempdir") if os.path.isdir(os.path.join("./tempdir", nombre))]
#         # Borrar todos los directorios en /temp_folder
#         for directorio in directorios:
#                 shutil.rmtree(os.path.join("./tempdir", directorio))
#     except:
#         # Al final del programa, restaurar la señal predeterminada para cerrar la aplicación
#         signal.signal(signal.SIGINT, signal.SIG_DFL)

# # Registrar la función para que se ejecute cuando se reciba la señal de cierre de la ventana
# signal.signal(signal.SIGINT, handler_exit)

def build_config_file():

    # Verificar si la carpeta .streamlit existe, si no, crearla
    if not os.path.exists("./.streamlit"):
        os.mkdir("./.streamlit")

    # Abrir el archivo de texto config.txt en modo escritura
    with open("./.streamlit/config.toml", "w") as f:
        # Escribir las líneas necesarias en el archivo
        f.write("[theme]\n")
        #f.write("base=\"dark\"\n\n")
        f.write("backgroundColor=\"#2a2a2a\"\n\n")
        f.write("secondaryBackgroundColor=\"#4d3d74\"\n\n") 
        f.write("primaryColor=\"#199dab\"\n\n") 
        f.write("textColor=\"#FFFFFF\"\n\n") 
        f.write("font=\"sans serif\"\n\n") 

        f.write("[global]\n")
        f.write("developmentMode = false\n\n")
        f.write("[server]\n")
        f.write("port = 8501\n")
        f.write("maxUploadSize = 1000000\n")
        f.write("maxMessageSize = 1000000\n\n")
        f.write("[logger]\n")
        f.write("level=\"info\"\n")
        
      


if __name__ == "__main__":

    #armo el config file 
    build_config_file()
    # obtener la ruta del directorio actual
    current_dir = os.getcwd()
    if not os.path.exists("./tempdir"):
        os.mkdir("./tempdir")

    temp_path= os.path.join(current_dir, 'tempdir')
    # crear una lista con los nombres de las carpetas en el directorio actual
    folder_list = os.listdir(temp_path)

    # tiempo inicial
    init_time=time.gmtime(0)
    # iterar a través de la lista de carpetas y detecta la sesion actual
    for folder in folder_list:
        folder_path = os.path.join(temp_path, folder)
        folder_last_modified_time = time.gmtime(os.path.getmtime(folder_path))

        if folder_last_modified_time>=init_time:

            init_time = folder_last_modified_time
            session_folder = folder

    # borro temporales viejos
    for folder in folder_list:
        if folder!=session_folder:
            shutil.rmtree(os.path.join("./tempdir", folder))

    session_main_path = os.path.join(temp_path, session_folder, 'my_exe_App_V1.2.py')

    if os.path.isfile(session_main_path):
        # construir la ruta de la carpeta2
        print(f"\nmy_exe_App_V1.2.py session path is : {session_main_path}\n")

    else:
        print("\nFolder tempdir not found\n")
        sys.exit()


    streamlit.web.bootstrap.run(
        session_main_path,
        "streamlit run",
        [],
        {
            "_is_running_with_streamlit": True,
        },
    )
