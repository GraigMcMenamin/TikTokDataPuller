from datetime import datetime
import requests
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import csv
import pandas as pd
import shutil
import tkinter.simpledialog as sd
import tkinter.messagebox as messagebox
import sys

# Global variables
data_types_vars = []
data_types_options = []
field_name_checkboxes = []
field_names_options = []
operations_vars = []
field_name_values = []
not_field_name_checkboxes = []
not_field_names_options = []
not_operations_vars = []
not_field_name_values = []
search_id = ''
client_key = ''
client_secret = ''
access_token = ''

# Generate access token
def get_access_token():

    url = "https://open.tiktokapis.com/v2/oauth/token/"
    payload = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }

    # Send request for access token
    response = requests.post(url, data=payload, headers=headers)

    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract access token from full response
        access_token = data.get('access_token')
        if access_token:
            return access_token
        else:
            return None
    else:
        return None
    
def authenticate():
    global client_key, client_secret, access_token 
    # Prompt the user to enter client key and client secret
    client_key = sd.askstring("Client Key", "Enter your client key:")
    if client_key is None:
        return None, None
    client_secret = sd.askstring("Client Secret", "Enter your client secret:")
    if client_secret is None:
        return None, None
    # Get access token
    access_token = get_access_token()
    return
    
authenticate()
if not access_token:
    choice = messagebox.askretrycancel("Error", "Invalid client key or secret.")
    if not choice:  # If user chooses to exit
        sys.exit()
    authenticate()

    
# Function to create a frame with checkboxes for data types
def create_data_types_frame(parent_frame):
    global data_types_vars, data_types_options

    data_types_frame = ttk.Frame(parent_frame, padding=10)
    data_types_frame.grid(column=0, row=1)
    data_types_options = ['id', 'region_code', 'video_description', 'view_count', 'comment_count', 'create_time', 'like_count', 'share_count', 'music_id', 'effect_ids', 'hashtag_names', 'playlist_id', 'voice_to_text', 'username']
    data_types_vars = [tk.BooleanVar(value=True) for _ in data_types_options]

    for i, data_type in enumerate(data_types_options):
        ttk.Checkbutton(data_types_frame, text=data_type, variable=data_types_vars[i]).grid(row=i, column=0, sticky=tk.W)

