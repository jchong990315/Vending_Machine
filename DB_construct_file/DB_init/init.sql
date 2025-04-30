USE Vending_Machine;

CREATE TABLE `Inventory` (
    `i_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `item_name` VARCHAR(255) NOT NULL,
    `stock` INT DEFAULT 0,
    `price` DECIMAL(10,2) NOT NULL,
    `threshold` INT NOT NULL,
    `channel` VARCHAR(3) UNIQUE NOT NULL,
    PRIMARY KEY (`i_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10001;

CREATE TABLE `UserProfile` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL,
    `transactions` JSON DEFAULT NULL,
    `total_spent` DECIMAL(10,2) NOT NULL DEFAULT '0.00',
    PRIMARY KEY (`id`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB;

CREATE TABLE `Transactions` (
  `t_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,                  
  `transaction_date` DATETIME NOT NULL,
  `total` DECIMAL(10,2) DEFAULT 0,
  `payment_id` VARCHAR(100) DEFAULT NULL,           
  `payment_status` VARCHAR(50) DEFAULT 'pending',  
  PRIMARY KEY (`t_id`),
  CONSTRAINT `fk_transactions_user`
    FOREIGN KEY (`user_id`) REFERENCES `UserProfile`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10001;

CREATE TABLE `transactions_items` (
    `t_id` INT UNSIGNED NOT NULL,
    `i_id` INT UNSIGNED NOT NULL,
    `item_name` VARCHAR(255) NOT NULL,
    `quantity` INT NOT NULL,
    `price` DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (`t_id`, `i_id`),
    CONSTRAINT `fk_transactions_items_t_id`
        FOREIGN KEY (`t_id`) REFERENCES `Transactions`(`t_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_transactions_items_i_id`
        FOREIGN KEY (`i_id`) REFERENCES `Inventory`(`i_id`)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `Item_Description` (
    `description_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `i_id` INT UNSIGNED NOT NULL,
    `description` TEXT NOT NULL,
    `calories` INT DEFAULT NULL,
    `carbohydrates` DECIMAL(10,2) DEFAULT NULL,
    `allergy_info` TEXT DEFAULT NULL,
    PRIMARY KEY (`description_id`),
    FOREIGN KEY (`i_id`) REFERENCES `Inventory`(`i_id`)
        ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10001;

INSERT INTO Inventory (item_name, stock, price, threshold, channel)
VALUES 
  ('Diet Coke', 100, 2.50, 5, 'A1'),
  ('Coke', 100, 2.50, 5, 'A2'),
  ('Sprite', 50, 2.50, 5, 'A3'),
  ('Dr Pepper', 60, 2.50, 5, 'B1'),
  ('Mt Dew', 50, 3.00, 5, 'B2'),
  ('Water', 80, 1.50, 5, 'B3');

INSERT INTO Item_Description (i_id, description, calories, carbohydrates, allergy_info)
VALUES
  (10001, 'A refreshing diet soda with a hint of citrus flavor.', 0, 0.0, 'Contains caffeine.'),
  (10002, 'A classic soda with a perfect balance of sweetness and carbonation.', 140, 39.0, 'Contains caffeine.'),
  (10003, 'A crisp, lemon-lime soda that is always refreshing.', 150, 41.0, 'Contains caffeine.'),
  (10004, 'A bold, sweet soda with a unique blend of flavors.', 150, 42.0, 'Contains caffeine.'),
  (10005, 'A citrus-flavored soda with a distinct and zesty taste.', 170, 46.0, 'Contains caffeine.'),
  (10006, 'A simple and hydrating beverage, perfect for any time of day.', 0, 0.0, 'No allergens.');
