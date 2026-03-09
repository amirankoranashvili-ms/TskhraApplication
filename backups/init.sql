-- enums
CREATE TYPE gender AS ENUM ('MALE', 'FEMALE');
CREATE TYPE kyc_status AS ENUM ('NONE', 'PENDING', 'APPROVED', 'REJECTED');
CREATE TYPE user_status AS ENUM ('ACTIVE', 'SUSPENDED', 'BANNED', 'DELETED');
CREATE TYPE activity_status AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED');
CREATE TYPE business_type AS ENUM ('INDIVIDUAL', 'COMMERCIAL');
CREATE TYPE week_day AS ENUM ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN');
CREATE TYPE call_type AS ENUM ('OUTCALL', 'ONSITE', 'BOTH');
CREATE TYPE booking_type AS ENUM ('AWAITING', 'SCHEDULED', 'REJECTED', 'CANCELLED_BY_BUSINESS', 'CANCELLED_BY_USER', 'COMPLETED');

-- cities
INSERT INTO cities (name)
VALUES ('Tbilisi'),
       ('Batumi'),
       ('Kutaisi'),
       ('Rustavi'),
       ('Gori'),
       ('Zugdidi'),
       ('Poti'),
       ('Khashuri'),
       ('Samtredia'),
       ('Senaki'),
       ('Zestafoni'),
       ('Marneuli'),
       ('Telavi'),
       ('Akhaltsikhe'),
       ('Kobuleti'),
       ('Ozurgeti'),
       ('Chiatura'),
       ('Mtskheta'),
       ('Borjomi');

-- categories
-- ნაბიჯი 1: ვამატებთ მხოლოდ მთავარ (მშობელ) კატეგორიებს. 
-- id-ს ბაზა თავისით მიანიჭებს.
INSERT INTO categories (name) VALUES
                                ('Legal and Finance'),
                                ('Beauty and Personal Care'),
                                ('Health'),
                                ('Home Services'),
                                ('Cleaning'),
                                ('Auto Services'),
                                ('Education'),
                                ('Fitness and Sports'),
                                ('Pets'),
                                ('Events'),
                                ('IT and Technology'),
                                ('Transport');
