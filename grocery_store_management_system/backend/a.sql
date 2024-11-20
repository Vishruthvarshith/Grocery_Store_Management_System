-- Create the database
CREATE DATABASE grocery_store;

-- Use the grocery_store database
USE grocery_store;

-- Table for storing unit of measurement (UOM) information
CREATE TABLE uom (
    uom_id INT AUTO_INCREMENT PRIMARY KEY,
    uom_name VARCHAR(50) NOT NULL
);

-- Table for storing product information
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    uom_id INT NOT NULL,
    price_per_unit DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (uom_id) REFERENCES uom(uom_id) ON DELETE CASCADE
);

-- Table for storing order information
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    datetime DATETIME NOT NULL
);

-- Table for storing order details, linked to orders and products
CREATE TABLE order_details (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);




--INSERT INTO UOM
INSERT INTO uom (uom_id, uom_name) VALUES (1, 'each');
INSERT INTO uom (uom_id, uom_name) VALUES (2, 'kg');
INSERT INTO uom (uom_id, uom_name) VALUES (3, 'litre');
INSERT INTO uom (uom_id, uom_name) VALUES (4, 'dozen');
INSERT INTO uom (uom_id, uom_name) VALUES (5, 'pack');


--DELETE FROM UOM
-- Deleting UOM with uom_id = 1 (each)
DELETE FROM uom 
WHERE uom_id = 1;

-- Deleting UOM with uom_id = 2 (kg)
DELETE FROM uom 
WHERE uom_id = 2;

-- Deleting UOM with uom_id = 3 (litre)
DELETE FROM uom 
WHERE uom_id = 3;

-- Deleting UOM with uom_id = 4 (dozen)
DELETE FROM uom 
WHERE uom_id = 4;

-- Deleting UOM with uom_id = 5 (pack)
DELETE FROM uom 
WHERE uom_id = 5;

-- Inserting a new product
INSERT INTO products (name, uom_id, price_per_unit)
VALUES ('Apple', 1, 2.50), 
       ('Milk', 2, 1.20), 
       ('Pen', 3, 0.50), 
       ('Shampoo', 4, 5.99);
-- Deleting a product by product_id

DELETE FROM products 
WHERE product_id = 1;  -- Replace with the actual product_id to delete


-- Inserting a new order
INSERT INTO orders (customer_name, total, datetime)
VALUES ('John Doe', 25.50, '2024-11-15 10:00:00');
       ('Jane Smith', 15.75, '2024-11-15 12:00:00');


-- Deleting an order by order_id
DELETE FROM orders 
WHERE order_id = 1;  -- Replace with the actual order_id to delete


-- Inserting order details for an order
INSERT INTO order_details (order_id, product_id, quantity, total_price)
VALUES (1, 1, 5, 12.50),  -- Order ID 1, Product ID 1 (Apple), quantity 5, total_price 12.50
       (1, 2, 3, 3.60),   -- Order ID 1, Product ID 2 (Milk), quantity 3, total_price 3.60
       (2, 3, 4, 2.00);   -- Order ID 2, Product ID 3 (Pen), quantity 4, total_price 2.00

-- Deleting order details by order_detail_id
DELETE FROM order_details 
WHERE order_detail_id = 1;  -- Replace with the actual order_detail_id to delete







--View Table
CREATE VIEW view_products_with_uom AS
SELECT 
    p.product_id,
    p.name AS product_name,
    p.price_per_unit,
    u.uom_name AS unit_of_measurement
FROM 
    products p
JOIN 
    uom u ON p.uom_id = u.uom_id;

CREATE VIEW view_order_summary AS
SELECT 
    o.order_id,
    o.customer_name,
    o.total AS total_amount,
    o.datetime AS order_date
FROM 
    orders o;

CREATE VIEW view_order_details_with_products AS
SELECT 
    od.order_detail_id,
    od.order_id,
    p.name AS product_name,
    od.quantity,
    od.total_price
FROM 
    order_details od
JOIN 
    products p ON od.product_id = p.product_id;


CREATE VIEW view_total_sales_by_product AS
SELECT 
    p.product_id,
    p.name AS product_name,
    SUM(od.total_price) AS total_sales
FROM 
    order_details od
JOIN 
    products p ON od.product_id = p.product_id
GROUP BY 
    p.product_id, p.name;

CREATE VIEW view_orders_by_customer AS
SELECT 
    o.customer_name,
    o.order_id,
    o.total AS order_total,
    o.datetime AS order_date
FROM 
    orders o
ORDER BY 
    o.customer_name, o.datetime;


--Triggers
CREATE TABLE IF NOT EXISTS order_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
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




