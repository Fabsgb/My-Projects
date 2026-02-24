from flask import Flask, jsonify, render_template, request
import alarm
from threading import Thread
from gpiozero import Button
from waiting import wait
from datetime import datetime
import socket
import os

app = Flask(__name__,
            # Point both templates and static files to your desired folder
            template_folder='../Web/Alarm Control',
            static_folder='../Web/Alarm Control',
            static_url_path='')

# Global state to track if alarm is running
alarm_state = {'is_running': False, 'is_triggered': False}
system_logs = []

def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    system_logs.insert(0, f"[{timestamp}] {message}")

sensor = Button(4)

def monitor_alarm():
    """Waits for the sensor event, then triggers the alarm."""
    try:
        # Wait until sensor triggers (is not active) OR system is disarmed
        # We check alarm_state['is_running'] so we can exit if the user clicks Disarm
        wait(lambda: not sensor.is_active or not alarm_state['is_running'], sleep_seconds=0.1)
        
        # If we are still armed (meaning the sensor triggered it), start the alarm
        if alarm_state['is_running']:
            alarm_state['is_triggered'] = True
            add_log("ALARM TRIGGERED!")
            alarm.Start_Alarm(Buzzer_Pin=3, Buzzer_Sleep=0.5, Led_Pin=17, Led_Sleep=0.66, Console_Sleep=0.25)
    except Exception as e:
        print(f"Error in monitor thread: {e}")

@app.route('/')
def home():
    """Serves the main index.html page."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({**alarm_state, 'logs': system_logs})

@app.route('/api/toggle', methods=['POST'])
def toggle_alarm():
    try:
        # Get the password sent from the website
        data = request.get_json()
        if not data or data.get('password') != "Password":
            return jsonify({'error': 'Incorrect password'}), 401

        if alarm_state['is_running']:
            alarm.Stop_Alarm()
            alarm_state['is_running'] = False
            alarm_state['is_triggered'] = False
            message = "Alarm stopped (disarmed)."
            add_log(message)
        else:
            alarm_state['is_running'] = True
            alarm_state['is_triggered'] = False
            Thread(target=monitor_alarm).start()
            message = "Alarm armed. Waiting for event..."
            add_log(message)
        
        return jsonify({'is_running': alarm_state['is_running'], 'message': message})
    except Exception as e:
        # Log the error to the Gunicorn console and return a proper error response
        print(f"!!! HARDWARE ERROR: {e}")
        # Ensure state is correct on failure
        alarm_state['is_running'] = False
        return jsonify({'error': f'A server-side hardware error occurred: {e}'}), 500

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    data = request.get_json()
    if not data or data.get('password') != "Password":
        return jsonify({'error': 'Incorrect password'}), 401
    system_logs.clear()
    add_log("Logs cleared.")
    return jsonify({'message': 'Logs cleared'})

if __name__ == '__main__':
    # Helper to find local IP
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    print(f"\n\n *** ACCESS WEBSITE AT: https://{get_ip()}:5000 *** \n\n")
    # debug=True is great for development
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
