"""
Main Application Entry Point
Initializes database, creates tables, and launches the application
"""

import sys
import mysql.connector
from mysql.connector import Error

from config import (
    get_db_connection, create_database_if_not_exists, 
    close_connection, DB_CONFIG
)
from login_register_screens import AuthScreen


def create_tables():
    """
    Create all required database tables
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Users table
        users_table = """
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
        """
        
        # Campaigns table
        campaigns_table = """
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
        """
        
        # Donations table
        donations_table = """
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
        """
        
        # User preferences table
        preferences_table = """
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            email_notifications BOOLEAN DEFAULT TRUE,
            monthly_reports BOOLEAN DEFAULT TRUE,
            impact_updates BOOLEAN DEFAULT TRUE,
            newsletter BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Execute table creation queries
        print("Creating database tables...")
        cursor.execute(users_table)
        print("✓ Users table created")
        
        cursor.execute(campaigns_table)
        print("✓ Campaigns table created")
        
        cursor.execute(donations_table)
        print("✓ Donations table created")
        
        cursor.execute(preferences_table)
        print("✓ User preferences table created")
        
        close_connection(connection)
        print("\n✓ All tables created successfully!\n")
        
    except Error as e:
        print(f"\n✗ Error creating tables: {e}\n")
        raise


def insert_sample_data():
    """
    Insert sample data for testing
    """
    try:
        from utils import create_user, create_campaign, create_donation, ROLE_ADMIN, ROLE_DONOR
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            print("Sample data already exists, skipping insertion.\n")
            close_connection(connection)
            return
        
        print("Inserting sample data...")
        
        # Create sample admin user
        success, msg, admin_id = create_user(
            "Admin", "User", "admin@donation.com", "admin123",
            phone="1234567890", address="123 Admin St", role=ROLE_ADMIN
        )
        if success:
            print(f"✓ Admin user created (ID: {admin_id})")
        
        # Create sample donor users
        donors = [
            ("John", "Doe", "john@donation.com", "john123", "+1-555-0001", "123 Main St"),
            ("Jane", "Smith", "jane@donation.com", "jane123", "+1-555-0002", "456 Oak Ave"),
            ("Mike", "Johnson", "mike@donation.com", "mike123", "+1-555-0003", "789 Pine Rd"),
        ]
        
        donor_ids = []
        for fname, lname, email, pwd, phone, address in donors:
            success, msg, donor_id = create_user(
                fname, lname, email, pwd, phone, address, role=ROLE_DONOR
            )
            if success:
                donor_ids.append(donor_id)
                print(f"✓ Donor user created: {fname} {lname} (ID: {donor_id})")
        
        # Create sample campaigns
        campaigns_data = [
            ("Clean Water Initiative", "Bringing clean drinking water to rural villages", 50000, "Clean Water", admin_id),
            ("Education for All", "Building schools and providing educational resources", 75000, "Education", admin_id),
            ("Medical Equipment", "Funding essential medical equipment for hospitals", 60000, "Medical", admin_id),
            ("Disaster Relief Fund", "Emergency aid for disaster-affected communities", 100000, "Disaster Relief", admin_id),
        ]
        
        campaign_ids = []
        for title, desc, goal, category, created_by in campaigns_data:
            success, msg, campaign_id = create_campaign(title, desc, goal, category, created_by)
            if success:
                campaign_ids.append(campaign_id)
                print(f"✓ Campaign created: {title} (ID: {campaign_id})")
        
        # Create sample donations
        donations_data = [
            (donor_ids[0], campaign_ids[0], 500, "Great cause!"),
            (donor_ids[1], campaign_ids[0], 1000, ""),
            (donor_ids[2], campaign_ids[1], 750, "Love education initiatives"),
            (donor_ids[0], campaign_ids[1], 250, ""),
            (donor_ids[1], campaign_ids[2], 2000, "Important work"),
            (donor_ids[2], campaign_ids[2], 500, ""),
            (donor_ids[0], campaign_ids[3], 1500, "Disaster relief"),
        ]
        
        for donor_id, campaign_id, amount, message in donations_data:
            success, msg, donation_id = create_donation(donor_id, campaign_id, amount, message)
            if success:
                print(f"✓ Donation created: ${amount} to campaign {campaign_id}")
        
        print("\n✓ Sample data inserted successfully!\n")
        
    except Exception as e:
        print(f"\n✗ Error inserting sample data: {e}\n")


def verify_connection():
    """
    Verify database connection
    
    Returns:
        bool: True if connection successful
    """
    try:
        connection = get_db_connection()
        if connection.is_connected():
            print("✓ Database connection successful")
            close_connection(connection)
            return True
    except Error as e:
        print(f"✗ Database connection failed: {e}")
        return False


def initialize_application():
    """
    Initialize application by setting up database and tables
    
    Returns:
        bool: True if initialization successful
    """
    print("=" * 50)
    print("Donation Management System - Initialization")
    print("=" * 50 + "\n")
    
    try:
        # Create database
        print("Step 1: Creating database...")
        create_database_if_not_exists()
        print("✓ Database created/verified\n")
        
        # Verify connection
        print("Step 2: Verifying database connection...")
        if not verify_connection():
            print("\n✗ Failed to connect to database")
            print("Please check your database credentials in config.py")
            return False
        print()
        
        # Create tables
        print("Step 3: Creating database tables...")
        create_tables()
        
        # Insert sample data
        print("Step 4: Inserting sample data...")
        insert_sample_data()
        
        print("=" * 50)
        print("✓ Initialization complete!")
        print("=" * 50)
        print("\nApplication is ready to launch!\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Initialization failed: {e}")
        print("Please check your database configuration.")
        return False


def launch_application():
    """
    Launch the donation management system application
    """
    try:
        print("\nLaunching Donation Management System...\n")
        app = AuthScreen()
        app.mainloop()
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Initialize application
    if initialize_application():
        # Launch the application
        launch_application()
    else:
        print("\nFailed to initialize application. Exiting...")
        sys.exit(1)