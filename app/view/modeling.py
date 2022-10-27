from flask_jwt_extended import jwt_required, decode_token
from flask import jsonify, request, send_file
from sklearn.metrics import r2_score
from werkzeug.utils import secure_filename
import os
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from .. import app, user

def path_get(filename):
    filename = secure_filename(filename)
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    first_name=user.find_one({"email":email})['first_name']
    path= app.config['UPLOAD_FOLDER']+first_name+'/'
    if not os.path.exists(path) or not os.path.isfile(path+filename):
      return jsonify(message=filename+" not found"), 404
    return path,first_name

@app.route('/api/linear_regression/<filename>',methods=['POST'])
@jwt_required()
def linear_regression(filename):
    """Endpoint for input csv file、x、y、modeling and dump linear regression
    This is using docstrings for specifications.
    ---
    tags:
      - 'Modeling'
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
    definitions:
      lr_model_build_successfully_message:
        type: object
        properties:
          message:
            type: string
          correlation:
            type: string
    responses:
      200:
        description: ${filename}_LR_model build successfully
        schema:
          $ref: '#/definitions/lr_model_build_successfully_message'
        examples:
          application/json: { "message": "${filename}_LR_model build successfully", "correlation": "0.76" }
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
    model = LinearRegression(fit_intercept=False)
    model.fit(df[[x]],df[[y]])
    joblib.dump(model,path+filename.split('.')[0]+'_'+'LR_model')
    return jsonify(message=filename.split('.')[0]+'_'+'LR_model'+" build successfully",correlation=model.coef_.tolist()), 200

@app.route('/api/multi_regression/<filename>',methods=['POST'])
@jwt_required()
def multi_regression(filename):
    """Endpoint for input csv file、X、y、modeling and dump Multiple regression
    This is using docstrings for specifications.
    ---
    tags:
      - 'Modeling'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
      - name: X
        in: formData
        type: string
        required: true
      - name: y
        in: formData
        type: string
        required: true
    definitions:
      mr_model_build_successfully_message:
        type: object
        properties:
          message:
            type: string
          coefficient:
            type: string
    responses:
      200:
        description: ${filename}_MR_model build successfully
        schema:
          $ref: '#/definitions/mr_model_build_successfully_message'
        examples:
          application/json: { "message": "${filename}_MR_model build successfully", "coefficient": "[0.00755095 0.00780526]" }
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
    X = request.form['X']
    y = request.form['y']
    path,first_name = path_get(filename)
    df = pd.read_csv(os.path.join(path,filename))
    model = LinearRegression()
    print(f"x:{X.split(',')}")
    model.fit(df[X.split(',')],df[[y]])
    joblib.dump(model,path+filename.split('.')[0]+'_'+'MR_model')
    return jsonify(message=filename.split('.')[0]+'_'+'MR_model'+" build successfully",coefficient=model.coef_.tolist()), 200

@app.route('/api/poly_regression/<filename>',methods=['POST'])
@jwt_required()
def poly_regression(filename):
    """Endpoint for input csv file、X、y、modeling and dump Multiple regression
    This is using docstrings for specifications.
    ---
    tags:
      - 'Modeling'
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
    definitions:
      pr_model_build_successfully_message:
        type: object
        properties:
          message:
            type: string
          coefficient:
            type: string
    responses:
      200:
        description: ${filename}_PR_model build successfully
        schema:
          $ref: '#/definitions/pr_model_build_successfully_message'
        examples:
          application/json: { "message": "${filename}_PR_model build successfully", "r2_score": "0.94" }
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
    model = numpy.poly1d(numpy.polyfit(df[x],df[y],3))
    joblib.dump(model,path+filename.split('.')[0]+'_'+'PR_model')
    return jsonify(message=filename.split('.')[0]+'_'+'PR_model'+" build successfully",r2_score=r2_score(df[y],model(df[x]))), 200

@app.route('/api/decision_tree/<filename>', methods=['POST'])
@jwt_required()
def decision_tree(filename):
    """Endpoint for input csv file、features、y、modeling and dump decision tree
    This is using docstrings for specifications.
    ---
    tags:
      - 'Modeling'
    security:
      - Bearer: []
    parameters:
      - name: filename
        in: path
        type: string
        required: true
      - name: features
        in: formData
        type: string
        required: true
      - name: y
        in: formData
        type: string
        required: true
    responses:
      200:
        description: ${filename}_dtree build successfully
        examples:
          application/json: { "message": "${filename}_dtree build successfully" }
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
    features = request.form['features']
    y = request.form['y']
    path,first_name = path_get(filename)
    df = pd.read_csv(os.path.join(path,filename))
    labelencoder = LabelEncoder()
    X = df[features.split(',')]
    y=labelencoder.fit_transform(df[y])
    dtree = DecisionTreeClassifier()
    dtree = dtree.fit(X,y)
    joblib.dump(dtree,path+filename.split('.')[0]+'_'+'dtree')
    return jsonify(message=filename.split('.')[0]+'_'+'dtree'+" build successfully"), 200
