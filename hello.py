# -*- coding: utf-8 -*-
from flask import Flask
import time
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World! miso@nagoya %s" %(time.strftime('%l:%M%p %z on %b %d, %Y'))
