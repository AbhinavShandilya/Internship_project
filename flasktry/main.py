from flask import Flask, render_template, request, Response, send_file
from request_from_esp import receive_data
from dashboard import displayData, filter_by_id, getCSVFile
from functools import wraps
import os
import subprocess
import threading
import multiprocessing


def getCred():
    try:
        # Get the directory of the current script
        current_directory = os.path.dirname(os.path.abspath(__file__))

    # Path to the credentials file

        file_path = os.path.join(current_directory, 'credentials.txt')

        # Read the contents of the file
        with open(file_path, 'r') as file:
            file_content = file.read()
            return file_content
    except Exception as e:
        print("Credential file missing, need to be created in current folder")
        #return render_template('error.html', error=e)

# Extract credentials using AST (Abstract Syntax Trees) parsing
credentials_dict = {}
file_content = getCred()
try:
    exec(file_content, credentials_dict)
    ADMIN_USERNAME = credentials_dict['ADMIN_CREDENTIALS']['ADMIN_USERNAME']
    ADMIN_PASSWORD = credentials_dict['ADMIN_CREDENTIALS']['ADMIN_PASSWORD']
    print(f"Admin Username: {ADMIN_USERNAME}")
    #print(f"Admin Password: {ADMIN_PASSWORD}")
except Exception as e:
    print(f"Error reading credentials from file: {e}")



def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return Response('Login required', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.before_request
def before_request():
    if request.endpoint == 'home':
        return None

@app.route('/readfile')
def index():
    return getCSVFile()

@app.route('/energy_data_esp', methods=['POST', 'GET'])
def energy_data_esp():
    return receive_data()

@app.route('/dashboardWeb', methods = ['POST', 'GET'])
@requires_auth
def dashboardWeb():
    try:
        return displayData()
    except Exception as e:
        return render_template('error.html', error=e)

@app.route('/dashboardWeb/byId', methods=['GET'])
def filterByID():
    return filter_by_id()

@app.route('/download_file', methods=['GET'])
def download_file():
    selected_file = request.args.get('selected_file')
    file_path = os.path.join(app.root_path, selected_file)

    return send_file(file_path, as_attachment=True)
#if __name__ == '__main__':
 #   app.run(debug=True, host='0.0.0.0', port=80)





def run_flask_app():
    app.run(debug=False, host='0.0.0.0', port=80)

def run_additional_command():
    command = ["tailscale.exe", "funnel", "80"]  # Replace with your command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")

if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Run the additional command
    run_additional_command()

    # Wait for Flask thread to finish (optional)
    flask_thread.join()



import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the saved model
model = joblib.load('energy_model.pkl')

# Load the scaler as well
scaler = joblib.load('scaler.pkl')

@app.route('/predict_energy', methods=['POST'])
def predict_energy():
    # Assuming the user sends features via POST request
    user_data = request.get_json()
    
    # Extract features from the JSON (this needs to be matched with the features expected by your model)
    future_data = pd.DataFrame({
        'Hour': [user_data['Hour']],
        'Day': [user_data['Day']],
        'Month': [user_data['Month']],
        'Weekday': [user_data['Weekday']],
        'Temperature': [user_data['Temperature']],
        'Humidity': [user_data['Humidity']],
        'Lag_Reading_1': [user_data['Lag_Reading_1']],
        'Lag_Reading_2': [user_data['Lag_Reading_2']],
        'Lag_Reading_3': [user_data['Lag_Reading_3']]
    })
    
    # Create cyclical features and interaction terms for prediction
    future_data['Hour_sin'] = np.sin(2 * np.pi * future_data['Hour'] / 24)
    future_data['Hour_cos'] = np.cos(2 * np.pi * future_data['Hour'] / 24)
    future_data['Temp_Hour_interaction'] = future_data['Temperature'] * future_data['Hour']
    
    # Scale the features
    scaled_data = scaler.transform(future_data[['Hour_sin', 'Hour_cos', 'Day', 'Month', 'Weekday', 
                                                'Temperature', 'Humidity', 'Temp_Hour_interaction', 
                                                'Lag_Reading_1', 'Lag_Reading_2', 'Lag_Reading_3']])
    
    # Predict the energy reading
    predicted_reading = model.predict(scaled_data)
    
    return jsonify({'predicted_reading': predicted_reading[0]})



