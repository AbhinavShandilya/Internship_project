import datetime
import os.path

from flask import request, jsonify
import pandas as pd



def receive_data():
    if request.method == 'POST':
        data = request.get_json()  # Assuming the ESP32 sends JSON data
        if data is not None:
            # Process the received data here
            data = [data]
            print('15 Data: ', data, type(data))
            saveDataCSV(data)
            return jsonify({"message": "Data received and saved successfully"})
        else:
            return jsonify({"error": "Invalid JSON data"}), 400
    else:
        return jsonify({"error": "Only POST requests are allowed"}), 405

def saveDataCSV(data):
    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%Y-%m")
    csv_filename = f'ESP32_Readings_{current_month}.csv'
    if not os.path.exists(csv_filename):
        df = pd.DataFrame(columns=["Id", "Home Number", "Reading", "Status", "Date", "Time"])
    else:
        df = pd.read_csv(csv_filename)

    for item in data:
        new_row = {
            "Id": item["Id"],
            "Home Number": item["Home Number"],
            "Reading": item["Reading"],
            "Status": item["Status"],
            "Date": item["Date"],
            "Time": item["Time"]
        }
        df = df._append(new_row, ignore_index=True)

    df.to_csv(csv_filename, index=False)

