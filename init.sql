DROP DATABASE IF EXISTS `WashWorld`;

CREATE TABLE `cars` (
  `car_id` char(32) PRIMARY KEY NOT NULL,
  `user_id` CHAR(32) NOT NULL,
  `car_license_plate` varchar(12) NOT NULL
);

CREATE TABLE `locations` (
  `location_id` char(32) PRIMARY KEY NOT NULL,
  `location_address` varchar(255) NOT NULL,
  `location_zipcode` varchar(12) NOT NULL,
  `location_coordinate_x` decimal(9,6) NOT NULL,
  `location_coordinate_y` decimal(9,6) NOT NULL,
  `location_open_hours` varchar(50) NOT NULL,
  `location_region` varchar(50) NOT NULL
);

CREATE TABLE `location_services` (
  `location_service_id` char(32) PRIMARY KEY NOT NULL,
  `location_id` char(32),
  `location_service_status` varchar(50) NOT NULL
);

CREATE TABLE `location_equipment` (
  `location_equipment_id` char(32) PRIMARY KEY NOT NULL,
  `location_id` char(32),
  `location_equipment_type` varchar(50) NOT NULL,
  `location_equipment_number` int NOT NULL,
  `location_equipment_status` varchar(50) NOT NULL,
  `location_equipment_max_height` float NOT NULL,
  `location_equipment_max_width` float NOT NULL
);

CREATE TABLE `subscriptions` (
  `subscription_id` char(32) PRIMARY KEY NOT NULL,
  `product_id` char(32),
  `subscriptions_name` decimal(10,2) NOT NULL,
  `subscriptions_price` decimal(10,2) NOT NULL,
  `subscriptions_status` varchar(20) NOT NULL,
  `subscriptions_start_date` bigint NOT NULL,
  `subscriptions_end_date` bigint NOT NULL,
  `subscriptions_next_billing_date` bigint NOT NULL
);

CREATE TABLE `products` (
  `product_id` char(32) PRIMARY KEY NOT NULL,
  `car_id` char(32),
  `product_name` varchar(50) NOT NULL,
  `product_price` decimal(10,2) NOT NULL,
  `product_category` varchar(100) NOT NULL
);

CREATE TABLE `users` (
  `user_id` char(32) PRIMARY KEY NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `user_password_hashed` varchar(255) NOT NULL,
  `user_firstname` varchar(50) NOT NULL,
  `user_lastname` varchar(50) NOT NULL,
  `user_phone` varchar(20) NOT NULL,
  `user_created_at` bigint NOT NULL,
  `user_updated_at` bigint NOT NULL,
  `user_deleted_at` bigint,
  `user_verification_key` char(32) NOT NULL,
  `user_verified_at` bigint NOT NULL,
  `user_reset_password` char(75)
);

CREATE TABLE `user_credit` (
  `user_credit_id` char(32) PRIMARY KEY NOT NULL,
  `user_credit_amount` decimal(10,2) NOT NULL,
  `user_id` char(32),
  `product_id` char(32)
);

CREATE TABLE `offers` (
  `offer_id` char(32) PRIMARY KEY NOT NULL,
  `product_id` char(32),
  `offer_description` varchar(255) NOT NULL,
  `offer_discount_percentage` decimal(5,2) NOT NULL,
  `offer_start_date` bigint NOT NULL,
  `offer_end_date` bigint NOT NULL
);

CREATE TABLE `wash_log` (
  `wash_log_id` char(32) PRIMARY KEY NOT NULL,
  `car_id` char(32),
  `location_id` char(32),
  `wash_log_start_time` bigint NOT NULL
);

ALTER TABLE `cars` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

ALTER TABLE `location_services` ADD FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`);

ALTER TABLE `location_equipment` ADD FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`);

ALTER TABLE `subscriptions` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`car_id`);

ALTER TABLE `user_credit` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

ALTER TABLE `user_credit` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

ALTER TABLE `offers` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

ALTER TABLE `wash_log` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`car_id`);

ALTER TABLE `wash_log` ADD FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`);