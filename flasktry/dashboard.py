from flask import  render_template
from flask import request
import csv
import plotly.express as px
import plotly.graph_objs as go
import json
import pandas as pd
import plotly
import os
directory = os.getcwd()

def getCSVFile():
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    except Exception as e:
        return render_template('error.html', error=e)
    return render_template('file_selection.html', files=files)


def displayData():
    try:
        selected_file = request.form.get('selected_file')
        #print("selected_file: ", selected_file)
        readData = readCSVData(selected_file)
        uniqueId = set(row[0] for row in readData if row[0].isdigit())
        uniqueHomeNumber  = uniqueStatus = set(row[1] for row in readData)
        uniqueStatus = set(row[3] for row in readData)
        return render_template('dashboardNewTry.html', unique_ids=uniqueId, data = readData, selected_file = selected_file, unique_status = uniqueStatus, unique_home_number = uniqueHomeNumber)
    except Exception as e:
        return render_template('error.html', error=e)

def readCSVData(selected_file):
    data = []
    #print("31 csv name - ", selected_file)
    with open(selected_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data


def filter_by_id():
    try:
        selected_id = request.args.get('id')
        selected_status = request.args.get('status')
        selected_home = request.args.get('homeid')
        print('45 selected_home: ', selected_home)
        print('46 selected_status: ', selected_status)
        selected_file = request.args.get('selected_file')
        # Read data from the CSV file
        data = readCSVData(selected_file)  # Implement this function to read your CSV data
        # Filter the data based on the selected Id
        if selected_id:
            print('50 inside selected_id: ', selected_id)
            filtered_data = [row for row in data if row[0] == selected_id]
        elif selected_status:
            filtered_data = [row for row in data if row[3] == selected_status]
        elif selected_home:
            filtered_data = [row for row in data if row[1] == selected_home]
        else:
            filtered_data = data  # No filter, show all data
        print('56 filtered_data: ', filtered_data)
        if selected_id:
            plot_json = generate_scatter_plot(selected_id, selected_file)
            return render_template('filterbyID.html', filtered_data=filtered_data, data=data, plot_json=plot_json)
        else:
            return render_template('filterbyID.html', filtered_data=filtered_data, data=data, plot_json=None)
    except Exception as e:
        return render_template('error.html', error=e)


def readcsvwithPandas(selected_id, selected_file):
    selected_id = int(selected_id)
    date_parser = lambda x: pd.to_datetime(x, format='mixed')
    # Read the CSV file with the custom date parser
    df = pd.read_csv(selected_file)
    newDF = df[df['Id'] == selected_id]
    # Define the column names you want to select
    selected_columns = ['Reading','Date']
    # Filter the DataFrame to include only the selected columns
    filtered_df = df[selected_columns]
    filtered_df = df.loc[df['Id'] == selected_id]
    # Print the filtered DataFrame
    return filtered_df

def generate_scatter_plot(selected_id, selected_file):
    # Create a scatter plot using Plotly

    filtered_df = readcsvwithPandas(selected_id, selected_file)  # Make sure you have a function to read your data
    #print('Filtered DataFrame:', filtered_df)

    # Create a bar trace
    trace = go.Bar(x=filtered_df['Date'], y=filtered_df['Reading'])

    # Create a figure and add the trace
    fig = go.Figure(data=[trace])

    # Customize the chart appearance and labels
    fig.update_layout(title='Reading Bar Plot', xaxis_title='Date', yaxis_title='Reading Value')

    # Convert the chart to JSON format
    plot_json = fig.to_json()
    #print('Plot JSON:', plot_json)

    return plot_json  # Return JSON data
