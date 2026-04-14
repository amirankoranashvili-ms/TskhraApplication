-- enums
CREATE TYPE gender AS ENUM ('MALE', 'FEMALE');
CREATE TYPE kyc_status AS ENUM ('NONE', 'PENDING', 'APPROVED', 'REJECTED');
CREATE TYPE user_status AS ENUM ('ACTIVE', 'SUSPENDED', 'BANNED', 'DELETED');
CREATE TYPE activity_status AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED');
CREATE TYPE business_type AS ENUM ('INDIVIDUAL', 'COMMERCIAL');
CREATE TYPE week_day AS ENUM ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN');
CREATE TYPE call_type AS ENUM ('OUTCALL', 'ONSITE', 'BOTH');
CREATE TYPE booking_status AS ENUM ('AWAITING', 'SCHEDULED', 'REJECTED', 'CANCELLED_BY_BUSINESS', 'CANCELLED_BY_USER', 'COMPLETED');
CREATE TYPE chain_status AS ENUM ('ACTIVE', 'COMPLETED', 'BROKEN');
CREATE TYPE item_condition AS ENUM ('NEW', 'LIKE_NEW', 'USED', 'DAMAGED');
CREATE TYPE item_status AS ENUM ('AVAILABLE', 'HIDDEN', 'TRADED', 'REMOVED');
CREATE TYPE owning_side AS ENUM ('OFFERER', 'RESPONDER');
CREATE TYPE trade_range AS ENUM ('CITY_WIDE', 'COUNTRY_WIDE');
CREATE TYPE trade_status AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'CANCELED', 'COUNTERED', 'EXPIRED', 'COMPLETED');

-- cities
INSERT INTO cities (name, nameKa)
VALUES ('Tbilisi', 'თბილისი'),
       ('Batumi', 'ბათუმი'),
       ('Kutaisi', 'ქუთაისი'),
       ('Rustavi', 'რუსთავი'),
       ('Gori', 'გორი'),
       ('Zugdidi', 'ზუგდიდი'),
       ('Poti', 'ფოთი'),
       ('Khashuri', 'ხაშური'),
       ('Samtredia', 'სამტრედია'),
       ('Senaki', 'სენაკი'),
       ('Zestafoni', 'ზესტაფონი'),
       ('Marneuli', 'მარნეული'),
       ('Telavi', 'თელავი'),
       ('Akhaltsikhe', 'ახალციხე'),
       ('Kobuleti', 'ქობულეთი'),
       ('Ozurgeti', 'ოზურგეთი'),
       ('Chiatura', 'ჭიათურა'),
       ('Mtskheta', 'მცხეთა'),
       ('Borjomi', 'ბორჯომი');

INSERT INTO cities_swap (name)
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
INSERT INTO categories (name)
VALUES ('Legal and Finance'),
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
INSERT INTO categories (parent_id, name)
VALUES
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


-- INDEXES

-- admins
CREATE UNIQUE INDEX idx_admins_email ON admins (email);
CREATE UNIQUE INDEX idx_admins_username ON admins (username);
-- users
CREATE UNIQUE INDEX idx_users_keycloak_id ON users (keycloak_id);
CREATE UNIQUE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_user_status ON users (user_status);
CREATE INDEX idx_users_kyc_status ON users (kyc_status);
-- categories
CREATE INDEX idx_categories_parent_id ON categories (parent_id);
-- cities
CREATE UNIQUE INDEX idx_cities_name ON cities (name);
-- user_verification_requests
CREATE INDEX idx_uvr_user_id ON user_verification_requests (user_id);
CREATE INDEX idx_uvr_resolved_by ON user_verification_requests (resolved_by);
-- CREATE INDEX idx_uvr_status ON user_verification_requests (status); FIXME add staus to schema
-- businesses
CREATE INDEX idx_businesses_user_id ON businesses (user_id);
CREATE INDEX idx_businesses_category_id ON businesses (category_id);
CREATE INDEX idx_businesses_address_id ON businesses (address_id);
CREATE INDEX idx_businesses_activity_status ON businesses (activity_status);
-- addresses
CREATE INDEX idx_addresses_city_id ON addresses (city_id);
-- resources
CREATE INDEX idx_resources_business_id ON resources (business_id);
CREATE INDEX idx_resources_activity_status ON resources (activity_status);
-- services
CREATE INDEX idx_services_business_id ON services (business_id);
CREATE INDEX idx_services_activity_status ON services (activity_status);
-- service_resources
CREATE INDEX idx_service_resources_resource_id ON service_resources (resource_id);
-- business_schedules
CREATE INDEX idx_bs_business_id ON business_schedules (business_id);
-- business_unavailable_schedules
CREATE INDEX idx_bus_business_id ON business_unavailable_schedules (business_id);
-- business_unavailable_onetimes
CREATE INDEX idx_buo_business_id ON business_unavailable_onetimes (business_id);
CREATE INDEX idx_buo_date ON business_unavailable_onetimes (date);
-- bookings
CREATE INDEX idx_bookings_user_id ON bookings (user_id);
CREATE INDEX idx_bookings_service_id ON bookings (service_id);
CREATE INDEX idx_bookings_resource_id ON bookings (resource_id);
CREATE INDEX idx_bookings_booking_date ON bookings (booking_date);
CREATE INDEX idx_bookings_booking_status ON bookings (booking_status);
CREATE INDEX idx_bookings_booked_at ON bookings (booked_at);
CREATE INDEX idx_bookings_status_date ON bookings (booking_status, booking_date);