BEGIN;

DROP TABLE IF EXISTS inventory;

CREATE TABLE inventory (
    id integer PRIMARY KEY,
    product text NOT NULL,
    quantity integer NOT NULL,
    price integer NOT NULL
);

INSERT INTO inventory (id, product, quantity, price) VALUES
    (1, 'keyboard', 3, 5000),
    (2, 'mouse', 7, 1500),
    (3, 'monitor', 0, 25000),
    (4, 'webcam', 2, 7000);

COMMIT;
