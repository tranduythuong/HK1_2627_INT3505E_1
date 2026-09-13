from flask import Flask,jsonify,request
app = Flask(__name__)
ORDERS = [
    {'id': 1, 'status': 'pending'},
    {'id': 2, 'status': 'shipped'},
    {'id': 3, 'status': 'delivered'}
]
def find_order_by_id(order_id):
    for order in ORDERS:
        if order['id'] == order_id:
            return order
    return None
@app.route('/orders/<int:order_id>',methods=['DELETE'])
def delete_order(order_id):
    order = find_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    if order['status'] in ['delivered', 'shipped']:
        return jsonify({'error': 'Cannot delete order'}), 409
    ORDERS.remove(order)
    return '', 204
if __name__ == '__main__':
    app.run(host = 'localhost', port = 4040, debug = True)