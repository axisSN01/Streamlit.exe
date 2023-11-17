# -*- coding: utf-8 -*-


__author__ = 'Alexis Ibarra'

import streamlit as st
import pandas as pd
from datetime import datetime
import pdb
import os
# img_to_bytes and img_to_html inspired from https://pmbaumgartner.github.io/streamlitopedia/sizing-and-images.html
import base64
from pathlib import Path
import sys

###################################### Global constants ##########################################
ATTRIBUTE_NAME_MAPPING = {
}


###################################### Global Functions ####################################################### 

############################## Style functions #########################################    
# Define a function to apply color to selected rows
# Streamlit not render Pandas styler 
# https://discuss.streamlit.io/t/pandas-dataframe-style-not-rendering-in-st-experimental-data-editor/40174/2
def highlight_rows(row, color):
        return f'background-color: {color}'

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def img_to_html(img_path):

    img_html = "<img src='data:image/png;base64,{}' width='100' height='100' align=center>".format(
      img_to_bytes(img_path)
    )
    html_content = f'<div class="header-image" style="text-align: center;">{img_html}</div>'

    return html_content
############################## Data Processing functions #####################################################

def process_role(df, selected_change, selected_start_date, selected_end_date):


    if selected_change == "Add" or selected_change == "Extension":
        df["sunrise"] = selected_start_date
        df["sunset"] = selected_end_date

        if selected_change == "Add":
            df["operation"] = "AddRole"
        else:
            df["operation"] = "RemoveRole"

    elif selected_change == "Remove":
        df["operation"] = "RemoveRole"
        df["sunrise"] = ""
        df["sunset"] = ""
    
    df.rename(columns={"SAP ID": "nativeIdentity"}, inplace=True)
    df.rename(columns={"PeopleKey": "identityName"}, inplace=True)
    df.rename(columns={"Roles": "roles"}, inplace=True)    

    # reorder columns
    df = df[["operation","roles","identityName","sunrise","sunset","nativeIdentity"]]

    return df

def process_entitlement(df, selected_change, selected_start_date, selected_end_date):

    if selected_change == "Add" or selected_change == "Extension":
        df["attributeValue"] = df["Entitlement"] + "@" + \
                    datetime.strftime(selected_start_date, "%m/%d/%Y") + "@" +\
                    datetime.strftime(selected_end_date, "%m/%d/%Y")
        
        df["attributeName"] = df["application"].map(ATTRIBUTE_NAME_MAPPING)  
        df.drop(columns="Entitlement",inplace=True)          
        df.rename(columns={"PeopleKey": "identityName"}, inplace=True)

        if selected_change == "Add":
            df["operation"] = "AddEntitlement"

        else:
            df["operation"] = "RemoveEntitlement"


    elif selected_change == "Remove":
        df["operation"] = "RemoveEntitlement"
        df.rename(columns={"PeopleKey": "identityName"}, inplace=True)
        df["attributeName"] = df["application"].map(ATTRIBUTE_NAME_MAPPING)        
        df.rename(columns={"Entitlement":"attributeValue"},inplace=True)          



    # reorder columns
    df.rename(columns={"SAP ID": "nativeIdentity"}, inplace=True)
    df = df[["operation","application","attributeName","attributeValue","identityName","nativeIdentity"]]
    
    return df


def perform_etl(df):
    # Find index rows with blanks
    blank_rows = df[df.isnull().all(axis=1)].index.tolist()

    # Find index rows that need trimming
    trim_rows = df[df.applymap(lambda x: isinstance(x, str) and x.strip() != x if isinstance(x, str) else False).any(axis=1)].index.tolist()

    # Drop blank rows and trim specified rows
    cleaned_df = df.drop(blank_rows).applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return cleaned_df, blank_rows, trim_rows


def create_list_df(df, selected_process):

    chunk_list_cleaned_200_EID=[]

    column_name="identityName"

    list_df_to_csv = chunk_dataframes(df, chunk_list_cleaned_200_EID, column_name)
    
    return list_df_to_csv