-- ნაბიჯი 2: ვამატებთ ქვეკატეგორიებს.
-- parent_id ავტომატურად მოიძებნება მთავარი კატეგორიის სახელის მიხედვით.
INSERT INTO categories (parent_id, name) VALUES
-- Legal and Finance
((SELECT id FROM categories WHERE name = 'Legal and Finance'), 'Legal Services'),
((SELECT id FROM categories WHERE name = 'Legal and Finance'), 'Notary Services'),
((SELECT id FROM categories WHERE name = 'Legal and Finance'), 'Accounting and Audit'),
((SELECT id FROM categories WHERE name = 'Legal and Finance'), 'Business Consulting'),
-- Beauty and Personal Care
((SELECT id FROM categories WHERE name = 'Beauty and Personal Care'), 'Hair Care Services'),
((SELECT id FROM categories WHERE name = 'Beauty and Personal Care'), 'Nail Care Services'),
((SELECT id FROM categories WHERE name = 'Beauty and Personal Care'), 'Aesthetic Cosmetology'),
((SELECT id FROM categories WHERE name = 'Beauty and Personal Care'), 'Makeup Services'),
((SELECT id FROM categories WHERE name = 'Beauty and Personal Care'), 'Spa and Relaxation Procedures'),
-- Health
((SELECT id FROM categories WHERE name = 'Health'), 'Physiotherapy and Rehabilitation'),
((SELECT id FROM categories WHERE name = 'Health'), 'Psychological Counseling'),
((SELECT id FROM categories WHERE name = 'Health'), 'Nursing and Ambulatory Care'),
((SELECT id FROM categories WHERE name = 'Health'), 'Dietetics and Nutrition'),
-- Home Services
((SELECT id FROM categories WHERE name = 'Home Services'), 'Plumbing'),
((SELECT id FROM categories WHERE name = 'Home Services'), 'Electrical Works'),
((SELECT id FROM categories WHERE name = 'Home Services'), 'HVAC Services'),
((SELECT id FROM categories WHERE name = 'Home Services'), 'Home Appliance Repair'),
((SELECT id FROM categories WHERE name = 'Home Services'), 'Disinfection Services'),
-- Cleaning
((SELECT id FROM categories WHERE name = 'Cleaning'), 'Residential Cleaning'),
((SELECT id FROM categories WHERE name = 'Cleaning'), 'Commercial Cleaning'),
((SELECT id FROM categories WHERE name = 'Cleaning'), 'Dry Cleaning (Furniture/Carpets)'),
((SELECT id FROM categories WHERE name = 'Cleaning'), 'Facade and Window Cleaning'),
-- Auto Services
((SELECT id FROM categories WHERE name = 'Auto Services'), 'Vehicle Maintenance'),
((SELECT id FROM categories WHERE name = 'Auto Services'), 'Chassis and Suspension Repair'),
((SELECT id FROM categories WHERE name = 'Auto Services'), 'Auto Electrics and Diagnostics'),
((SELECT id FROM categories WHERE name = 'Auto Services'), 'Car Wash and Polishing'),
-- Education
((SELECT id FROM categories WHERE name = 'Education'), 'Foreign Language Teaching'),
((SELECT id FROM categories WHERE name = 'Education'), 'Exact and Natural Sciences'),
((SELECT id FROM categories WHERE name = 'Education'), 'Music and Arts Education'),
((SELECT id FROM categories WHERE name = 'Education'), 'Professional Training and Retraining'),
-- Fitness and Sports
((SELECT id FROM categories WHERE name = 'Fitness and Sports'), 'Personal Trainer and Fitness'),
((SELECT id FROM categories WHERE name = 'Fitness and Sports'), 'Wellness Exercises'),
((SELECT id FROM categories WHERE name = 'Fitness and Sports'), 'Swimming Pool Services'),
((SELECT id FROM categories WHERE name = 'Fitness and Sports'), 'Martial Arts Training'),
-- Pets
((SELECT id FROM categories WHERE name = 'Pets'), 'Veterinary Services'),
((SELECT id FROM categories WHERE name = 'Pets'), 'Pet Grooming and Care'),
((SELECT id FROM categories WHERE name = 'Pets'), 'Pet Training and Behavior Correction'),
((SELECT id FROM categories WHERE name = 'Pets'), 'Pet Boarding'),
-- Events
((SELECT id FROM categories WHERE name = 'Events'), 'Photo and Video Production'),
((SELECT id FROM categories WHERE name = 'Events'), 'Event Planning and Organization'),
((SELECT id FROM categories WHERE name = 'Events'), 'Musical and Visual Entertainment'),
((SELECT id FROM categories WHERE name = 'Events'), 'Festive Decoration and Floristry'),
((SELECT id FROM categories WHERE name = 'Events'), 'Catering'),
-- IT and Technology
((SELECT id FROM categories WHERE name = 'IT and Technology'), 'Computer Hardware Services'),
((SELECT id FROM categories WHERE name = 'IT and Technology'), 'Software and Web Services'),
((SELECT id FROM categories WHERE name = 'IT and Technology'), 'Mobile Device Repair'),
((SELECT id FROM categories WHERE name = 'IT and Technology'), 'Network Infrastructure Installation'),
-- Transport
((SELECT id FROM categories WHERE name = 'Transport'), 'Freight Transport and Logistics'),
((SELECT id FROM categories WHERE name = 'Transport'), 'Passenger Transportation'),
((SELECT id FROM categories WHERE name = 'Transport'), 'Courier and Postal Services'),
((SELECT id FROM categories WHERE name = 'Transport'), 'Special Equipment Services');