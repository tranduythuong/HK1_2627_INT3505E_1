from flask import Flask,jsonify,request
app = Flask(__name__)
USERS = [
    {"id": 1, "name": "Duy"},
    {"id": 2, "name": "An"},
    {"id": 3, "name": "Minh"},
    {"id": 5, "name": "Minh Nam"},
    {"id": 4, "name": "Tran Manh Nam"}
]
@app.route('/user/<int:user_id>',methods=['GET'])
def get_user(user_id):
    user= find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'status': 'success', 'user': user}), 200
def find_by_id(user_id):
    for user in USERS:
        if user['id'] == user_id:
            return user
    return None
@app.route('/user',methods=['GET'])
def get_users():
    limit = request.args.get('limit;', default=10, type=int)
    name = request.args.get('name', default='', type=str).strip().lower()
    users = [ user for user in USERS if name in user['name'].lower()]
    if not users:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'status': 'success', 'users': users[:limit]}), 200
if __name__ == '__main__':
    app.run(host = 'localhost', port = 4040, debug = True)
