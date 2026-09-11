from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json(silent = True) or {}
    return jsonify({"you sent": data}), 200
@app.route('/user', methods=['GET'])
def get_user():
    return jsonify({"status":"200"}), 200
if __name__ == '__main__':
    app.run(host = 'localhost', port = 4040, debug = True)
