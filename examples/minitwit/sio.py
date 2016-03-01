from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('sio.html')

@socketio.on('connect')
def handle_connection():
    print('connected')
    emit('news', { 'hello': 'world' })

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=1233, host='0.0.0.0')
