#!/usr/bin/env python

from flask import Flask, jsonify, url_for, render_template
from subprocess import call, Popen
from vedis import Vedis
import re

app = Flask(__name__)

class bulb:
    def __init__(self):
        self.path_base = '/usr/local/bin/'
        self.base = self.path_base + 'bulb'
        self.dimm_base = self.path_base + 'dimm_bulb'
        self.ved = Vedis('store.ved')

    def __del__(self):
        self.ved.close()

    def run(self, arg):
        call(['sudo', self.base, arg])

    def dimm(self, level, inc):
        Popen(['sudo', self.dimm_base, '-l ' + str(level), '-i ' + str(inc)])

    def undimm(self, level, inc):
        Popen(['sudo', self.dimm_base, '-l ' + str(level), '-i ' + str(inc), '-r'])
    

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

@app.route('/api/v1.0/dimm/<int:level>/<int:increment>/')
def dimm(level, increment):
    """
    Dimm the bulb with the increment
    """
    
    com = bulb()
    com.dimm(level, increment)

    return jsonify({ 'success' : True })

@app.route('/api/v1.0/brighten/<int:level>/<int:increment>/')
def brighten(level, increment):
    """
    Brightens the bulb with the increment
    """
    
    com = bulb()
    com.undimm(level, increment)

    return jsonify({ 'success' : True })

@app.route('/api/v1.0/warm/<int:brightness>/')
def warm(brightness):
    """
    Set the bulb to warm mode and set the brightness (10-255)
    """

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
def colour(colour):
    """
    Set the colour of the bulb in hex
    """
    
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
