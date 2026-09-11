import uuid

from flask import Flask, jsonify, request
app = Flask(__name__)
USERS=[]
@app.route('/user', methods= ['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    if not name or not password:
        return jsonify({'error': 'Name and password are required'}), 400
    user = {
        'name': name,
        'password': password,
        'user_id': str(uuid.uuid4())
       }
    USERS.append(user)
    return {"id": user.get('user_id'), "name": user.get('name')}, 201
if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 4040, debug = True)
    