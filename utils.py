
import re
import bcrypt
from datetime import datetime
from config import get_db_connection, close_connection, ROLE_DONOR, ROLE_ADMIN, DB_CONFIG

# ==================== PASSWORD HASHING ====================

def hash_password(password):
    """
    Hash password using bcrypt
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """
    Verify password against hash
    
    Args:
        password (str): Plain text password to verify
        hashed_password (str): Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


# ==================== VALIDATION FUNCTIONS ====================

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email:
        return False, "Email is required"
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, "Valid email"


def validate_password(password):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 50:
        return False, "Password must be less than 50 characters"
    
    return True, "Valid password"


def validate_name(name, field_name="Name"):
    """
    Validate name format
    
    Args:
        name (str): Name to validate
        field_name (str): Field name for error messages
        
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    if not name or not name.strip():
        return False, f"{field_name} is required"
    
    if len(name) < 2:
        return False, f"{field_name} must be at least 2 characters"
    
    if len(name) > 50:
        return False, f"{field_name} must be less than 50 characters"
    
    return True, f"Valid {field_name.lower()}"


def validate_phone(phone):
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    if not phone:
        return True, "Phone is optional"
    
    # Remove common separators
    cleaned = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    if not cleaned.isdigit() or len(cleaned) < 10:
        return False, "Invalid phone number format"
    
    return True, "Valid phone number"


def validate_amount(amount):
    """
    Validate donation amount
    
    Args:
        amount (float/str): Amount to validate
        
    Returns:
        tuple: (bool, str, float) - (is_valid, message, amount_value)
    """
    try:
        amount_float = float(amount)
        
        if amount_float <= 0:
            return False, "Amount must be greater than 0", 0
        
        if amount_float > 1000000:
            return False, "Amount cannot exceed 1,000,000", 0
        
        return True, "Valid amount", amount_float
    except ValueError:
        return False, "Invalid amount format", 0


# ==================== USER QUERIES ====================

def create_user(first_name, last_name, email, password, phone="", address="", role=ROLE_DONOR):
    """
    Create a new user in database
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email (unique)
        password (str): User's password (will be hashed)
        phone (str): User's phone number
        address (str): User's address
        role (str): User role (donor/admin)
        
    Returns:
        tuple: (bool, str, int) - (success, message, user_id)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "Email already exists", 0
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert user
        query = """
            INSERT INTO users (first_name, last_name, email, password_hash, phone, address, role, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            first_name, last_name, email, hashed_password,
            phone, address, role, datetime.now()
        ))
        
        user_id = cursor.lastrowid
        close_connection(connection)
        
        return True, "User created successfully", user_id
    
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, f"Error creating user: {str(e)}", 0


def authenticate_user(email, password):
    """
    Authenticate user with email and password
    
    Args:
        email (str): User's email
        password (str): User's password
        
    Returns:
        tuple: (bool, str, dict) - (success, message, user_data)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "SELECT id, first_name, last_name, email, password_hash, role FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        
        user = cursor.fetchone()
        close_connection(connection)
        
        if not user:
            return False, "Email not found", {}
        
        user_id, first_name, last_name, email_db, password_hash, role = user
        
        if not verify_password(password, password_hash):
            return False, "Invalid password", {}
        
        user_data = {
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email_db,
            'role': role
        }
        
        return True, "Authentication successful", user_data
    
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return False, f"Authentication error: {str(e)}", {}


