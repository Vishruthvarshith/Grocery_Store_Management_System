from sql_connect import connect_sql
from datetime import datetime

# Product functions 

def initialize_triggers(connection):
    cursor = connection.cursor()
    
    # Create the `order_log` table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            message VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Drop and re-create `update_order_total` trigger to avoid duplication
    cursor.execute('DROP TRIGGER IF EXISTS update_order_total;')
    cursor.execute('''
        CREATE TRIGGER update_order_total
        AFTER INSERT ON order_details
        FOR EACH ROW
        BEGIN
            -- Update the total in the orders table based on the inserted order detail
            UPDATE orders
            SET total = (
                SELECT SUM(total_price)
                FROM order_details
                WHERE order_id = NEW.order_id
            )
            WHERE order_id = NEW.order_id;

            -- Insert a log message into the `order_log` table
            INSERT INTO order_log (message)
            VALUES (CONCAT('Order total updated for order_id: ', NEW.order_id));
        END;
    ''')

    # Create the `product_back_up` table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_back_up (
            product_id INT,
            name VARCHAR(100),
            uom_id INT,
            price_per_unit DECIMAL(10, 2),
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Drop and re-create `before_product_delete` trigger to avoid duplication
    cursor.execute('DROP TRIGGER IF EXISTS before_product_delete;')
    cursor.execute('''
        CREATE TRIGGER before_product_delete
        BEFORE DELETE ON products
        FOR EACH ROW
        BEGIN
            INSERT INTO product_back_up (product_id, name, uom_id, price_per_unit, deleted_at)
            VALUES (OLD.product_id, OLD.name, OLD.uom_id, OLD.price_per_unit, NOW());
        END;
    ''')

    connection.commit()
    cursor.close()

def get_all_products(connection):
    cursor = connection.cursor()
    query = ("SELECT products.product_id, products.name, products.uom_id, products.price_per_unit, uom.uom_name "
             "FROM products "
             "INNER JOIN uom ON products.uom_id = uom.uom_id")
    cursor.execute(query)
    response = []
    for (product_id, name, uom_id, price_per_unit, uom_name) in cursor:
        response.append({
            'product_id': product_id,
            'name': name,
            'uom_id': uom_id,
            'price_per_unit': price_per_unit,
            'uom_name': uom_name
        })
    cursor.close()
    return response


def insert_new_product(connection, product):
    cursor = connection.cursor()

    # Check if the product already exists by name
    check_query = "SELECT product_id FROM products WHERE name = %s"
    cursor.execute(check_query, (product['product_name'],))
    existing_product = cursor.fetchone()

    if existing_product:
        # If the product exists, update it
        product_id = existing_product[0]
        update_query = ("UPDATE products SET uom_id = %s, price_per_unit = %s WHERE product_id = %s")
        update_data = (product['uom_id'], product['price_per_unit'], product_id)
        cursor.execute(update_query, update_data)
        connection.commit()
        cursor.close()
        return product_id
    else:
        # If the product does not exist, insert a new product
        insert_query = ("INSERT INTO products (name, uom_id, price_per_unit) VALUES (%s, %s, %s)")
        insert_data = (product['product_name'], product['uom_id'], product['price_per_unit'])
        cursor.execute(insert_query, insert_data)
        connection.commit()
        product_id = cursor.lastrowid
        cursor.close()
        return product_id


def delete_product(connection, product_id):
    cursor = connection.cursor()
    query = "DELETE FROM products WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    connection.commit()
    cursor.close()
    return product_id


def update_a_product(connection, product):
    cursor = connection.cursor()
    product_id = product['product_id']
    query = ("UPDATE products SET name = %s, uom_id = %s, price_per_unit = %s WHERE product_id = %s")
    data = (product['product_name'], product['uom_id'], product['price_per_unit'], product_id)
    cursor.execute(query, data)
    connection.commit()
    cursor.close()
    return product_id


# Order Management Functions
def insert_order(connection, order):
    cursor = connection.cursor()
    order_query = ("INSERT INTO orders "
             "(customer_name, total, datetime)"
             "VALUES (%s, %s, %s)")
    order_data = (order['customer_name'], order['grand_total'], datetime.now())
    cursor.execute(order_query, order_data)
    order_id = cursor.lastrowid
    order_details_query = ("INSERT INTO order_details "
                           "(order_id, product_id, quantity, total_price)"
                           "VALUES (%s, %s, %s, %s)")
    order_details_data = []
    for order_detail_record in order['order_details']:
        order_details_data.append([
            order_id,
            int(order_detail_record['product_id']),
            float(order_detail_record['quantity']),
            float(order_detail_record['total_price'])
        ])
    cursor.executemany(order_details_query, order_details_data)
    connection.commit()
    
    return order_id



def get_all_order_details(connection):
    cursor = connection.cursor()
    query = ("SELECT order_details.order_id, order_details.quantity, order_details.total_price, "
             "products.name, products.price_per_unit "
             "FROM order_details "
             "LEFT JOIN products ON order_details.product_id = products.product_id")
    cursor.execute(query)
    records = []
    for (order_id, quantity, total_price, product_name, price_per_unit) in cursor:
        records.append({
            'order_id': order_id,
            'quantity': quantity,
            'total_price': total_price,
            'product_name': product_name,
            'price_per_unit': price_per_unit
        })
    cursor.close()
    return records


def get_order_details(connection, order_id):
    cursor = connection.cursor()
    query = ("SELECT order_details.order_id, order_details.quantity, order_details.total_price, "
             "products.name, products.price_per_unit "
             "FROM order_details "
             "LEFT JOIN products ON order_details.product_id = products.product_id "
             "WHERE order_details.order_id = %s")
    cursor.execute(query, (order_id,))
    records = []
    for (order_id, quantity, total_price, product_name, price_per_unit) in cursor:
        records.append({
            'order_id': order_id,
            'quantity': quantity,
            'total_price': total_price,
            'product_name': product_name,
            'price_per_unit': price_per_unit
        })
    cursor.close()
    return records


def get_all_orders(connection):
    cursor = connection.cursor()
    query = "SELECT * FROM orders"
    cursor.execute(query)
    response = []
    for (order_id, customer_name, total, dt) in cursor:
        response.append({
            'order_id': order_id,
            'customer_name': customer_name,
            'total': total,
            'datetime': dt,
        })
    cursor.close()
    for record in response:
        record['order_details'] = get_order_details(connection, record['order_id'])
    return response


# UOM Functions
def get_uoms(connection):
    cursor = connection.cursor()
    query = "SELECT * FROM uom"
    cursor.execute(query)
    response = []
    for (uom_id, uom_name) in cursor:
        response.append({
            'uom_id': uom_id,
            'uom_name': uom_name
        })
    cursor.close()
    return response
