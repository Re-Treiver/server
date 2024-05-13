# -*- coding: utf-8 -*-
# pip install Flask

from flask import Flask, jsonify, request, redirect, url_for, send_from_directory, render_template,make_response
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from pickletools import read_uint1
from torchvision import models
from PIL import Image
import torchvision.transforms as transforms
import io
import json
import os
import sys
import requests
import base64
import torch




app = Flask(__name__)
CORS(app)

# yolo model 불러오기
model = torch.hub.load('./yolov5/', 'custom', path='./yolov5/runs/train/mask_check_models5/weights/best.pt', source='local')

app.config['UPLOAD_FOLDER'] = './uploads'

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected for uploading'}), 400

    if file:
        # 이미지를 읽어 PIL 이미지로 변환
        image = Image.open(file.stream).convert('RGB')

        # YOLOv5 모델을 사용하여 이미지에서 객체 탐지
        results = model(image, size=640)
        
        # 결과를 DataFrame으로 변환
        results_data = results.pandas().xyxy[0]

        # DataFrame을 JSON 형태로 변환하여 반환
        return results_data.to_json(orient="records")

    else:
        return jsonify({'error': 'Allowed image types are png, jpg, jpeg, gif'}), 400


# POST 통신으로 들어오는 이미지를 저장하고 모델로 추론하는 과정
def save_image(file):
    file.save('./temp/'+ file.filename)

@app.route('/')
def web():
    return "flask test page"

@app.route('/')
def home():
    return 'Hello, World!'

# 데이터베이스 설정
app.config['MYSQL_HOST'] = 'database-moa.cbmghsj09tes.ap-northeast-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_dbname'
app.config['MYSQL_CHARSET'] = 'utf8'

mysql = MySQL(app)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image past in the request'}), 400
    
    file= request.files['image']
    if file.filename == '':
        return jsonify({'error' : 'No image selected for uploading'}), 400
    
    if file and allowed_file(file.filename):
        filename=secure_filename(file.filename)
        file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO images (filename, filepath) VALUES (%s, %s)", (filename, file_path))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'message': 'Image successfully uploaded and saved'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        return jsonify({'error': 'Allowed image types are - png, jpg, jpeg, gif'}), 400


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/index')
def index():
   return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