def get_user_by_id(user_id):
    """
    Get user details by ID
    
    Args:
        user_id (int): User ID
        
    Returns:
        tuple: (bool, dict) - (success, user_data)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT id, first_name, last_name, email, phone, address, role, created_at
            FROM users WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        
        user = cursor.fetchone()
        close_connection(connection)
        
        if not user:
            return False, {}
        
        user_data = {
            'id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'phone': user[4],
            'address': user[5],
            'role': user[6],
            'created_at': user[7]
        }
        
        return True, user_data
    
    except Exception as e:
        print(f"Error getting user: {e}")
        return False, {}


def update_user(user_id, first_name=None, last_name=None, phone=None, address=None):
    """
    Update user information
    
    Args:
        user_id (int): User ID
        first_name (str): New first name
        last_name (str): New last name
        phone (str): New phone number
        address (str): New address
        
    Returns:
        tuple: (bool, str)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        updates = []
        values = []
        
        if first_name is not None:
            updates.append("first_name = %s")
            values.append(first_name)
        
        if last_name is not None:
            updates.append("last_name = %s")
            values.append(last_name)
        
        if phone is not None:
            updates.append("phone = %s")
            values.append(phone)
        
        if address is not None:
            updates.append("address = %s")
            values.append(address)
        
        if not updates:
            return False, "No updates provided"
        
        updates.append("updated_at = %s")
        values.append(datetime.now())
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, values)
        
        close_connection(connection)
        return True, "User updated successfully"
    
    except Exception as e:
        print(f"Error updating user: {e}")
        return False, f"Error updating user: {str(e)}"


# ==================== CAMPAIGN QUERIES ====================

def create_campaign(title, description, goal_amount, category, created_by, start_date=None, end_date=None):
    """
    Create a new campaign
    
    Args:
        title (str): Campaign title
        description (str): Campaign description
        goal_amount (float): Campaign goal amount
        category (str): Campaign category
        created_by (int): Admin user ID who created campaign
        start_date (datetime): Campaign start date
        end_date (datetime): Campaign end date
        
    Returns:
        tuple: (bool, str, int) - (success, message, campaign_id)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if start_date is None:
            start_date = datetime.now()
        
        query = """
            INSERT INTO campaigns (title, description, goal_amount, current_amount, 
                                 category, created_by, status, start_date, end_date, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            title, description, goal_amount, 0,
            category, created_by, "active", start_date, end_date, datetime.now()
        ))
        
        campaign_id = cursor.lastrowid
        close_connection(connection)
        
        return True, "Campaign created successfully", campaign_id
    
    except Exception as e:
        print(f"Error creating campaign: {e}")
        return False, f"Error creating campaign: {str(e)}", 0


