#!/usr/bin/env python

from flask import Flask, jsonify, url_for, render_template
from subprocess import call
import re

app = Flask(__name__)

class bulb:
    def __init__(self):
        self.base = '/usr/local/bin/bulb'

    def run(self, arg):
        call(['sudo', self.base, arg])

def list_routes():
    import urllib
    output = {}
    for rule in app.url_map.iter_rules():
        doc = app.view_functions[rule.endpoint].__doc__
        if rule.rule.startswith('/api/') and doc != None:
            output[rule.rule] = doc.strip()

    return output

@app.route('/api/v1.0/on/')
def on():
    """
    Turn the bulb on
    """
    com = bulb()
    com.run('-e')
    return jsonify({ 'success' : True })

@app.route('/api/v1.0/off/')
def off():
    """
    Turn the bulb off
    """
    com = bulb()
    com.run('-d')
    return jsonify({ 'success' : True })

@app.route('/api/v1.0/warm/<int:brightness>/')
def warm(brightness=None):
    """
    Set the bulb to warm mode and set the brightness (10-255)
    """

    if colour == None:
        return jsonify({'success' : False, 'error' : 'no brightness given'})


    com = bulb()
    val = max(min(brightness, 255), 0)
    hexVal = hex(val)[2:].zfill(2).strip()
    hexVal = re.sub(r'\W+', '', hexVal)
    com.run(''.join(['-w ', hexVal]))

    return jsonify({ 
            'success'   : True, 
            'value'     : val,
            'hex value' : hexVal
            })

@app.route('/api/v1.0/colour/<string:colour>/')
def colour(colour=None):
    """
    Set the colour of the bulb in hex
    """
    if colour == None:
        return jsonify({'success' : False, 'error' : 'no colour given'})
    
    com = bulb()
    com.run(''.join(['-c ', colour]))

    return jsonify({ 
            'success' : True, 
            'colour'  : colour,
            })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1.0/')
def api():
    return jsonify({
            'success' : True,
            'version' : 1.0,
            'methods' : list_routes()
            })

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
