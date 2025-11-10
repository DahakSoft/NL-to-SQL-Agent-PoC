-- This file defines the database schema that the AI agent will use to generate SQL queries.

-- Products table: stores core information about each product.
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL
);

-- Stock levels table: tracks the quantity of each product in different warehouses.
CREATE TABLE stock_levels (
    product_id INT,
    quantity INT NOT NULL,
    warehouse_name VARCHAR(50),
    FOREIGN KEY (product_id) REFERENCES products(id)
);