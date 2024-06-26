# -*coding: utf-8 -*
from flask import Flask, jsonify, request
from flask_restx import Api, Resource
import mysql.connector

app = Flask(__name__)
api = Api(app)
app.config['JSON_AS_ASCII'] = False



#DB_URL = "d" # 환경변수 설정해보자.
#DB_USER =
#DB_PASS =
#DB_NAME =

def connection(): # SQL과 연결할 때 사용
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",# 비밀번호
        database="re_triver_test",# DB명
        charset='utf8'
    )

def close(cursor, db_connection): # 사용 후 반드시 닫아주기!
    return cursor.close(); db_connection.close()

@api.route('/')
class Test(Resource):
    def get(self):
        success = "success"
        return jsonify({"result":success}), 200


@api.route('/upload')
class UploadImage(Resource):
    def post(self):
        if 'image' not in request.files:
            return {"isUploadSuccess" : "false"}, 400
        image = request.files['image']
        image.save(image.filename) # 이미지를 현재 작업 디렉토리에 저장합니다.
        return jsonify({"isUploadSuccess" : "success"}), 200


@api.route('/menus')
class Menus(Resource):
    def get(self):  # 해당 함수 return 값이 http return값으로 들어감
        # connect with db
        db_connection = connection()
        cursor = db_connection.cursor()
        # GET
        query = 'SELECT * FROM menu'
        cursor.execute(query)
        # return
        data = cursor.fetchall()
        print(data[0][0])

        #close
        close(cursor,db_connection)

        return jsonify({
            "id":data[0][0],
            "name":data[0][1],
            "price":data[0][2],
        })


if __name__ == '__main__':
    app.run(debug=True)

