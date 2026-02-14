import mysql.connector
from mysql.connector import Error

# Database Configuration
DB_CONFIG = {
    'host': '141.209.241.57',
    'user': 'vempa3s',
    'password': 'mypass',  
    'database': 'BIS698Fall25_GRP7',
    'port': 3306,
    'autocommit': True,
    'raise_on_warnings': False
}


def get_db_connection():
    """
    Establish and return a database connection
    
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
        
    Raises:
        Error: If connection fails
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        raise


def create_database_if_not_exists():
    """
    Create the database if it doesn't exist
    """
    try:
        config = DB_CONFIG.copy()
        config.pop('database')
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}"
        )
        print(f"Database '{DB_CONFIG['database']}' created successfully or already exists.")
        
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error creating database: {e}")
        raise


def close_connection(connection):
    """
    Safely close database connection
    
    Args:
        connection: MySQL connection object
    """
    if connection and connection.is_connected():
        connection.close()


# Application Constants
APP_TITLE = "Donation Management System"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# User Roles
ROLE_ADMIN = "admin"
ROLE_DONOR = "donor"

# Campaign Status
CAMPAIGN_ACTIVE = "active"
CAMPAIGN_COMPLETED = "completed"
CAMPAIGN_PAUSED = "paused"

# Donation Categories
CATEGORIES = [
    "Medical",
    "Education",
    "Wildlife",
    "Environment",
    "Disaster Relief",
    "Food Security",
    "Clean Water",
    "Mental Health",
    "Infrastructure",
    "Other"
]