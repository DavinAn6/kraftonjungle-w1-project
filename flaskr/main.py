from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient

# Connects to local MongoDB. Database: "dbjungle", Collection: "memos".
# client = MongoClient('localhost', 27017)
# db = client.dbjungle                        
# db.memos.create_index([("like", -1)]) 

from bson.objectid import ObjectId

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('dashboard.html')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)