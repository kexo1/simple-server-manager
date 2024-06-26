from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import subprocess
import os
import uuid
import eventlet

app = Flask(__name__)
socketio = SocketIO(app)

# CHANGE THIS
SERVER_SCRIPT_PATH = "/mnt/sata/servers/valheim_server/start_server.sh" # Path to your server script
SCREEN_LOG_PATH = "/mnt/sata/servers/valheim_server/screenlog.0" # Path to your screen session log
SCREEN_NAME = "valheim_server_"
DEFAULT_PORT = 5000

# Variable to store the current session ID and server status
current_session_id = None
server_status = False

@app.route('/')
def index():
    global server_status
    return render_template('index.html', status=server_status)

@app.route('/start', methods=['POST'])
def start_server():
    global current_session_id, server_status
    if not server_status:
        # Generate a unique session ID
        current_session_id = str(uuid.uuid4())
        screen_session_name = f"{SCREEN_NAME}{current_session_id}"
        
        # Clear the previous log file (if exists)
        try:
            if os.path.exists(SCREEN_LOG_PATH):
                os.remove(SCREEN_LOG_PATH)
        except Exception as e:
            print(f"Error while removing screen log file: {str(e)}")
        
        # Start screen session with logging enabled
        try:
            subprocess.run(["screen", "-L", "-Logfile", SCREEN_LOG_PATH, "-dmS", screen_session_name, SERVER_SCRIPT_PATH])
            server_status = True
            # Start the background task to tail the log file
            socketio.start_background_task(target=tail_log)
        except Exception as e:
            print(f"Error while starting screen session: {str(e)}")
        
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_server():
    global current_session_id, server_status
    if server_status:
        screen_session_name = f"{SCREEN_NAME}{current_session_id}"
        # Send SIGINT to the screen session to gracefully stop the server and save the world
        try:
            subprocess.run(["screen", "-S", screen_session_name, "-X", "stuff", "^C"])
            server_status = False
        except Exception as e:
            print(f"Error while stopping screen session: {str(e)}")
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    global server_status
    emit('server_status', {'status': server_status})

def tail_log():
    """Tail the screen log file and emit updates to connected clients."""
    retries = 0
    max_retries = 10
    # Get session log file with 10 retries (depends on server start speed)
    while retries < max_retries:
        try:
            with open(SCREEN_LOG_PATH, 'r') as f:
                while True:
                    line = f.readline()
                    if not line:
                        socketio.sleep(1)  # Use socketio.sleep instead of time.sleep
                        continue
                    socketio.emit('console_output', {'data': line}, namespace='/')
        except FileNotFoundError:
            print(f"Screen log file not found, retrying... ({retries}/{max_retries})")
            retries += 1
            socketio.sleep(1)  # Use socketio.sleep instead of time.sleep
        except Exception as e:
            print(f"Error in tail_log task: {str(e)}")
            break

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=DEFAULT_PORT)
