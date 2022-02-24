from flask_jwt_extended import jwt_required, decode_token
from flask import jsonify, request, render_template, redirect, send_from_directory
from werkzeug.utils import secure_filename
import os
from .. import app, user

ALLOWED_EXTENSIONS = {'txt','pdf','png','jpg','jpeg', 'gif','csv'}
app.config["UPLOAD_FOLDER"] = 'app/data/'
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            # flash('No file part')
            return redirect(request.url)
    
        file = request.files['file']
        # app.logger.info(test)
        #df = pd.read_csv(file)
        #print(df)
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            token = request.headers['Authorization'].split(' ')[1]
            email = decode_token(token)['sub']
            first_name=user.find_one({"email":email})['first_name']
            path= app.config['UPLOAD_FOLDER']+first_name+'/'
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path,filename))
            return jsonify(message=filename+" Upload successfully"), 201
            #return redirect(url_for('uploaded_file',filename=filename))
    
    return render_template('upload.html')
'''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
'''
@app.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download(filename):
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    print(decode_token(token))
    first_name=user.find_one({"email":email})['first_name']
    path= app.config['UPLOAD_FOLDER']+first_name
    return send_from_directory(path,filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete(filename):
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    first_name=user.find_one({"email":email})['first_name']
    path= app.config['UPLOAD_FOLDER']+first_name+'/'
    if os.path.exists(path):
        os.remove(path+filename)
    return jsonify(message=filename+" Delete successfully"), 200
