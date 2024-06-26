<div align = left>

# simple-server-manager

Manages your .sh script using screen sessions on Raspberry Pi.

## Feautres
Turn on/off .sh script using screen sessions with live console output.

## How it works
It creates screen session with custom ID in the name with logging enabled, then it waits for screen session to create log file (located in folder where .sh script is). If log file is found, then it will be updating console output on html site. After pressing stop button, the script will be turned off with SIGINIT command and screen session will be removed.

## Required packages
* flask-socketio
* gevent-websocket
* eventlet

## Usage
In `simple_server_manager.py` change these variables to yours, you can also change default port.
```python
SERVER_SCRIPT_PATH = "/your/script/path.sh"
SCREEN_LOG_PATH = "/your/log/screenlog.0"
SCREEN_NAME = "screenname"
DEFAULT_PORT = 5000
```
