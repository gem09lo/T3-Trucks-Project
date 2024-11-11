SET search_path TO gem_lo_schema;

DROP TABLE IF EXISTS FACT_Transaction;
DROP TABLE IF EXISTS DIM_Payment_Method;
DROP TABLE IF EXISTS DIM_Truck;



CREATE TABLE DIM_Payment_Method (
    payment_method_id INT UNIQUE NOT NULL,
    payment_method VARCHAR(100) UNIQUE NOT NULL,
    PRIMARY KEY (payment_method_id)
);

CREATE TABLE DIM_Truck (
    truck_id INT UNIQUE NOT NULL,
    truck_name VARCHAR(100) NOT NULL,
    truck_description VARCHAR(300),
    has_card_reader BOOLEAN NOT NULL,
    fsa_rating SMALLINT NOT NULL,
    PRIMARY KEY (truck_id)
);

CREATE TABLE FACT_Transaction (
    transaction_id INT GENERATED ALWAYS AS IDENTITY,
    at TIMESTAMP default CURRENT_TIMESTAMP,
    total FLOAT NOT NULL,
    payment_method_id INT NOT NULL, 
    truck_id INT NOT NULL, 
    PRIMARY KEY (transaction_id),
    FOREIGN KEY (truck_id) REFERENCES DIM_Truck(truck_id),
    FOREIGN KEY (payment_method_id) REFERENCES DIM_Payment_Method(payment_method_id)
);


INSERT INTO DIM_Payment_Method (payment_method_id, payment_method)
VALUES 
(1, 'card'),
(2, 'cash');

INSERT INTO DIM_Truck (truck_id, truck_name, truck_description, has_card_reader, fsa_rating)
VALUES 
(1, 'Burrito Madness', 'An authentic taste of Mexico.', '1', 4),
(2, 'Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', '1', 2),
(3, 'Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', '1', 5),
(4, 'Hartmann''s Jellied Eels', 'A taste of history with this classic English dish.', '1', 4),
(5, 'Yoghurt Heaven', 'All the great tastes, but only some of the calories!', '1', 4),
(6, 'SuperSmoothie', 'Pick any fruit or vegetable, and we''ll make you a delicious, healthy, multi-vitamin shake. Live well; live wild.', '0', 3);