CREATE TABLE IF NOT EXISTS product_back_up (
    product_id INT,
    name VARCHAR(100),
    uom_id INT,
    price_per_unit DECIMAL(10, 2),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER before_product_delete
BEFORE DELETE ON products
FOR EACH ROW
BEGIN
    INSERT INTO product_back_up (product_id, name, uom_id, price_per_unit, deleted_at)
    VALUES (OLD.product_id, OLD.name, OLD.uom_id, OLD.price_per_unit, NOW());
END;


--Store Procdure

CREATE DEFINER=`root`@`localhost` PROCEDURE `AddProduct`(
    IN p_name VARCHAR(100),
    IN p_uom_id INT,
    IN p_price_per_unit DECIMAL(10, 2)
)
BEGIN
    INSERT INTO products (name, uom_id, price_per_unit)
    VALUES (p_name, p_uom_id, p_price_per_unit);
END


CREATE DEFINER=`root`@`localhost` PROCEDURE `CreateOrder`(
    IN p_customer_name VARCHAR(100),
    IN p_order_datetime DATETIME,
    INOUT p_order_id INT
)
BEGIN
    INSERT INTO orders (customer_name, total, datetime)
    VALUES (p_customer_name, 0, p_order_datetime);

    SET p_order_id = LAST_INSERT_ID();
END


CREATE DEFINER=`root`@`localhost` PROCEDURE `DeleteProduct`(
    IN p_product_id INT
)
BEGIN
    DELETE FROM products WHERE product_id = p_product_id;
END


CREATE DEFINER=`root`@`localhost` PROCEDURE `UpdateProduct`(
    IN p_product_id INT,
    IN p_new_name VARCHAR(100),
    IN p_new_uom_id INT,
    IN p_new_price_per_unit DECIMAL(10, 2)
)
BEGIN
    UPDATE products
    SET 
        name = p_new_name,
        uom_id = p_new_uom_id,
        price_per_unit = p_new_price_per_unit
    WHERE 
        product_id = p_product_id;
END


--Example

CALL UpdateProduct(1, 'Organic Onion', 2, 3.99);



--Joint Operation

SELECT 
    od.order_detail_id,
    o.customer_name,
    o.datetime,
    p.name AS product_name,
    p.price_per_unit,
    od.quantity,
    od.total_price
FROM 
    order_details od
JOIN 
    orders o ON od.order_id = o.order_id
JOIN 
    products p ON od.product_id = p.product_id



SELECT 
    od.order_detail_id,
    o.customer_name,
    o.datetime AS order_datetime,
    p.name AS product_name,
    u.uom_name AS unit_of_measurement,
    p.price_per_unit,
    od.quantity,
    od.total_price
FROM 
    order_details od
JOIN 
    orders o ON od.order_id = o.order_id
JOIN 
    products p ON od.product_id = p.product_id
JOIN 
    uom u ON p.uom_id = u.uom_id;


--Nested Queries:

--Get the total value of each order (sum of all order details)
--This query uses a subquery to calculate the total value of each order by summing the total_price in the order_details table

SELECT o.order_id, o.customer_name, o.datetime, 
    (SELECT SUM(od.total_price) 
     FROM order_details od 
     WHERE od.order_id = o.order_id) AS order_total
FROM orders o;

--Get products sold in a specific order This query retrieves the details of the products in a given order,
-- including product name, quantity, and total price.
SELECT o.order_id, o.customer_name, p.name AS product_name, 
    (SELECT od.quantity 
     FROM order_details od 
     WHERE od.order_id = o.order_id AND od.product_id = p.product_id) AS quantity,
    (SELECT od.total_price 
     FROM order_details od 
     WHERE od.order_id = o.order_id AND od.product_id = p.product_id) AS total_price
FROM orders o
JOIN products p;

--Get the most expensive product sold in a specific order This query uses a subquery to
-- find the most expensive product sold in a specific order (e.g., order_id = 1).
SELECT o.customer_name, o.order_id, 
    (SELECT p.name 
     FROM products p
     JOIN order_details od ON p.product_id = od.product_id
     WHERE od.order_id = o.order_id
     ORDER BY p.price_per_unit DESC LIMIT 1) AS most_expensive_product
FROM orders o
WHERE o.order_id = 1;
--Get the customer who spent the most on a single order This query calculates the total spending for each order and 
--uses a subquery to find the order with the highest total value.

--Aggregated Queries:

--Get the total value of each order (sum of all order details)
--This query aggregates the total value of each order by summing up the total_price for each order in the order_details table.

SELECT o.order_id, o.customer_name, o.datetime, SUM(od.total_price) AS order_total
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY o.order_id;

--Get the total quantity and total price of each product sold
--This query aggregates the total quantity sold and total sales for each product across all orders.

SELECT p.product_id, p.name, SUM(od.quantity) AS total_quantity, SUM(od.total_price) AS total_sales
FROM products p
JOIN order_details od ON p.product_id = od.product_id
GROUP BY p.product_id;

--Get the total sales per unit of measurement (UOM)
--This query calculates the total sales (total price) for each unit of measurement (UOM).
SELECT u.uom_name, SUM(od.total_price) AS total_sales
FROM uom u
JOIN products p ON u.uom_id = p.uom_id
JOIN order_details od ON p.product_id = od.product_id
GROUP BY u.uom_name;

--Get the total revenue per day
--This query aggregates the total revenue per day by summing the total_price of all orders placed on each day.
SELECT DATE(o.datetime) AS order_date, SUM(od.total_price) AS daily_revenue
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY DATE(o.datetime)
ORDER BY order_date;



