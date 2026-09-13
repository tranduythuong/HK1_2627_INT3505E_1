from flask import Flask,jsonify,request
STUDENTS = [
    {'id': 1, 'name': 'Nguyen Van An'},
    {'id': 2, 'name': 'Tran Thi Binh'},
    {'id': 3, 'name': 'Le Van Cuong'},
    {'id': 4, 'name': 'Pham Thi Dung'}
]
app = Flask(__name__)
def find_student_by_id(student_id):
    for st in STUDENTS:
        if st['id'] == student_id:
            return st
    return None

@app.route('/students',methods = ['POST'])
def create_student():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Invalid request'}), 400
    id = len(STUDENTS) + 1
    data['id'] = id
    STUDENTS.append(data)
    return jsonify({'status': 'success', 'student': data}), 201

@app.route('/students', methods = ['GET'])
def get_students():
    start = request.args.get('start', default=0, type=int)
    limit = request.args.get('limit', default=10, type=int)
    list = STUDENTS[start:(start + limit)]
    return jsonify({'status':'success','list': list}), 200

@app.route('/students/<int:student_id>', methods = ['GET'])
def get_student(student_id):
    student = find_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({'status': 'success', 'student': student}), 200

@app.route('/students/<int:student_id>', methods = ['PUT'])
def update_student(student_id):
    student = find_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    student.update(data) # phuong thuc co san cua dict,set
    return jsonify({'status': 'success', 'student': student}), 200

@app.route('/students/<int:student_id>', methods = ['DELETE'])
def delete_student(student_id):
    student = find_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    STUDENTS.remove(student)
    return '', 204
if __name__ == '__main__':
    app.run(host = 'localhost', port = 4040, debug = True)