def chunk_dataframes(df, chunk_list_cleaned_200_EID, column_name):
    #suffle rows
    df_suffle = df.sample(frac=1).reset_index(drop=True)
    
    garbage_df = pd.DataFrame()

    # Step 2: Cut the suffled dataframe into chunks of 2000 lines as maximum
    chunks = [df_suffle[i:i+2000] for i in range(0, len(df_suffle), 2000)]


    for chunk in chunks:
        # get the pd.Series of EIDs present in the current chunk, EID grouped by count of rows.
        counts = chunk[column_name].value_counts()
        # get the list of the EID that has more than 200 rows.
        excess_values = counts[counts > 200].index.tolist()

        # if the list is not blank, i.e. [], then ...
        if excess_values:
            for value in excess_values:
                # for the current EID get the exceded rows, i.e. more than 200 rows.
                excess_rows = chunk[chunk[column_name] == value].iloc[200:]

                # concat to the garbage_df the whole rows that has been exceding 200 rows ( to be proceesed after)
                garbage_df = pd.concat([garbage_df, chunk.loc[excess_rows.index]])

                # for the current chunk drop the execed rows (there are now saved in garbage_df) 
                chunk = chunk.drop(excess_rows.index)

            # once it finished to clean the current chunk, saved in the list of cleaned chunks.
            chunk_list_cleaned_200_EID.append(chunk)
            
    # check if the chunk_list_cleaned_200_EID list is empty, if true is because there is not
    # troubles with EID counts over 200, so retrieve the original list chunks.
    if not chunk_list_cleaned_200_EID:
        return chunks

    # once finished the process, check garbage_df if is needed to continue moving rows
    if not garbage_df.empty:
        counts = garbage_df[column_name].value_counts()
        excess_values = counts[counts > 200].index.tolist()
        if excess_values:
            # if yes, then made a recursvie call to the function, but now the df input is the garbage_df
            chunk_dataframes(garbage_df, chunk_list_cleaned_200_EID, column_name)
            # once finish return the df list.
            return chunk_list_cleaned_200_EID
        
        else:
            # if not, lets say, when your finish to clean the garbage_df, append the garbage_df to the final list to be returned.
            chunk_list_cleaned_200_EID.append(garbage_df)
            return chunk_list_cleaned_200_EID

    else:
        # if not, lets say, there is no more garbage, just return
        return chunk_list_cleaned_200_EID
    

@st.experimental_memo
def read_files_to_df_list(files):
    
    df_list = []

    for file in files: 
        if ".xlsx" in os.path.basename(file.name):
            temp_df = pd.read_excel(file)
            temp_df.name = os.path.basename(file.name)

        elif ".csv" in os.path.basename(file.name):
            temp_df = pd.read_csv(file)
            temp_df.name = os.path.basename(file.name)

        df_list.append(temp_df)

    return df_list


def compare_dataframe_headers(dataframe_list):
    if len(dataframe_list) <= 1:
        return [True, None, None]
    
    reference_headers = list(dataframe_list[0].columns)
    
    for df in dataframe_list[1:]:
        if list(df.columns) != reference_headers:
            return [False, dataframe_list[0], df]
    
    return [True, None, None]   


def download_data(df_chunk_list):

    # Get the user's home directory
    home_directory = os.path.expanduser("~")

    # Define the relative path to the Downloads folder
    relative_path = "Downloads"

    # current time folder
    current_datetime_folder = "my_exe_App_V1.2 results " + datetime.now().strftime("%m-%d-%y %H_%M_%S")

    # Combine the home directory and relative path
    downloads_folder = os.path.join(home_directory, relative_path, current_datetime_folder)
    os.makedirs(downloads_folder)

    for idx, chunk in enumerate(df_chunk_list):
        # Create the full file path for the CSV file
        csv_file_path = os.path.join(downloads_folder, f"my_exe_App_V1.2_{idx:02d}.csv")

        chunk.to_csv(csv_file_path, index=False)
    
    return downloads_folder


##################################################  Main REACT function ####################################################

