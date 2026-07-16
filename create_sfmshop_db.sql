-- создание таблиц
CREATE TABLE users (
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
email VARCHAR(100) UNIQUE
);

CREATE TABLE products(
id SERIAL PRIMARY KEY,
name VARCHAR(200) NOT NULL,
price DECIMAL(10,2),
quantity INTEGER DEFAULT 0
);

CREATE TABLE orders(
id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id),
total DECIMAL(10,2) NOT NULL,
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items(
id SERIAL PRIMARY KEY,
order_id INTEGER REFERENCES orders(id),
product_id INTEGER REFERENCES products(id),
quantity INTEGER
);

-- добавление тестовых данных

INSERT INTO users (name, email) VALUES
('Vitalii', 'vitalii@test.com'),
('Ivan', 'ivan@test.com'),
('Ekaterina', 'kate@test.com');

INSERT INTO products (name, price, quantity) VALUES
('Ноутбук', 50000, 10),
('Мышь', 1500, 15),
('Клавиатура', 5000, 12),
('Компьютерный стол', 7000, 8),
('Зарядное устройство', 2000, 20);

INSERT INTO orders (user_id, total) VALUES
(1, 62000),
(2, 15500);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 3, 1),
(1, 4, 1),
(2, 2, 1),
(2, 3, 1),
(2, 4, 1),
(2, 5, 1);