from flask_jwt_extended import jwt_required, decode_token
from flask import jsonify, request, render_template, redirect, send_from_directory
from werkzeug.utils import secure_filename
import os
from os import listdir
import pandas as pd
import matplotlib.pyplot as plt
import sys
from .. import app, user

ALLOWED_EXTENSIONS = {'csv','png'}
app.config['DOWNLOAD_FOLDER'] = 'data/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Endpoint for upload csv file and analyzing data
    This is using docstrings for specifications.
    ---
    tags:
      - 'File'
    security:
      - Bearer: []
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      201:
        description: ${filename} upload successfully
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${filename} Upload successfully" }
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(message="No file part"), 400
    
        file = request.files['file']
        
        if file.filename == '':
            return jsonify(message="No selected file"), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            token = request.headers['Authorization'].split(' ')[1]
            email = decode_token(token)['sub']
            first_name=user.find_one({"email":email})['first_name']
            path= app.config['UPLOAD_FOLDER']+first_name+'/'
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path,filename))
            #df = pd.read_csv(os.path.join(path,filename))
            #df.plot()
            #plt.savefig(os.path.join(path,"test.png"))
            return jsonify(message=filename+" Upload successfully"), 201
            #return redirect(url_for('uploaded_file',filename=filename))

    # return render_template('upload.html')

@app.route('/api/guest/<first_name>/upload', methods=['POST'])
def guest_upload_file(first_name):
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(message="No file part"), 400
    
        file = request.files['file']
        
        if file.filename == '':
            return jsonify(message="No selected file"), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path= app.config['UPLOAD_FOLDER']+"/guest/"+first_name+'/'
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path,filename))
            fileList = listdir(path)
            return jsonify(message=filename+" Upload successfully",filelist=fileList), 201

@app.route('/api/guest/<first_name>/uploaded',methods=['GET'])
def guest_uploaded(first_name):
    path = app.config['UPLOAD_FOLDER']+"/guest/"+first_name+'/'
    if not os.path.exists(path):
      os.makedirs(path)
    files = listdir(path)
    return jsonify(filelist=files), 200

@app.route('/api/guest/<first_name>/delete/<filename>', methods=['DELETE'])
def guest_delete(first_name,filename):
    path = app.config['UPLOAD_FOLDER']+"/guest/"+first_name+'/'
    if os.path.exists(path):
      os.remove(path+filename)
      return jsonify(message=filename+" Delete successfully"), 200
    else:
      return jsonify(message=first_name+" folder not found"), 404

@app.route('/api/uploaded',methods=['GET'])
@jwt_required()
def uploaded():
    """Endpoint for list uploaded file
    This is using docstrings for specifications.
    ---
    tags:
      - 'File'
    security:
      - Bearer: []
    responses:
      200:
        description: List uploaded file successfully
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": [2021ETF2.0.png,flask-developer-roadmap.png] }
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
    """
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    first_name = user.find_one({"email":email})['first_name']
    path = app.config['UPLOAD_FOLDER']+first_name
    if not os.path.exists(path):
      os.makedirs(path)
    files = listdir(path)
    return jsonify(message=files), 200

@app.route('/api/download/<filename>', methods=['GET'])
@jwt_required()
def download(filename):
    """Endpoint for download file
    This is using docstrings for specifications.
    ---
    tags:
      - 'File'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    responses:
      200:
        description: Download file successfully
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
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    first_name = user.find_one({"email":email})['first_name']
    path = app.config['DOWNLOAD_FOLDER']+first_name+'/'
    if not os.path.exists('app/'+path) or not os.path.isfile('app/'+path+filename):
      return jsonify(message=filename+" not found"), 404
    return send_from_directory(path,filename, as_attachment=True)

@app.route('/api/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete(filename):
    """Endpoint for delete file
    This is using docstrings for specifications.
    ---
    tags:
      - 'File'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    responses:
      200:
        description: ${filename} delete successfully
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${filename} delete successfully" }
      401:
        description: Missing Authorization Header
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Missing Authorization Header" }
      404:
        description: ${first_name} Folder not found
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "${first_name} Folder not found" }
    """
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    first_name=user.find_one({"email":email})['first_name']
    path= app.config['UPLOAD_FOLDER']+first_name+'/'
    if os.path.exists(path):
      os.remove(path+filename)
      return jsonify(message=filename+" Delete successfully"), 200
    else:
      return jsonify(message=first_name+" folder not found"), 404