def main(session_main_path):

    version = "1.2"
    df_output = pd.DataFrame()
    df = pd.DataFrame()
    uploaded_files = None
    downloaded_clicked = None

    ##################### Initialization session variables #################################
    if 'ready_to_download' not in st.session_state:
        st.session_state['ready_to_download'] = False

    if 'chunck_list_ready' not in st.session_state:
        st.session_state['chunck_list_ready'] = []

    ############################# Page header #####################################
    st.set_page_config(
        page_title=f"Streamlit_my_exe_App_V{version}", 
        layout="wide",
        page_icon="😎",
        initial_sidebar_state="expanded",
        menu_items={
        'Get Help': 'https://help..com/',
        'Report a bug': "https://apps.powerapps.com/play",
        'About': f"##### Version {version}, made by alexis ibarra"
        }
    )

    hide_menu_style = """
        <style>
         [class="css-1uh038d e1pxm3bq0"]{
            visibility: hidden;
         }
        
        footer{
            visibility:hidden;
        }

        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


    st.title("my_exe_App_V1.2")

    # # Create a path to the file "logo.png" in the current working directory
    # if session_main_path=="":
    #     logo_path = "./logo.png"
    # else:
    #     logo_path = os.path.join(session_main_path, "logo.png")
    # Get the parent folder
    logo_path = os.path.join(os.path.dirname(session_main_path),"logo.png")

    # Sidebar content with styled image
    st.sidebar.markdown(img_to_html(logo_path), unsafe_allow_html=True)

    ############################## build the SideBar ###############################

    selected_process = st.sidebar.selectbox(
        "What type of Process?",
        ("Role", "Entitlement")
    )
    selected_change = st.sidebar.selectbox(
        "What type of action?",
        ("Add", "Remove", "Extension")
    )    
    selected_start_date = st.sidebar.date_input(
        "Start date",
        datetime.today(),
    )

    selected_end_date = st.sidebar.date_input(
        "End date",
        datetime.today(),
    )

    # styles for text info
    st.markdown(
    """
    <style>
        [data-testid=stSidebar] [class=stMarkdown] [data-testid=stMarkdownContainer]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
    )

    st.sidebar.markdown("**_______ Info zone ________**")
    st.sidebar.text("Input file count rows:")

    # styles for subheaders text h3 and selected choices
    st.markdown(
    """
    <style type="text/css">
    h3{
        color: rgb(25,157,171);
    }

    li[role="option"][aria-selected="true"] {
    background-color: rgb(25,157,171);
    }

    </style>
    """, unsafe_allow_html=True
    )

    ################################# build main page ###########################
    
    st.experimental_memo.clear()
    uploaded_files = st.file_uploader("Upload a source files", type=["csv", "xlsx"], accept_multiple_files=True)

    if uploaded_files:

        df_list = read_files_to_df_list(uploaded_files)

        is_headers_mismatch = compare_dataframe_headers(df_list)

        st.markdown("<h3>File input preview:</h3>",unsafe_allow_html=True)

        if not is_headers_mismatch[0]:
            st.error('Error: Column names mismatch', icon="🚨")
            st.error(f'{is_headers_mismatch[1].name} with columns: {list(is_headers_mismatch[1].columns)}', icon="📄")
            st.error(f'{is_headers_mismatch[2].name} with columns: {list(is_headers_mismatch[2].columns)}', icon="📄")
            return

        else:
            uploaded_df = pd.DataFrame()
            for df in df_list:
                uploaded_df = pd.concat([uploaded_df, df])


        # Display the input table
        st.write(uploaded_df)
        
        st.markdown("<h3>CSV output preview:</h3>",unsafe_allow_html=True)

        if uploaded_df is not None:
            st.sidebar.markdown(f'**{uploaded_df.shape[0]}**')
            uploaded_df_cleaned, blank_rows, trim_rows = perform_etl(uploaded_df)
            st.sidebar.text("count blank rows:")
            st.sidebar.markdown(f'**{len(blank_rows)}**')  
            st.sidebar.text("count rows to trim:")
            st.sidebar.markdown(f'**{len(trim_rows)}**')     

            if (selected_process == "Role" and "Roles" not in uploaded_df.columns):
                st.error("Please Select the correct Process in the Sidebar", icon="🚨")
                st.error(f"Column expected: 'Roles' ", icon="📄")
                st.error(f"Columns recieved: {list(uploaded_df.columns)} ", icon="📄")               

            elif (selected_process == "Entitlement" and "Entitlement" not in uploaded_df.columns):
                st.error("Please Select the correct Process in the Sidebar", icon="🚨")
                st.error(f"Column expected: 'Entitlement' ", icon="📄")
                st.error(f"Columns recieved: {list(uploaded_df.columns)} ", icon="📄")

            elif selected_process == "Role":
                df_output = process_role(uploaded_df_cleaned, selected_change, selected_start_date, selected_end_date)

            elif selected_process == "Entitlement":       
                df_output = process_entitlement(uploaded_df_cleaned, selected_change, selected_start_date, selected_end_date) 

        st.write(df_output)

        if not df_output.empty:
            if st.button("Process files", type="primary"):
                st.spinner('Operation in progress. Please wait...')            
                st.session_state['chunck_list_ready'] = create_list_df(df_output, selected_process)
                st.session_state['ready_to_download'] = True
                st.sidebar.text("CSV output count:")
                st.sidebar.text(len(st.session_state['chunck_list_ready']))
                st.success('Process Done!')
                st.balloons()

        if st.session_state['ready_to_download']:

            if st.button('Download CSVs', type="primary"):
                downloads_folder = download_data(st.session_state['chunck_list_ready'])
                del st.session_state['chunck_list_ready']
                st.session_state['ready_to_download'] = False
                st.markdown('##### :blue[Your CSVs are available in Folder:]')
                st.markdown(f'{downloads_folder}')
            
    print("\n\nVisuals refreshed...\n\n")   


if __name__=='__main__':
    main(sys.argv[0])