def get_all_campaigns(status=None):
    """
    Get all campaigns, optionally filtered by status
    
    Args:
        status (str): Filter by status (optional)
        
    Returns:
        list: List of campaign dictionaries
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if status:
            query = """
                SELECT id, title, description, goal_amount, current_amount, category,
                       status, created_by, start_date, end_date, created_at
                FROM campaigns WHERE status = %s ORDER BY created_at DESC
            """
            cursor.execute(query, (status,))
        else:
            query = """
                SELECT id, title, description, goal_amount, current_amount, category,
                       status, created_by, start_date, end_date, created_at
                FROM campaigns ORDER BY created_at DESC
            """
            cursor.execute(query)
        
        campaigns = cursor.fetchall()
        close_connection(connection)
        
        campaigns_list = []
        for campaign in campaigns:
            campaigns_list.append({
                'id': campaign[0],
                'title': campaign[1],
                'description': campaign[2],
                'goal_amount': campaign[3],
                'current_amount': campaign[4],
                'category': campaign[5],
                'status': campaign[6],
                'created_by': campaign[7],
                'start_date': campaign[8],
                'end_date': campaign[9],
                'created_at': campaign[10]
            })
        
        return campaigns_list
    
    except Exception as e:
        print(f"Error fetching campaigns: {e}")
        return []


def get_campaign_by_id(campaign_id):
    """
    Get campaign details by ID
    
    Args:
        campaign_id (int): Campaign ID
        
    Returns:
        dict: Campaign data or empty dict if not found
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT id, title, description, goal_amount, current_amount, category,
                   status, created_by, start_date, end_date, created_at
            FROM campaigns WHERE id = %s
        """
        cursor.execute(query, (campaign_id,))
        
        campaign = cursor.fetchone()
        close_connection(connection)
        
        if not campaign:
            return {}
        
        return {
            'id': campaign[0],
            'title': campaign[1],
            'description': campaign[2],
            'goal_amount': campaign[3],
            'current_amount': campaign[4],
            'category': campaign[5],
            'status': campaign[6],
            'created_by': campaign[7],
            'start_date': campaign[8],
            'end_date': campaign[9],
            'created_at': campaign[10]
        }
    
    except Exception as e:
        print(f"Error fetching campaign: {e}")
        return {}


def update_campaign(campaign_id, title=None, description=None, goal_amount=None, 
                   category=None, status=None, end_date=None):
    """
    Update campaign information
    
    Args:
        campaign_id (int): Campaign ID
        title (str): New title
        description (str): New description
        goal_amount (float): New goal amount
        category (str): New category
        status (str): New status
        end_date (datetime): New end date
        
    Returns:
        tuple: (bool, str)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = %s")
            values.append(title)
        
        if description is not None:
            updates.append("description = %s")
            values.append(description)
        
        if goal_amount is not None:
            updates.append("goal_amount = %s")
            values.append(goal_amount)
        
        if category is not None:
            updates.append("category = %s")
            values.append(category)
        
        if status is not None:
            updates.append("status = %s")
            values.append(status)
        
        if end_date is not None:
            updates.append("end_date = %s")
            values.append(end_date)
        
        if not updates:
            return False, "No updates provided"
        
        updates.append("updated_at = %s")
        values.append(datetime.now())
        values.append(campaign_id)
        
        query = f"UPDATE campaigns SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, values)
        
        close_connection(connection)
        return True, "Campaign updated successfully"
    
    except Exception as e:
        print(f"Error updating campaign: {e}")
        return False, f"Error updating campaign: {str(e)}"


# ==================== DONATION QUERIES ====================

def create_donation(donor_id, campaign_id, amount, message=""):
    """
    Create a new donation
    
    Args:
        donor_id (int): Donor user ID
        campaign_id (int): Campaign ID
        amount (float): Donation amount
        message (str): Optional donation message
        
    Returns:
        tuple: (bool, str, int) - (success, message, donation_id)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if campaign exists
        cursor.execute("SELECT current_amount FROM campaigns WHERE id = %s", (campaign_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, "Campaign not found", 0
        
        current_amount = result[0]
        
        # Convert to float to handle Decimal type from database
        current_amount = float(current_amount)
        amount = float(amount)
        
        # Insert donation
        query = """
            INSERT INTO donations (donor_id, campaign_id, amount, message, donation_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (donor_id, campaign_id, amount, message, datetime.now()))
        donation_id = cursor.lastrowid
        
        # Update campaign current amount
        new_amount = current_amount + amount
        cursor.execute(
            "UPDATE campaigns SET current_amount = %s WHERE id = %s",
            (new_amount, campaign_id)
        )
        
        close_connection(connection)
        return True, "Donation created successfully", donation_id
    
    except Exception as e:
        print(f"Error creating donation: {e}")
        return False, f"Error creating donation: {str(e)}", 0


def get_user_donations(user_id):
    """
    Get all donations by a user
    
    Args:
        user_id (int): User ID
        
    Returns:
        list: List of donation dictionaries
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT d.id, d.donor_id, d.campaign_id, c.title, d.amount, d.message, d.donation_date
            FROM donations d
            JOIN campaigns c ON d.campaign_id = c.id
            WHERE d.donor_id = %s
            ORDER BY d.donation_date DESC
        """
        cursor.execute(query, (user_id,))
        
        donations = cursor.fetchall()
        close_connection(connection)
        
        donations_list = []
        for donation in donations:
            donations_list.append({
                'id': donation[0],
                'donor_id': donation[1],
                'campaign_id': donation[2],
                'campaign_title': donation[3],
                'amount': donation[4],
                'message': donation[5],
                'donation_date': donation[6]
            })
        
        return donations_list
    
    except Exception as e:
        print(f"Error fetching user donations: {e}")
        return []


