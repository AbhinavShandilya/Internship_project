import serial
import openpyxl
from datetime import datetime

# Initialize serial port
ser = serial.Serial('COM5', 9600)  # Replace 'COM1' with your serial port and 9600 with the baud rate

# Create a new Excel workbook
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Serial Data"

# Write headers to Excel file
sheet['A1'] = 'Timestamp'
sheet['B1'] = 'Data'


# Function to write data to Excel
def write_to_excel(timestamp, data):
    sheet.append([timestamp, data])
    workbook.save("serial_data_ultra_1306_3.xlsx")


try:
    while True:
        # Read data from serial port
        data = ser.readline().strip().decode()
        print(data)
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write data to Excel
        write_to_excel(timestamp, data)

except KeyboardInterrupt:
    print("Process interrupted.")
finally:
    # Close serial port and save Excel file
    ser.close()
    workbook.close()
