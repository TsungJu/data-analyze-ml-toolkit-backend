from xml.etree.ElementInclude import include
from flask_jwt_extended import jwt_required, decode_token
from flask import jsonify, request, send_file
from werkzeug.utils import secure_filename
import os, io
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import plotly.express as px
from .. import app, user
from flask import Blueprint

analyzing_blueprint = Blueprint('analyzing_blueprint', __name__)

def path_get(filename):
    filename = secure_filename(filename)
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    first_name=user.find_one({"email":email})['first_name']
    path= app.config['UPLOAD_FOLDER']+first_name+'/'
    if not os.path.exists(path) or not os.path.isfile(path+filename):
      return jsonify(message=filename+" not found"), 404
    return path,first_name

@analyzing_blueprint.route('/api/info/<filename>',methods=['GET'])
@jwt_required()
def info(filename):
    """Endpoint for analyzing csv file and return csv info
    This is using docstrings for specifications.
    ---
    tags:
      - 'Analyzing'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    responses:
      200:
        description: csv info get successfully
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "csv info get successfully" }
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
      404:
        description: ${filename} not found
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${filename} not found" }
    """
    path,first_name = path_get(filename)
    df = pd.read_csv(os.path.join(path,filename))
    buffer = io.StringIO()
    print(type(df.columns))
    df.info(buf=buffer)
    info = buffer.getvalue().split('\n')
    return jsonify(message="csv info get successfully",info=info,columns=df.columns.to_list()), 200

@analyzing_blueprint.route('/api/correlation/<filename>',methods=['GET'])
@jwt_required()
def correlation(filename):
    """Endpoint for analyzing csv file and return correlation
    This is using docstrings for specifications.
    ---
    tags:
      - 'Analyzing'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    responses:
      200:
        description: correlation get successfully
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "correlation get successfully" }
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
      404:
        description: ${filename} not found
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${filename} not found" }
    """
    path,first_name = path_get(filename)
    df = pd.read_csv(os.path.join(path,filename))
    corr = df.corr().to_json()
    return jsonify(message="correlation get successfully",corr=corr), 200

@analyzing_blueprint.route('/api/diagram_plot/<filename>',methods=['GET'])
@jwt_required()
def plotting(filename):
    """Endpoint for input csv file、save and return diagram
    This is using docstrings for specifications.
    ---
    tags:
      - 'Analyzing'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    produces:
      - image/png
    responses:
      200:
        description: diagram png file save and get successfully
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
      404:
        description: ${filename} not found
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${filename} not found" }
    """
    path,first_name = path_get(filename)
    df = pd.read_csv(os.path.join(path,filename))
    df.plot()
    plt.savefig(os.path.join(path,filename.split('.')[0]+"_diagram.png"))
    plt.close()
    plt.cla()
    plt.clf()
    return send_file(app.config['DOWNLOAD_FOLDER']+first_name+'/'+filename.split('.')[0]+"_diagram.png", mimetype='image/png')

@analyzing_blueprint.route('/api/scatter_plot/<filename>',methods=['POST'])
@jwt_required()
def scatter_plot(filename):
    """Endpoint for input csv file、x axis、y axis、save and return scatter plot 
    This is using docstrings for specifications.
    ---
    tags:
      - 'Analyzing'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
      - name: x
        in: formData
        type: string
        required: true
      - name: y
        in: formData
        type: string
        required: true
    produces:
      - image/png
    responses:
      200:
        description: scatter plot png file save and get successfully
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
      404:
        description: ${filename} not found
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${filename} not found" }
    """
    x = request.form['x']
    y = request.form['y']
    path,first_name = path_get(filename)
    df = pd.read_csv(os.path.join(path,filename))
    df.plot(kind = 'scatter',x=x,y=y)
    plt.savefig(os.path.join(path,filename.split('.')[0]+"_x_"+x+"_y_"+y+"_scatter.png"))
    plt.close()
    plt.cla()
    plt.clf()
    return send_file(app.config['DOWNLOAD_FOLDER']+first_name+'/'+filename.split('.')[0]+"_x_"+x+"_y_"+y+"_scatter.png", mimetype='image/png')

@analyzing_blueprint.route('/api/histogram_plot/<filename>',methods=['POST'])
@jwt_required()
def hist(filename):
    """Endpoint for input csv file、column、save and return histogram plot 
    This is using docstrings for specifications.
    ---
    tags:
      - 'Analyzing'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
      - name: column
        in: formData
        type: string
        required: true
    produces:
      - image/png
    responses:
      200:
        description: histogram plot png file save and get successfully
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
      404:
        description: ${filename} not found
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${filename} not found" }
    """
    column = request.form['column']
    path,first_name = path_get(filename)
    df = pd.read_csv(os.path.join(path,filename))
    df[column].plot(kind = 'hist')
    plt.savefig(os.path.join(path,filename.split('.')[0]+"_"+column+"_histogram.png"))
    plt.close()
    plt.cla()
    plt.clf()
    return send_file(app.config['DOWNLOAD_FOLDER']+first_name+'/'+filename.split('.')[0]+"_"+column+"_histogram.png", mimetype='image/png')

# Because transfer size bigger than image/png, temp comment out
'''
@analyzing_blueprint.route('/api/guest/<first_name>/histogram_plotly/<filename>',methods=['POST'])
def hist_plotly(first_name,filename):
    x = request.form['column']
    #y = request.form['y']
    #path,first_name = path_get(filename)
    path = app.config['UPLOAD_FOLDER']+"guest/"+first_name+'/'
    df_data = pd.read_csv(os.path.join(path,filename))
    fig = px.histogram(df_data, x=x)
    return fig.to_html().split("<body>")[1].split("</body>")[0]
'''

@analyzing_blueprint.route('/api/guest/<first_name>/histogram_plot/<filename>',methods=['POST'])
def guest_hist_plotly(first_name,filename):
    column = request.form['column']
    path = app.config['UPLOAD_FOLDER']+"guest/"+first_name+'/'
    df = pd.read_csv(os.path.join(path,filename))
    df[column].plot(kind = 'hist')
    plt.savefig(os.path.join(path,filename.split('.')[0]+"_"+column+"_histogram.png"))
    plt.close()
    plt.cla()
    plt.clf()
    return send_file(app.config['DOWNLOAD_FOLDER']+"guest/"+first_name+'/'+filename.split('.')[0]+"_"+column+"_histogram.png", mimetype='image/png')

@analyzing_blueprint.route('/api/guest/<first_name>/info/<filename>',methods=['GET'])
def guest_info(first_name,filename):
    path = app.config['UPLOAD_FOLDER']+"guest/"+first_name+'/'
    df = pd.read_csv(os.path.join(path,filename))
    buffer = io.StringIO()
    print(type(df.columns))
    df.info(buf=buffer)
    info = buffer.getvalue().split('\n')
    return jsonify(message="csv info get successfully",info=info,columns=df.columns.to_list()), 200
