from flask import Flask, jsonify, render_template, request
import alarm
from threading import Thread
from gpiozero import Button
from waiting import wait
from datetime import datetime
import socket
import os
from dotenv import load_dotenv

load_dotenv("/home/fabsgb/Desktop/Programieren/variables.env")

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
            alarm.Start_Alarm(Buzzer_Pin=3, Buzzer_Sleep=0.5, Led_Pin=17, Led_Sleep=0.66, Console_Sleep=0)
    except Exception as e:
        print(f"Error in monitor thread: {e}")

@app.route('/')
def home():
    """Serves the main index.html page."""
    return render_template('index.html')

@app.route('/api/status', methods=['POST'])
def get_status():
    data = request.get_json()
    if not data or data.get('password') != os.environ['web_password']: #You thought you could get my password but naaahhhhh it isnt here 
        return jsonify({'error': 'Incorrect password'}), 401
    return jsonify({**alarm_state, 'logs': system_logs})

@app.route('/api/toggle', methods=['POST'])
def toggle_alarm():
    try:
        # Get the password sent from the website
        data = request.get_json()
        if not data or data.get('password') != os.environ['web_password']:
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
    if not data or data.get('password') != os.environ['web_password']:
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

    # Start a simple HTTP server on port 80 to redirect to HTTPS:8000
    def run_redirector():
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class RedirectHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                # Redirect to the same host but on port 8000 and HTTPS
                host = self.headers.get('Host', '').split(':')[0]
                new_url = f"https://{host}:8000{self.path}"
                self.send_response(301)
                self.send_header('Location', new_url)
                self.end_headers()
            def log_message(self, format, *args):
                pass # Silence logs

        try:
            server = HTTPServer(('0.0.0.0', 80), RedirectHandler)
            print(" * Auto-redirect running: Type IP (http://...) -> redirects to HTTPS:8000")
            server.serve_forever()
        except PermissionError:
            print(" ! NOTE: Run with 'sudo' to enable auto-redirect from port 80.")

    Thread(target=run_redirector, daemon=True).start()

    print(f"\n\n *** ACCESS WEBSITE AT: https://{get_ip()}:8000 *** \n\n")
    # debug=True is great for development
    basedir = os.path.abspath(os.path.dirname(__file__))
    cert_path = os.path.join(basedir, 'cert.pem')
    key_path = os.path.join(basedir, 'key.pem')
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False, ssl_context=(cert_path, key_path), threaded=True)