# Function to create a frame for selecting included parameters
def create_parameters_frame(parent_frame):
    global field_name_checkboxes, field_names_options, operations_vars, field_name_values

    parameters_frame = ttk.Frame(parent_frame, padding=10)
    parameters_frame.grid(column=1, row=1)

    field_names_options = ["keyword", "create_date", "username", "region_code", "video_id", "hashtag_name", "music_id", "effect_id", "video_length"]
    field_name_checkboxes = [tk.BooleanVar() for _ in field_names_options]
    operations_vars = [tk.StringVar(value="") for _ in field_names_options]
    field_name_values = [tk.StringVar(value="") for _ in field_names_options]

    for i, field_name in enumerate(field_names_options):
        ttk.Checkbutton(parameters_frame, text=field_name, variable=field_name_checkboxes[i]).grid(row=i, column=0, sticky=tk.W)
        operations_dropdown = ttk.Combobox(parameters_frame, values=["", "EQ", "IN", "GT", "GTE", "LT", "LTE"], textvariable=operations_vars[i], state="readonly", width=3)
        operations_dropdown.grid(row=i, column=2, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(parameters_frame, textvariable=field_name_values[i]).grid(row=i, column=3, padx=5, pady=5, sticky=tk.W)

# Function to create a frame for selecting excluded parameters
def create_not_parameters_frame(parent_frame):
    global not_field_name_checkboxes, not_field_names_options, not_operations_vars, not_field_name_values

    not_parameters_frame = ttk.Frame(parent_frame, padding=10)
    not_parameters_frame.grid(column=4, row=1)

    not_field_names_options = ["keyword", "create_date", "username", "region_code", "video_id", "hashtag_name", "music_id", "effect_id", "video_length"]
    not_field_name_checkboxes = [tk.BooleanVar() for _ in not_field_names_options]
    not_operations_vars = [tk.StringVar(value="") for _ in not_field_names_options]
    not_field_name_values = [tk.StringVar(value="") for _ in not_field_names_options]

    for i, not_field_name in enumerate(not_field_names_options):
        ttk.Checkbutton(not_parameters_frame, text=not_field_name, variable=not_field_name_checkboxes[i]).grid(row=i, column=0, sticky=tk.W)
        not_operations_dropdown = ttk.Combobox(not_parameters_frame, values=["", "EQ", "IN", "GT", "GTE", "LT", "LTE"], textvariable=not_operations_vars[i], state="readonly", width=3)
        not_operations_dropdown.grid(row=i, column=5, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(not_parameters_frame, textvariable=not_field_name_values[i]).grid(row=i, column=6, padx=5, pady=5, sticky=tk.W)

# Function to generate and run API request, as well as organize response data
def make_api_request():
    global search_id

    # Pull all info for request from user
    data_types = [data_types_options[i] for i, var in enumerate(data_types_vars) if var.get()]
    start_date = start_date_calendar.get_date()
    end_date = end_date_calendar.get_date()
    max_count = max_count_entry.get()
    cursor = cursor_entry.get()

    #check if the first page is being requested, if so there's no need for a search id
    if cursor == '0': 
        search_id = ''

    param_list = []
    for i in range(len(field_names_options)):
        if field_name_checkboxes[i].get():
            element = {
                "operation": operations_vars[i].get(),
                "field_name": field_names_options[i],
                "field_values": field_name_values[i].get().split(',')  # Split values into a list
            }
            param_list.append(element)


    not_param_list = []
    for i in range(len(not_field_names_options)):
        if not_field_name_checkboxes[i].get():
            element = {
                "operation": not_operations_vars[i].get(),
                "field_name": not_field_names_options[i],
                "field_values": not_field_name_values[i].get().split(',')  # Split values into a list
            }
            not_param_list.append(element)

    # Define url endpoint and headers
    url = "https://open.tiktokapis.com/v2/research/video/query/?fields=" + ','.join(data_types)
    headers = {
        "authorization": "bearer " + access_token,
        "Content-Type": "application/json",
    }

    # Put all request data together to from the request's body
    request_data = {
        "query": {
            "and": param_list,
            "not": not_param_list
        },
        "start_date": start_date,
        "end_date": end_date,
        "max_count": max_count,
        "cursor": cursor,
        "search_id": search_id
    }

    print('REQUEST: ',request_data) # Print request body to console

    response = requests.post(url, json=request_data, headers=headers) # Make request
    
    if response.status_code == 200: # Check if request was successful

        print('RESPONSE: ',response.text) # Print response to console
        data = response.json()

        # check if response is empty
        if 'data' in data and 'videos' in data['data'] and isinstance(data['data']['videos'], list) and data['data']['videos']:
            videos_data = data['data']['videos']  # Extract the 'videos' data from the full response
        else:
            # end function if query returns empty data
            print('Query successful, no data was returned.')
            result_label.config(text="Query successful, no data was returned.")
            return
        
        # Check if the data has more value to pull
        has_more = data['data']['has_more']
        if has_more == True:
            # if so, take the search_id (there will be no search_id if there are no more values)
            search_id = data['data']['search_id']

        # Collect all unique column names from all videos
        all_column_names = list(set.union(*(set(video.keys()) for video in videos_data)))

        # Ensure that all columns from data_types are present in the DataFrame
        for column in data_types:
            if column not in all_column_names:
                # If column is missing, add an empty column with the corresponding title
                all_column_names.append(column)

        # Put column in alphabetical order
        all_column_names.sort()

        # Create a DataFrame with all unique column names
        df = pd.DataFrame(columns=all_column_names)

        # Populate the DataFrame with video data
        for video in videos_data:
            df = pd.concat([df, pd.DataFrame([video], columns=all_column_names)], ignore_index=True)

        # Iterate over specified columns
        columns_to_quote = ['id', 'music_id', 'playlist_id', 'create_time']
        for column in columns_to_quote:
            if column in df.columns:
                # change long id numbers to strings
                # df[column] = df[column].astype(str)
                # add apostrophes in front of id numbers so excel processes them as strings
                df[column] = df[column].apply(lambda x: f"'{x}" if pd.notnull(x) else x)

        # Save the DataFrame to a CSV file
        df.to_csv('temp_api_response.csv', index=False)

        # Provide a download link for the user
        download_button.config(state=tk.NORMAL)
        result_label.config(text="API request successful.\nCSV file ready for download.")

    else:
        # Set result message if error occurs, using tiktok's error
        result_label.config(text=f"Error: {response.status_code}\n" + response.text)

# Function to initiate the download
def download_csv():
    date = datetime.now().strftime("%Y-%m-%d  %H-%M-%S")
    date = date+'.csv'
    shutil.move('temp_api_response.csv', date) # Renames temporary file and makes permanent
    result_label.config(text="CSV file downloaded")
    download_button.config(state=tk.DISABLED) # disable button to stop multiple downloads

# Create a Tkinter window
window = tk.Tk()
window.title("TikTok Video Data Puller")

# Create and layout GUI elements
frame = ttk.Frame(window, padding=10)
frame.grid(column=0, row=0)

# Label Parameter entry sections
data_types_label = ttk.Label(frame, text="Response Data Types")
data_types_label.grid(column=0, row=0)
included_parameters_label = ttk.Label(frame, text="Included Parameters")
included_parameters_label.grid(column=1, row=0)
excluded_parameters_label = ttk.Label(frame, text="Excluded Parameters")
excluded_parameters_label.grid(column=4, row=0)

# Call functions for data types and parameters directly
create_data_types_frame(frame)
create_parameters_frame(frame)
create_not_parameters_frame(frame)

# Start and end date entry using calendars
start_date_label = ttk.Label(frame, text="Start/End Date:")
start_date_label.grid(column=0, row=2, padx=5, pady=5, sticky=tk.W)
start_date_calendar = Calendar(frame, selectmode="day", date_pattern="ymmdd")
start_date_calendar.grid(column=0, row=3)
end_date_calendar = Calendar(frame, selectmode="day", date_pattern="ymmdd")
end_date_calendar.grid(column=1, row=3)

# Text box for max count entry
max_count_label = ttk.Label(frame, text="Max Count (1-100):")
max_count_label.grid(column=0, row=4, padx=5, pady=5, sticky=tk.W)
max_count_entry = ttk.Entry(frame, width=15)
max_count_entry.grid(column=0, row=4, sticky=tk.E)
max_count_entry.insert(0, "100")

# Text box for max count entry
cursor_label = ttk.Label(frame, text="Cursor :")
cursor_label.grid(column=0, row=5, padx=5, pady=5, sticky=tk.W)
cursor_entry = ttk.Entry(frame, width=15)
cursor_entry.grid(column=0, row=5, sticky=tk.E)
cursor_entry.insert(0, "0")

# Result label that changes based on status of requests, responses, and downloads
result_label = ttk.Label(frame, text="", wraplength=300)
result_label.grid(column=0, row=6)

# Button to run request
submit_button = ttk.Button(frame, text="Make API Request", command=make_api_request)
submit_button.grid(column=0, row=7)

# Button to intiate file download for response
download_button = ttk.Button(frame, text="Download CSV", state=tk.DISABLED, command=download_csv)
download_button.grid(column=0, row=8)

# Start the Tkinter main loop

window.mainloop()
