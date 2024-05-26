# -*coding: utf-8 -*
import os
from flask import Flask, jsonify, request, send_file
from flask_restx import Api, Resource
import mysql.connector
import torch
from PIL import Image

app = Flask(__name__)
api = Api(app)
app.config['JSON_AS_ASCII'] = False

# 데이터베이스 연결 정보 하드코딩
DB_URL = "127.0.0.1"
DB_USER = "root"
DB_PASS = "your_password"  # MySQL root 비밀번호
DB_NAME = "re_triver_test"

def connection():
    return mysql.connector.connect(
        host=DB_URL,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8'
    )

def close(cursor, db_connection):
    cursor.close()
    db_connection.close()

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def detect_objects(image_path):
    results = model(image_path)
    return results.pandas().xyxy[0]  # pandas DataFrame으로 반환

def get_recycle_method(object_name):
    db_connection = connection()
    cursor = db_connection.cursor()
    query = 'SELECT recycle_method FROM recycle_methods WHERE object_name = %s'
    cursor.execute(query, (object_name,))
    result = cursor.fetchone()
    close(cursor, db_connection)
    return result[0] if result else "분리수거 방법을 찾을 수 없습니다."

@api.route('/')
class Test(Resource):
    def get(self):
        success = "success"
        return jsonify({"result": success}), 200

@api.route('/upload')
class UploadImage(Resource):
    def post(self):
        if 'image' not in request.files:
            return {"isUploadSuccess": "false"}, 400
        image = request.files['image']
        image_path = os.path.join("uploads", image.filename)
        image.save(image_path)  # 이미지를 현재 작업 디렉토리에 저장합니다.

        # 객체 검출 수행
        detections = detect_objects(image_path)

        # 결과를 텍스트 파일로 저장
        result_file_path = os.path.join("results", f"{os.path.splitext(image.filename)[0]}.txt")
        with open(result_file_path, 'w', encoding='utf-8') as f:
            for _, row in detections.iterrows():
                object_name = row['name']
                recycle_method = get_recycle_method(object_name)
                f.write(f"Object: {object_name}\n")
                f.write(f"Recycle Method: {recycle_method}\n\n")

        return send_file(result_file_path, as_attachment=True), 200

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("results"):
        os.makedirs("results")
    app.run(debug=True)