def get_campaign_donations(campaign_id):
    """
    Get all donations for a campaign
    
    Args:
        campaign_id (int): Campaign ID
        
    Returns:
        list: List of donation dictionaries
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT d.id, d.donor_id, u.first_name, u.last_name, d.amount, d.message, d.donation_date
            FROM donations d
            JOIN users u ON d.donor_id = u.id
            WHERE d.campaign_id = %s
            ORDER BY d.donation_date DESC
        """
        cursor.execute(query, (campaign_id,))
        
        donations = cursor.fetchall()
        close_connection(connection)
        
        donations_list = []
        for donation in donations:
            donations_list.append({
                'id': donation[0],
                'donor_id': donation[1],
                'donor_name': f"{donation[2]} {donation[3]}",
                'amount': donation[4],
                'message': donation[5],
                'donation_date': donation[6]
            })
        
        return donations_list
    
    except Exception as e:
        print(f"Error fetching campaign donations: {e}")
        return []


def get_user_total_donations(user_id):
    """
    Get total donation amount by a user
    
    Args:
        user_id (int): User ID
        
    Returns:
        float: Total donation amount
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "SELECT SUM(amount) FROM donations WHERE donor_id = %s"
        cursor.execute(query, (user_id,))
        
        result = cursor.fetchone()
        close_connection(connection)
        
        return result[0] if result[0] else 0.0
    
    except Exception as e:
        print(f"Error calculating total donations: {e}")
        return 0.0


# ==================== STATISTICS QUERIES ====================

def get_dashboard_stats():
    """
    Get overall dashboard statistics
    
    Returns:
        dict: Dictionary with various statistics
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Total donations
        cursor.execute("SELECT SUM(amount) FROM donations")
        total_donations = cursor.fetchone()[0] or 0.0
        
        # Total donors
        cursor.execute("SELECT COUNT(DISTINCT donor_id) FROM donations")
        total_donors = cursor.fetchone()[0] or 0
        
        # Active campaigns
        cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'active'")
        active_campaigns = cursor.fetchone()[0] or 0
        
        # Total beneficiaries (unique donors)
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = %s", (ROLE_DONOR,))
        total_beneficiaries = cursor.fetchone()[0] or 0
        
        close_connection(connection)
        
        return {
            'total_donations': float(total_donations),
            'total_donors': int(total_donors),
            'active_campaigns': int(active_campaigns),
            'total_beneficiaries': int(total_beneficiaries)
        }
    
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {
            'total_donations': 0.0,
            'total_donors': 0,
            'active_campaigns': 0,
            'total_beneficiaries': 0
        }


def get_campaign_stats(campaign_id):
    """
    Get statistics for a specific campaign
    
    Args:
        campaign_id (int): Campaign ID
        
    Returns:
        dict: Campaign statistics
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Campaign basic info
        cursor.execute(
            "SELECT goal_amount, current_amount FROM campaigns WHERE id = %s",
            (campaign_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return {}
        
        goal, current = result
        
        # Number of donors
        cursor.execute(
            "SELECT COUNT(DISTINCT donor_id) FROM donations WHERE campaign_id = %s",
            (campaign_id,)
        )
        donors_count = cursor.fetchone()[0] or 0
        
        close_connection(connection)
        
        percentage = (current / goal * 100) if goal > 0 else 0
        
        return {
            'goal_amount': float(goal),
            'current_amount': float(current),
            'percentage': round(percentage, 1),
            'donors_count': int(donors_count),
            'remaining': max(0, float(goal - current))
        }
    
    except Exception as e:
        print(f"Error getting campaign stats: {e}")
        return {}