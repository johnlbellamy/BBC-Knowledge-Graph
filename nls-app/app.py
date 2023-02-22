from nls import NLS

from flask import Flask
from flask_cors import CORS, cross_origin

import numpy as np
import pandas as pd
from string import Template


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/bbc/<bbc_selection>", methods=['GET', 'POST', 'PUT'])
def bbc(bbc_selection):

    NLS.connect()

    nls = nls(bbc_selection)
    nls.tokenize()
    nls.tag() 
    nls.params_builder()
    nls.query_picker()

    return Response(json.dumps(nls.response),  mimetype='application/json')

@app.route("/elabs/<elabs_selection>", methods=['GET', 'POST', 'PUT'])
def elabs(elabs_selection):

    NLS.connect()

    nls = nls(elabs_selection)
    nls.tokenize()
    nls.tag() 
    nls.params_builder()
    nls.query_picker()
 
    return Response(json.dumps(nls.response),  mimetype='application/json')

if __name__ == "__main__":

    app.run(host='0.0.0.0')