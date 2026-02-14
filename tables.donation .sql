-- ============================================================
-- Donation Management System - Database Setup Script
-- ============================================================
-- This script creates all required tables for the donation
-- management system application
-- ============================================================

-- Users table
-- Stores information about admin users and donors
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    role ENUM('admin', 'donor') DEFAULT 'donor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Campaigns table
-- Stores information about fundraising campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description LONGTEXT,
    goal_amount DECIMAL(10, 2) NOT NULL,
    current_amount DECIMAL(10, 2) DEFAULT 0,
    category VARCHAR(100),
    status ENUM('active', 'completed', 'paused') DEFAULT 'active',
    created_by INT NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Donations table
-- Stores donation records from donors to campaigns
CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    campaign_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    message LONGTEXT,
    donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    INDEX idx_donor_id (donor_id),
    INDEX idx_campaign_id (campaign_id),
    INDEX idx_donation_date (donation_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Preferences table
-- Stores notification and communication preferences for users
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    email_notifications BOOLEAN DEFAULT TRUE,
    monthly_reports BOOLEAN DEFAULT TRUE,
    impact_updates BOOLEAN DEFAULT TRUE,
    newsletter BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Sample Data Insertion (Optional)
-- Uncomment the sections below to insert test data
-- ============================================================

-- Insert sample admin user
INSERT INTO users (first_name, last_name, email, password_hash, phone, address, role)
VALUES ('Admin', 'User', 'admin@donation.com', '[HASHED_PASSWORD]', '1234567890', '123 Admin St', 'admin');

-- Insert sample donor users
INSERT INTO users (first_name, last_name, email, password_hash, phone, address, role)
VALUES 
('John', 'Doe', 'john@donation.com', '[HASHED_PASSWORD]', '+1-555-0001', '123 Main St', 'donor'),
('Jane', 'Smith', 'jane@donation.com', '[HASHED_PASSWORD]', '+1-555-0002', '456 Oak Ave', 'donor'),
('Mike', 'Johnson', 'mike@donation.com', '[HASHED_PASSWORD]', '+1-555-0003', '789 Pine Rd', 'donor');

-- Insert sample campaigns
INSERT INTO campaigns (title, description, goal_amount, category, created_by)
VALUES 
('Clean Water Initiative', 'Bringing clean drinking water to rural villages', 50000, 'Clean Water', 1),
('Education for All', 'Building schools and providing educational resources', 75000, 'Education', 1),
('Medical Equipment', 'Funding essential medical equipment for hospitals', 60000, 'Medical', 1),
('Disaster Relief Fund', 'Emergency aid for disaster-affected communities', 100000, 'Disaster Relief', 1);

-- Insert sample donations
INSERT INTO donations (donor_id, campaign_id, amount, message)
VALUES 
(2, 1, 500, 'Great cause!'),
(3, 1, 1000, ''),
(4, 2, 750, 'Love education initiatives'),
(2, 2, 250, ''),
(3, 3, 2000, 'Important work'),
(4, 3, 500, ''),
(2, 4, 1500, 'Disaster relief');