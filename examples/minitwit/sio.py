#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
from threading import Thread
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None

def background_stuff():
     """ python code in main.py """
     print 'In background_stuff'
     while True:
         time.sleep(1)
         t = str(time.clock())
         print '==='
         socketio.emit('news', {'hello': 'This is data', 'time': t}, broadcast=True)


def init_thread():
    global thread
    if thread is None:
        thread = Thread(target=background_stuff)
        thread.daemon = True
        thread.start()
        print '*'*20 + 'Thread init' + '*'*20


@app.route('/')
def index():
    return render_template('sio.html')


@socketio.on('connect')
def handle_connection():
    print('-' * 20 + 'connected' + '-' * 20)
    emit('news', { 'hello': 'world' })
    init_thread()


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send('re:' + message)
    emit('other', { 'hello': 'hahahahah' })


if __name__ == '__main__':
    socketio.run(app, debug=True, port=1233, host='0.0.0.0')
