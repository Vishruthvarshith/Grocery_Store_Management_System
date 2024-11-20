from flask import Flask, request, jsonify, render_template
import sql_connect , json
import manage_functions
from flask_cors import CORS

app = Flask(__name__)
 
connection = sql_connect.connect_sql()
# Establish connection and initialize triggers

manage_functions.initialize_triggers(connection)  

@app.route('/', methods = ['GET'])
def home_page():
    return "This is a starting page, give some endpoints to see some result"


@app.route('/getProducts', methods=['GET'])
def get_products():
    response = manage_functions.get_all_products(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/insertProduct', methods=['POST'])
def insert_product():
    request_payload = json.loads(request.form['data'])
    product_id = manage_functions.insert_new_product(connection, request_payload)
    response = jsonify({
        'product_id': product_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/updateProduct', methods= ['POST'])
def update_product():
    request_payload = json.loads(request.form['data'])
    product_id = manage_functions.update_a_product(connection,request_payload)
    response = jsonify({
        'product_id': product_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    return_id = manage_functions.delete_product(connection, request.form['product_id'])
    response = jsonify({
        'product_id': return_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/getAllOrders', methods=['GET', 'POST'])
def get_all_orders():
    response = manage_functions.get_all_orders(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/insertOrder', methods=['POST'])
def insert_order():
    request_payload = json.loads(request.form['data'])
    order_id = manage_functions.insert_order(connection, request_payload)
    response = jsonify({
        'order_id': order_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')    
    return response

@app.route('/orderDetails', methods=['GET','POST'])
def order_details():
    response = manage_functions.get_all_order_details(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/getUOM', methods=['GET'])
def get_uom():
    response = manage_functions.get_uoms(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
# Flask routes to call stored procedures
@app.route('/callAddProduct', methods=['POST'])
def call_add_product():
    try:
        request_payload = json.loads(request.data)
        name = request_payload['name']
        uom_id = request_payload['uom_id']
        price_per_unit = request_payload['price_per_unit']

        cursor = connection.cursor()
        cursor.callproc('AddProduct', [name, uom_id, price_per_unit])
        connection.commit()
        cursor.close()

        return jsonify({"message": "Product added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/callCreateOrder', methods=['POST'])
def call_create_order():
    try:
        request_payload = json.loads(request.data)
        customer_name = request_payload['customer_name']
        order_datetime = request_payload['order_datetime']
        order_id = 0  # Initialize INOUT parameter

        cursor = connection.cursor()
        result_args = cursor.callproc('CreateOrder', [customer_name, order_datetime, order_id])
        connection.commit()
        cursor.close()

        return jsonify({"order_id": result_args[2]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/callDeleteProduct', methods=['POST'])
def call_delete_product():
    try:
        product_id = request.json['product_id']

        cursor = connection.cursor()
        cursor.callproc('DeleteProduct', [product_id])
        connection.commit()
        cursor.close()

        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/callUpdateProduct', methods=['POST'])
def call_update_product():
    try:
        request_payload = json.loads(request.data)
        product_id = request_payload['product_id']
        new_name = request_payload['new_name']
        new_uom_id = request_payload['new_uom_id']
        new_price_per_unit = request_payload['new_price_per_unit']

        cursor = connection.cursor()
        cursor.callproc('UpdateProduct', [product_id, new_name, new_uom_id, new_price_per_unit])
        connection.commit()
        cursor.close()

        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    


if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")
    app.run(port=5000, debug = True)
