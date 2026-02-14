"""
Login and Registration Screens with Database Integration
Handles user authentication and registration with forgot password functionality
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk
import io

from utils import (
    authenticate_user, create_user, validate_email,
    validate_password, validate_name, validate_phone, update_user,
    hash_password
)
from config import ROLE_DONOR, get_db_connection, close_connection


class PasswordEntry(ctk.CTkFrame):
    """Custom password entry with show/hide toggle"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.show_password = False
        
        # Create entry frame
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(fill="x")
        
        # Password entry
        self.entry = ctk.CTkEntry(entry_frame, show="*", *args, **kwargs)
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Show/hide button
        self.toggle_btn = ctk.CTkButton(
            entry_frame, text="👁️", width=40, height=40,
            fg_color="#4A5766", hover_color="#5A6776",
            corner_radius=8, font=("Arial", 12),
            command=self.toggle_visibility
        )
        self.toggle_btn.pack(side="right", padx=(5, 0))
    
    def toggle_visibility(self):
        """Toggle password visibility"""
        self.show_password = not self.show_password
        
        if self.show_password:
            self.entry.configure(show="")
            self.toggle_btn.configure(text="🙈")
        else:
            self.entry.configure(show="*")
            self.toggle_btn.configure(text="👁️")
    
    def get(self):
        """Get password value"""
        return self.entry.get()
    
    def insert(self, index, value):
        """Insert value into entry"""
        self.entry.insert(index, value)
    
    def delete(self, start, end):
        """Delete value from entry"""
        self.entry.delete(start, end)


class AuthScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Donation Management System")
        self.geometry("900x600")
        
        # Store current user data
        self.current_user = None
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create background
        self.create_background()
        
        # Show login screen by default
        self.show_login()
    
    def create_background(self):
        """Load and display background image or fallback color"""
        try:
            # Try to load background image
            bg_image = Image.open("background.png")
            bg_image = bg_image.resize((900, 600), Image.Resampling.LANCZOS)
            self.bg_image = ctk.CTkImage(light_image=bg_image, 
                                         dark_image=bg_image, 
                                         size=(900, 600))
            
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
        except FileNotFoundError:
            # Fallback to colored background
            self.bg_label = ctk.CTkLabel(self, text="", fg_color="#6C4FDB")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def clear_forms(self):
        """Clear all form widgets from window"""
        for widget in self.winfo_children():
            if widget != self.bg_label:
                widget.destroy()
    
    def show_login(self):
        """Display login screen with database integration"""
        self.clear_forms()
        
        # Login form container
        form_frame = ctk.CTkFrame(self, fg_color="#2B2B40", corner_radius=20,
                                 width=400, height=520, border_width=2,
                                 border_color="#3D3D5C")
        form_frame.place(relx=0.08, rely=0.5, anchor="w")
        form_frame.pack_propagate(False)
        
        # Content container
        content_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        content_frame.pack(expand=True, padx=40, pady=30)
        
        # Title
        ctk.CTkLabel(content_frame, text="Donation Management System", 
                    font=("Arial", 21, "bold"), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(content_frame, text="Find causes that matter to you", 
                    font=("Arial", 13), text_color="#8B8B9A").pack(pady=(0, 30))
        
        # Email field
        ctk.CTkLabel(content_frame, text="Email", font=("Arial", 12), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        email_entry = ctk.CTkEntry(content_frame, placeholder_text="Enter your email", 
                                  height=40, corner_radius=8, width=320)
        email_entry.pack(fill="x", pady=(0, 20))
        
        # Password field with visibility toggle
        ctk.CTkLabel(content_frame, text="Password", font=("Arial", 12), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        password_entry = PasswordEntry(content_frame, placeholder_text="Enter your password", 
                                      height=40, corner_radius=8)
        password_entry.pack(fill="x", pady=(0, 25))
        
        # Error label
        error_label = ctk.CTkLabel(content_frame, text="", font=("Arial", 10),
                                   text_color="#FF6B6B")
        error_label.pack(fill="x", pady=(0, 10))
        
        # Login button
        def handle_login():
            email = email_entry.get().strip()
            password = password_entry.get()
            error_label.configure(text="")
            
            # Validation
            is_valid, msg = validate_email(email)
            if not is_valid:
                error_label.configure(text=msg)
                return
            
            if not password:
                error_label.configure(text="Password is required")
                return
            
            # Authenticate user
            success, msg, user_data = authenticate_user(email, password)
            
            if success:
                self.current_user = user_data
                messagebox.showinfo("Success", f"Welcome back, {user_data['first_name']}!")
                self.launch_dashboard()
            else:
                error_label.configure(text=msg)
        
        login_btn = ctk.CTkButton(content_frame, text="Login", height=45, 
                                 corner_radius=8, fg_color="black", 
                                 hover_color="#1a1a1a", font=("Arial", 14, "bold"),
                                 width=320, command=handle_login)
        login_btn.pack(fill="x", pady=(0, 15))
        
        # Sign up link
        signup_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        signup_frame.pack(pady=(0, 10))
        
        ctk.CTkLabel(signup_frame, text="Don't have an account?", 
                    font=("Arial", 12), text_color="#8B8B9A").pack(side="left", padx=(0, 5))
        signup_link = ctk.CTkButton(signup_frame, text="Sign Up", 
                                   fg_color="transparent", hover_color="#3D3D5C",
                                   text_color="white", font=("Arial", 12, "bold"),
                                   width=60, command=self.show_signup)
        signup_link.pack(side="left")
        
        # Forgot password button
        forgot_btn = ctk.CTkButton(content_frame, text="Forgot Password?", 
                                  fg_color="transparent", hover_color="#3D3D5C",
                                  text_color="#8B8B9A", font=("Arial", 11), width=150,
                                  command=self.show_forgot_password)
        forgot_btn.pack()
    
    def show_signup(self):
        """Display signup screen with database integration"""
        self.clear_forms()
        
        # Signup form container
        form_frame = ctk.CTkFrame(self, fg_color="#2B2B40", corner_radius=20,
                                 width=420, height=560, border_width=2,
                                 border_color="#3D3D5C")
        form_frame.place(relx=0.08, rely=0.5, anchor="w")
        form_frame.pack_propagate(False)
        
        # Content container with scrollable frame
        content_frame = ctk.CTkScrollableFrame(form_frame, fg_color="transparent",
                                               width=340, height=500)
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Title
        ctk.CTkLabel(content_frame, text="Create Account", 
                    font=("Arial", 24, "bold"), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(content_frame, text="Join our community of donors", 
                    font=("Arial", 13), text_color="#8B8B9A").pack(pady=(0, 25))
        
        # Error label
        error_label = ctk.CTkLabel(content_frame, text="", font=("Arial", 10),
                                   text_color="#FF6B6B")
        error_label.pack(fill="x", pady=(0, 15))
        
        # Name fields
        name_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=(0, 20))
        
        # First Name
        fname_container = ctk.CTkFrame(name_frame, fg_color="transparent")
        fname_container.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(fname_container, text="First Name", font=("Arial", 11), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        fname_entry = ctk.CTkEntry(fname_container, placeholder_text="Enter your First Name", 
                                  height=40, corner_radius=8)
        fname_entry.pack(fill="x")
        
        # Last Name
        lname_container = ctk.CTkFrame(name_frame, fg_color="transparent")
        lname_container.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lname_container, text="Last Name", font=("Arial", 11), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        lname_entry = ctk.CTkEntry(lname_container, placeholder_text="Enter your Last Name", 
                                  height=40, corner_radius=8)
        lname_entry.pack(fill="x")
        
        # Email field
        ctk.CTkLabel(content_frame, text="Email", font=("Arial", 11), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        email_entry = ctk.CTkEntry(content_frame, placeholder_text="Enter your email", 
                                  height=40, corner_radius=8)
        email_entry.pack(fill="x", pady=(0, 20))
        
        # Phone field
        ctk.CTkLabel(content_frame, text="Phone (Optional)", font=("Arial", 11), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        phone_entry = ctk.CTkEntry(content_frame, placeholder_text="Enter your phone", 
                                  height=40, corner_radius=8)
        phone_entry.pack(fill="x", pady=(0, 20))
        
        # Password field
        ctk.CTkLabel(content_frame, text="Password", font=("Arial", 11), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        password_entry = PasswordEntry(content_frame, placeholder_text="Enter your password", 
                                      height=40, corner_radius=8)
        password_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(content_frame, text="(Min 6 characters)", font=("Arial", 9),
                    text_color="#8B8B9A").pack(fill="x", pady=(0, 20))
        
        # Confirm Password field
        ctk.CTkLabel(content_frame, text="Confirm Password", font=("Arial", 11), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        confirm_entry = PasswordEntry(content_frame, placeholder_text="Confirm your password", 
                                     height=40, corner_radius=8)
        confirm_entry.pack(fill="x", pady=(0, 25))
        
        # Sign Up button
        def handle_signup():
            fname = fname_entry.get().strip()
            lname = lname_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            error_label.configure(text="")
            
            # Validations
            is_valid, msg = validate_name(fname, "First name")
            if not is_valid:
                error_label.configure(text=msg)
                return
            
            is_valid, msg = validate_name(lname, "Last name")
            if not is_valid:
                error_label.configure(text=msg)
                return
            
            is_valid, msg = validate_email(email)
            if not is_valid:
                error_label.configure(text=msg)
                return
            
            if phone:
                is_valid, msg = validate_phone(phone)
                if not is_valid:
                    error_label.configure(text=msg)
                    return
            
            is_valid, msg = validate_password(password)
            if not is_valid:
                error_label.configure(text=msg)
                return
            
            if password != confirm:
                error_label.configure(text="Passwords do not match")
                return
            
            # Create user in database
            success, msg, user_id = create_user(
                fname, lname, email, password, phone, role=ROLE_DONOR
            )
            
            if success:
                messagebox.showinfo("Success", f"Account created successfully!\nWelcome, {fname}!")
                self.show_login()
            else:
                error_label.configure(text=msg)
        
        signup_btn = ctk.CTkButton(content_frame, text="Sign Up", height=45, 
                                  corner_radius=8, fg_color="black", 
                                  hover_color="#1a1a1a", font=("Arial", 14, "bold"),
                                  command=handle_signup)
        signup_btn.pack(fill="x", pady=(0, 15))
        
        # Login link
        login_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        login_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(login_frame, text="Already have an account?", 
                    font=("Arial", 12), text_color="#8B8B9A").pack(side="left", padx=(0, 5))
        login_link = ctk.CTkButton(login_frame, text="Log In", 
                                  fg_color="transparent", hover_color="#3D3D5C",
                                  text_color="white", font=("Arial", 12, "bold"),
                                  width=60, command=self.show_login)
        login_link.pack(side="left")
    
    def show_forgot_password(self):
        """Display forgot password screen"""
        self.clear_forms()
        
        # Forgot password form
        form_frame = ctk.CTkFrame(self, fg_color="#2B2B40", corner_radius=20,
                                 width=420, height=500, border_width=2,
                                 border_color="#3D3D5C")
        form_frame.place(relx=0.08, rely=0.5, anchor="w")
        form_frame.pack_propagate(False)
        
        # Content container
        content_frame = ctk.CTkScrollableFrame(form_frame, fg_color="transparent",
                                               width=340, height=450)
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Title
        ctk.CTkLabel(content_frame, text="Reset Password", 
                    font=("Arial", 24, "bold"), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(content_frame, text="Enter your email to reset your password", 
                    font=("Arial", 12), text_color="#8B8B9A").pack(pady=(0, 25))
        
        # Error/Success label
        message_label = ctk.CTkLabel(content_frame, text="", font=("Arial", 10),
                                     text_color="#FF6B6B")
        message_label.pack(fill="x", pady=(0, 15))
        
        # Email field
        ctk.CTkLabel(content_frame, text="Email Address", font=("Arial", 12), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        email_entry = ctk.CTkEntry(content_frame, placeholder_text="Enter your email", 
                                  height=40, corner_radius=8)
        email_entry.pack(fill="x", pady=(0, 25))
        
        # New Password field
        ctk.CTkLabel(content_frame, text="New Password", font=("Arial", 12), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        password_entry = PasswordEntry(content_frame, placeholder_text="Enter new password", 
                                      height=40, corner_radius=8)
        password_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(content_frame, text="(Min 6 characters)", font=("Arial", 9),
                    text_color="#8B8B9A").pack(fill="x", pady=(0, 20))
        
        # Confirm Password field
        ctk.CTkLabel(content_frame, text="Confirm Password", font=("Arial", 12), 
                    text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        confirm_entry = PasswordEntry(content_frame, placeholder_text="Confirm password", 
                                     height=40, corner_radius=8)
        confirm_entry.pack(fill="x", pady=(0, 25))
        
        # Reset button
        def handle_reset():
            email = email_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            message_label.configure(text="", text_color="#FF6B6B")
            
            # Validation
            is_valid, msg = validate_email(email)
            if not is_valid:
                message_label.configure(text=msg)
                return
            
            is_valid, msg = validate_password(password)
            if not is_valid:
                message_label.configure(text=msg)
                return
            
            if password != confirm:
                message_label.configure(text="Passwords do not match")
                return
            
            # Check if user exists and update password
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
                
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if not user:
                    message_label.configure(text="Email not found")
                    close_connection(connection)
                    return
                
                # Hash and update password
                hashed_password = hash_password(password)
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE email = %s",
                    (hashed_password, email)
                )
                
                close_connection(connection)
                
                message_label.configure(text="✓ Password reset successfully!", text_color="#10B981")
                messagebox.showinfo("Success", "Password has been reset!\nYou can now login with your new password.")
                self.show_login()
                
            except Exception as e:
                message_label.configure(text=f"Error: {str(e)}")
        
        reset_btn = ctk.CTkButton(content_frame, text="Reset Password", height=45, 
                                 corner_radius=8, fg_color="#5B72EE", 
                                 hover_color="#4A5FD8", font=("Arial", 14, "bold"),
                                 command=handle_reset)
        reset_btn.pack(fill="x", pady=(0, 15))
        
        # Back to login button
        back_btn = ctk.CTkButton(content_frame, text="Back to Login", height=45, 
                                corner_radius=8, fg_color="white", 
                                text_color="#6B7280", hover_color="#F3F4F6",
                                font=("Arial", 14), border_width=2, 
                                border_color="#E5E7EB",
                                command=self.show_login)
        back_btn.pack(fill="x")
    
    def launch_dashboard(self):
        """Launch appropriate dashboard based on user role"""
        # Import here to avoid circular imports
        from donor_screens import DonorApp
        from admin_screens import AdminDashboard
        
        if self.current_user['role'] == 'admin':
            self.destroy()
            app = AdminDashboard(self.current_user)
            app.mainloop()
        else:  # donor
            self.destroy()
            app = DonorApp(self.current_user)
            app.mainloop()


if __name__ == "__main__":
    app = AuthScreen()
    app.mainloop()