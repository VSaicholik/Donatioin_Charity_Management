import customtkinter as ctk

from tkinter import messagebox
from datetime import datetime
from utils import (
    get_all_campaigns, get_campaign_by_id, get_user_donations,
    get_user_total_donations, create_donation, update_user,
    get_campaign_stats, validate_amount, get_user_by_id
)

class DonorApp(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.current_campaign_for_donation = None
        self.last_donation_amount = None
        self.last_donation_campaign = None
        self.show_acknowledgement = False
        self.title("Donation Management System - Donor")
        self.geometry("1200x800")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.show_home_screen()

    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.winfo_children():
            widget.destroy()

    def create_navbar(self, current_page):
        """Create bottom navigation bar"""
        navbar = ctk.CTkFrame(self, height=70, fg_color="#F5F7FA", corner_radius=0)
        navbar.pack(side="bottom", fill="x")
        buttons = [
            ("🏠", "Home", "home"),
            ("📋", "Campaigns", "campaigns"),
            ("❤️", "Donate", "donate"),
            ("📊", "Impact", "impact"),
            ("👤", "Profile", "profile")
        ]

        for icon, label, page in buttons:
            btn_frame = ctk.CTkFrame(navbar, fg_color="transparent")
            btn_frame.pack(side="left", expand=True)
            is_active = (page == current_page)
            bg_color = "#E8EEFF" if is_active else "transparent"
            btn = ctk.CTkButton(btn_frame, text=f"{icon}\n{label}",
                                fg_color=bg_color, hover_color="#E8EEFF",
                                text_color="#5B72EE" if is_active else "#8B8B9A",
                                font=("Arial", 11), width=80, height=60,
                                command=lambda p=page: self.navigate(p))
            btn.pack()

    def navigate(self, page):
        """Navigate to different pages"""
        if page == "home":
            self.show_home_screen()
        elif page == "campaigns":
            self.show_campaign_list()
        elif page == "donate":
            self.show_donation_screen()
        elif page == "impact":
            self.show_impact_screen()
        elif page == "profile":
            self.show_profile_screen()

    def create_header(self, title, subtitle, show_settings=True):
        """Create header with user info and logout button"""
        header = ctk.CTkFrame(self, height=70, fg_color="#3D4A5C", corner_radius=0)
        header.pack(fill="x")

        # User avatar and info
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=10)
        initials = f"{self.user_data['first_name'][0]}{self.user_data['last_name'][0]}".upper()
        avatar = ctk.CTkLabel(left_frame, text=initials,
                              font=("Arial", 16, "bold"),
                              fg_color="#5B72EE", text_color="white",
                              width=45, height=45, corner_radius=22)
        avatar.pack(side="left", padx=(0, 15))

        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left")
        ctk.CTkLabel(info_frame, text=title, font=("Arial", 18, "bold"),
                     text_color="white").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=subtitle, font=("Arial", 12),
                     text_color="#B0B8C1").pack(anchor="w")

        # Right side - Logout and Settings buttons
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=10)

        logout_btn = ctk.CTkButton(right_frame, text="🚪 Logout", width=100, height=45,
                                   fg_color="#FF6B6B", hover_color="#FF5252",
                                   corner_radius=10, font=("Arial", 11),
                                   command=self.logout)
        logout_btn.pack(side="right", padx=(10, 0))

        if show_settings:
            settings_btn = ctk.CTkButton(right_frame, text="⚙️", width=45, height=45,
                                         fg_color="#4A5766", hover_color="#5A6776",
                                         corner_radius=22, font=("Arial", 18))
            settings_btn.pack(side="right", padx=(0, 10))
            avatar_right = ctk.CTkLabel(right_frame, text=initials,
                                        font=("Arial", 16, "bold"),
                                        fg_color="#5B72EE", text_color="white",
                                        width=45, height=45, corner_radius=22)
            avatar_right.pack(side="right", padx=(0, 10))

    def logout(self):
        """Logout function"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            from login_register_screens import AuthScreen
            self.destroy()
            app = AuthScreen()
            app.mainloop()

    def show_home_screen(self):
        """Display donor home screen"""
        self.clear_window()
        self.create_header("Welcome back, " + self.user_data['first_name'] + "!",
                          "Thank you for making a difference")
        self.create_navbar("home")

        content = ctk.CTkScrollableFrame(self, fg_color="#F5F7FA")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        total_donations = get_user_total_donations(self.user_data['id'])
        user_donations = get_user_donations(self.user_data['id'])
        campaigns_joined = len(set(d['campaign_id'] for d in user_donations))

        stats_frame = ctk.CTkFrame(content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        stats = [
            ("💵", "Total Donations", f"${total_donations:.2f}", "+12.5%", "#10B981"),
            ("📋", "Active Campaigns", str(campaigns_joined), "Active", "#5B72EE"),
            ("❤️", "Impact Created", f"{campaigns_joined * 10} people helped", "Lives", "#F59E0B")
        ]

        for icon, title, value, badge, color in stats:
            card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12)
            card.pack(side="left", fill="x", expand=True, padx=5)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=20, pady=15)

            icon_label = ctk.CTkLabel(top, text=icon, font=("Arial", 24),
                                      fg_color=color, text_color="white",
                                      width=45, height=45, corner_radius=8)
            icon_label.pack(side="left")

            badge_label = ctk.CTkLabel(top, text=badge, font=("Arial", 11),
                                       fg_color="#E8EEFF", text_color=color,
                                       corner_radius=12, padx=10, pady=5)
            badge_label.pack(side="right")

            ctk.CTkLabel(card, text=title, font=("Arial", 12),
                        text_color="#6B7280", anchor="w").pack(fill="x", padx=20)
            ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"),
                        text_color="#1F2937", anchor="w").pack(fill="x", padx=20, pady=(5, 15))

        recent_frame = ctk.CTkFrame(content, fg_color="white", corner_radius=12)
        recent_frame.pack(fill="both", expand=True, pady=10)

        header_frame = ctk.CTkFrame(recent_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(header_frame, text="Recent Donations",
                    font=("Arial", 18, "bold"), text_color="#1F2937").pack(side="left")

        if user_donations:
            donations_scroll = ctk.CTkScrollableFrame(recent_frame, fg_color="transparent")
            donations_scroll.pack(fill="both", expand=True, padx=20, pady=10)

            for donation in user_donations[:5]:
                donation_item = ctk.CTkFrame(donations_scroll, fg_color="#F9FAFB", corner_radius=8)
                donation_item.pack(fill="x", pady=5)

                info_frame = ctk.CTkFrame(donation_item, fg_color="transparent")
                info_frame.pack(fill="x", padx=15, pady=10)

                ctk.CTkLabel(info_frame, text=donation['campaign_title'],
                            font=("Arial", 12, "bold"), text_color="#1F2937",
                            anchor="w").pack(fill="x")
                ctk.CTkLabel(info_frame, text=str(donation['donation_date']),
                            font=("Arial", 10), text_color="#9CA3AF",
                            anchor="w").pack(fill="x")
                ctk.CTkLabel(info_frame, text=f"${donation['amount']:.2f}",
                            font=("Arial", 13, "bold"), text_color="#10B981",
                            anchor="e").pack(fill="x")
        else:
            ctk.CTkLabel(recent_frame, text="No donations yet. Start making a difference!",
                        font=("Arial", 13), text_color="#9CA3AF",
                        anchor="center").pack(fill="both", expand=True)

    def show_campaign_list(self):
        """Display campaign list screen"""
        self.clear_window()
        self.create_header("Explore Campaigns", "Find causes that matter to you")
        self.create_navbar("campaigns")

        search_frame = ctk.CTkFrame(self, fg_color="#F5F7FA", height=80)
        search_frame.pack(fill="x", padx=20, pady=15)

        search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Search campaigns...",
                                    height=45, font=("Arial", 14), corner_radius=10)
        search_entry.pack(fill="x", padx=10, pady=10)

        content = ctk.CTkScrollableFrame(self, fg_color="#F5F7FA")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        campaigns = get_all_campaigns(status="active")

        if not campaigns:
            ctk.CTkLabel(content, text="No campaigns available at the moment.",
                        font=("Arial", 14), text_color="#6B7280").pack(pady=20)
            return

        for campaign in campaigns:
            stats = get_campaign_stats(campaign['id'])
            card = ctk.CTkFrame(content, fg_color="white", corner_radius=12)
            card.pack(fill="x", pady=8)

            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(15, 5))

            ctk.CTkLabel(header_frame, text=campaign['title'], font=("Arial", 14, "bold"),
                        text_color="#1F2937", anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(header_frame, text=campaign['category'], font=("Arial", 10),
                        text_color="#5B72EE", anchor="e").pack(side="right")

            desc_text = campaign['description'][:100] + "..." if len(campaign['description']) > 100 else campaign['description']
            ctk.CTkLabel(card, text=desc_text, font=("Arial", 11), text_color="#6B7280",
                        anchor="w", wraplength=800).pack(fill="x", padx=20, pady=(0, 10))

            progress_frame = ctk.CTkFrame(card, fg_color="transparent")
            progress_frame.pack(fill="x", padx=20, pady=(0, 8))

            bar_bg = ctk.CTkFrame(progress_frame, height=8, fg_color="#E5E7EB", corner_radius=4)
            bar_bg.pack(fill="x")

            bar_fill = ctk.CTkFrame(bar_bg, fg_color="#5B72EE", corner_radius=4)
            bar_fill.place(relx=0, rely=0, relwidth=min(stats['percentage']/100, 1.0), relheight=1)

            stats_frame = ctk.CTkFrame(card, fg_color="transparent")
            stats_frame.pack(fill="x", padx=20, pady=(0, 15))

            ctk.CTkLabel(stats_frame, text=f"${stats['current_amount']:.0f} of ${stats['goal_amount']:.0f}",
                        font=("Arial", 11, "bold"), text_color="#1F2937", anchor="w").pack(side="left")

            ctk.CTkLabel(stats_frame, text=f"{stats['percentage']:.0f}%",
                        font=("Arial", 11, "bold"), text_color="#5B72EE", anchor="e").pack(side="right")

            ctk.CTkLabel(stats_frame, text=f"{stats['donors_count']} donors",
                        font=("Arial", 10), text_color="#9CA3AF", anchor="e").pack(side="right", padx=(0, 10))

            def donate_to_campaign(cid=campaign['id']):
                self.current_campaign_for_donation = cid
                self.show_donation_screen()

            donate_btn = ctk.CTkButton(card, text="💝 Donate", height=35, font=("Arial", 12),
                                      command=donate_to_campaign, fg_color="#5B72EE",
                                      hover_color="#4A5FD8")
            donate_btn.pack(fill="x", padx=20, pady=(0, 15))

    def show_donation_screen(self):
        """Display donation screen"""
        self.clear_window()
        
        if self.show_acknowledgement:
            # Show acknowledgement
            self.create_header("Thank You! 🎉", "Your donation makes a real difference")
            self.create_navbar("donate")

            content = ctk.CTkFrame(self, fg_color="#F5F7FA")
            content.pack(fill="both", expand=True, padx=40, pady=40)

            # Acknowledgement card
            ack_card = ctk.CTkFrame(content, fg_color="white", corner_radius=16)
            ack_card.pack(fill="both", expand=True)

            # Success message
            ctk.CTkLabel(ack_card, text="✓ Donation Successful!",
                        font=("Arial", 32, "bold"), text_color="#10B981").pack(pady=(30, 10))

            if self.last_donation_campaign and self.last_donation_amount:
                campaign = get_campaign_by_id(self.last_donation_campaign)
                if campaign:
                    ctk.CTkLabel(ack_card,
                                text=f"You donated ${self.last_donation_amount:.2f} to:\n{campaign['title']}",
                                font=("Arial", 16), text_color="#1F2937",
                                justify="center").pack(pady=(20, 30))

            ctk.CTkLabel(ack_card,
                        text="Thank you for your generous contribution!\nYour support helps make our mission possible.",
                        font=("Arial", 14), text_color="#6B7280",
                        justify="center").pack(pady=(0, 40))

            # Action buttons
            button_frame = ctk.CTkFrame(ack_card, fg_color="transparent")
            button_frame.pack(fill="x", padx=40, pady=(0, 30))

            def go_back_campaigns():
                self.show_acknowledgement = False
                self.current_campaign_for_donation = None
                self.show_campaign_list()

            def view_other_campaigns():
                self.show_acknowledgement = False
                self.current_campaign_for_donation = None
                self.show_campaign_list()

            back_btn = ctk.CTkButton(button_frame, text="← Back to Campaigns", height=45,
                                    fg_color="#5B72EE", hover_color="#4A5FD8",
                                    font=("Arial", 14, "bold"),
                                    command=go_back_campaigns)
            back_btn.pack(fill="x", padx=(0, 10), side="left", expand=True)

            other_btn = ctk.CTkButton(button_frame, text="View Other Campaigns →", height=45,
                                     fg_color="white", text_color="#5B72EE",
                                     border_width=2, border_color="#5B72EE",
                                     font=("Arial", 14, "bold"),
                                     command=view_other_campaigns)
            other_btn.pack(fill="x", padx=(10, 0), side="left", expand=True)

        else:
            # Show donation form
            self.create_header("Make a Donation", "Support campaigns you believe in")
            self.create_navbar("donate")

            content = ctk.CTkScrollableFrame(self, fg_color="#F5F7FA")
            content.pack(fill="both", expand=True, padx=40, pady=30)

            if self.current_campaign_for_donation:
                campaign = get_campaign_by_id(self.current_campaign_for_donation)
                if campaign:
                    # Campaign info - PROMINENTLY DISPLAYED
                    campaign_info = ctk.CTkFrame(content, fg_color="#E8EEFF", corner_radius=12)
                    campaign_info.pack(fill="x", pady=(0, 20))

                    ctk.CTkLabel(campaign_info, text="📌 Campaign Selected:", font=("Arial", 13, "bold"),
                                text_color="#5B72EE", anchor="w").pack(fill="x", padx=20, pady=(15, 5))

                    ctk.CTkLabel(campaign_info, text=campaign['title'], font=("Arial", 18, "bold"),
                                text_color="#1F2937", anchor="w").pack(fill="x", padx=20, pady=(0, 10))

                    # Campaign stats
                    stats = get_campaign_stats(campaign['id'])
                    campaign_stats_frame = ctk.CTkFrame(campaign_info, fg_color="transparent")
                    campaign_stats_frame.pack(fill="x", padx=20, pady=(0, 15))

                    ctk.CTkLabel(campaign_stats_frame, 
                                text=f"Goal: ${stats['goal_amount']:.2f} | Raised: ${stats['current_amount']:.2f} ({stats['percentage']:.0f}%) | Donors: {stats['donors_count']}",
                                font=("Arial", 11), text_color="#6B7280", anchor="w").pack(fill="x")

                    # Donation form
                    form_card = ctk.CTkFrame(content, fg_color="white", corner_radius=12)
                    form_card.pack(fill="x", pady=(0, 20))

                    ctk.CTkLabel(form_card, text="Donation Amount", font=("Arial", 14, "bold"),
                                text_color="#1F2937", anchor="w").pack(fill="x", padx=20, pady=(20, 10))

                    # Suggested amounts
                    suggested_frame = ctk.CTkFrame(form_card, fg_color="transparent")
                    suggested_frame.pack(fill="x", padx=20, pady=(0, 15))

                    amount_var = ctk.StringVar(value="")

                    def set_amount(amt):
                        amount_entry.delete("0", "end")
                        amount_entry.insert("0", str(amt))
                        amount_var.set(str(amt))

                    for amt in [10, 25, 50, 100]:
                        btn = ctk.CTkButton(suggested_frame, text=f"${amt}", width=50, height=35,
                                          fg_color="#E8EEFF", text_color="#5B72EE",
                                          hover_color="#D8DEFF", font=("Arial", 11),
                                          command=lambda a=amt: set_amount(a))
                        btn.pack(side="left", padx=5)

                    ctk.CTkLabel(form_card, text="Custom Amount ($)", font=("Arial", 12),
                                text_color="#1F2937", anchor="w").pack(fill="x", padx=20, pady=(0, 5))

                    amount_entry = ctk.CTkEntry(form_card, placeholder_text="Enter amount", height=40, corner_radius=8)
                    amount_entry.pack(fill="x", padx=20, pady=(0, 20))

                    ctk.CTkLabel(form_card, text="Optional Message", font=("Arial", 12),
                                text_color="#1F2937", anchor="w").pack(fill="x", padx=20, pady=(0, 5))

                    message_entry = ctk.CTkTextbox(form_card, height=80, corner_radius=8)
                    message_entry.pack(fill="x", padx=20, pady=(0, 20))

                    error_label = ctk.CTkLabel(form_card, text="", font=("Arial", 10),
                                             text_color="#FF6B6B")
                    error_label.pack(fill="x", padx=20, pady=(0, 10))

                    def process_donation():
                        amount_str = amount_entry.get().strip()
                        message = message_entry.get("0.0", "end").strip()
                        error_label.configure(text="")

                        is_valid, msg, amount = validate_amount(amount_str)

                        if not is_valid:
                            error_label.configure(text=msg)
                            return

                        if not self.current_campaign_for_donation:
                            error_label.configure(text="No campaign selected")
                            return

                        success, msg, donation_id = create_donation(
                            self.user_data['id'], self.current_campaign_for_donation, amount, message
                        )

                        if success:
                            self.last_donation_amount = amount
                            self.last_donation_campaign = self.current_campaign_for_donation
                            self.show_acknowledgement = True
                            self.show_donation_screen()
                        else:
                            error_label.configure(text=msg)

                    button_frame = ctk.CTkFrame(form_card, fg_color="transparent")
                    button_frame.pack(fill="x", padx=20, pady=(0, 20))

                    donate_btn = ctk.CTkButton(button_frame, text="💳 Confirm Donation", height=45,
                                             font=("Arial", 13), command=process_donation,
                                             fg_color="#5B72EE", hover_color="#4A5FD8")
                    donate_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

                    def cancel_donation():
                        self.show_acknowledgement = False
                        self.current_campaign_for_donation = None
                        self.show_campaign_list()

                    cancel_btn = ctk.CTkButton(button_frame, text="Cancel", height=45,
                                             font=("Arial", 13), command=cancel_donation,
                                             fg_color="white", text_color="#6B7280",
                                             border_width=2, border_color="#E5E7EB")
                    cancel_btn.pack(side="left", fill="x", expand=True)
            else:
                ctk.CTkLabel(content, text="No campaign selected. Please select a campaign to donate.",
                            font=("Arial", 14), text_color="#9CA3AF").pack(pady=20)

                back_btn = ctk.CTkButton(content, text="← Back to Campaigns", height=45,
                                        fg_color="#5B72EE", hover_color="#4A5FD8",
                                        font=("Arial", 14),
                                        command=self.show_campaign_list)
                back_btn.pack(fill="x", padx=20)

    def show_impact_screen(self):
        """Display impact/donations history screen"""
        self.clear_window()
        self.create_header("Your Impact", "Track your donations and contribution")
        self.create_navbar("impact")

        content = ctk.CTkScrollableFrame(self, fg_color="#F5F7FA")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        donations = get_user_donations(self.user_data['id'])

        timeline_card = ctk.CTkFrame(content, fg_color="white", corner_radius=12)
        timeline_card.pack(fill="both", expand=True)

        ctk.CTkLabel(timeline_card, text="Donation Timeline",
                    font=("Arial", 18, "bold"), text_color="#1F2937",
                    anchor="w").pack(fill="x", padx=20, pady=(20, 15))

        if not donations:
            ctk.CTkLabel(timeline_card, text="No donations yet. Start supporting campaigns!",
                        font=("Arial", 12), text_color="#9CA3AF",
                        anchor="center").pack(fill="both", expand=True)
            return

        for donation in donations:
            donation_item = ctk.CTkFrame(timeline_card, fg_color="transparent")
            donation_item.pack(fill="x", padx=20, pady=8)

            dot = ctk.CTkLabel(donation_item, text="●", font=("Arial", 20),
                             text_color="#5B72EE", width=30)
            dot.pack(side="left")

            info_frame = ctk.CTkFrame(donation_item, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(info_frame, text=donation['campaign_title'], font=("Arial", 13, "bold"),
                        text_color="#1F2937", anchor="w").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=str(donation['donation_date']), font=("Arial", 11),
                        text_color="#9CA3AF", anchor="w").pack(anchor="w")

            ctk.CTkLabel(donation_item, text=f"${donation['amount']:.2f}",
                        font=("Arial", 14, "bold"), text_color="#10B981").pack(side="right", padx=10)

    def show_profile_screen(self):
        """Display user profile screen"""
        self.clear_window()
        self.create_header("My Profile", "Manage your account settings")
        self.create_navbar("profile")

        content = ctk.CTkScrollableFrame(self, fg_color="#F5F7FA")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        success, full_user_data = get_user_by_id(self.user_data['id'])

        profile_card = ctk.CTkFrame(content, fg_color="white", corner_radius=16)
        profile_card.pack(fill="x", pady=(0, 20))

        header_frame = ctk.CTkFrame(profile_card, fg_color="#5B72EE", corner_radius=16, height=120)
        header_frame.pack(fill="x", padx=0, pady=0)

        avatar_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        avatar_frame.pack(pady=(60, 20))

        initials = f"{self.user_data['first_name'][0]}{self.user_data['last_name'][0]}".upper()

        avatar = ctk.CTkLabel(avatar_frame, text=initials,
                             font=("Arial", 32, "bold"),
                             fg_color="#5B72EE", text_color="white",
                             width=100, height=100, corner_radius=50)
        avatar.pack()

        ctk.CTkLabel(profile_card, text=f"{self.user_data['first_name']} {self.user_data['last_name']}",
                    font=("Arial", 24, "bold"), text_color="#1F2937").pack(pady=(10, 5))
        ctk.CTkLabel(profile_card, text=self.user_data['email'], font=("Arial", 13),
                    text_color="#6B7280").pack(pady=(0, 20))

        stats_container = ctk.CTkFrame(profile_card, fg_color="transparent")
        stats_container.pack(fill="x", padx=40, pady=(0, 30))

        total_donations = get_user_total_donations(self.user_data['id'])
        user_donations_list = get_user_donations(self.user_data['id'])
        campaigns_joined = len(set(d['campaign_id'] for d in user_donations_list))

        member_since = full_user_data.get('created_at', datetime.now())
        if member_since:
            member_since = str(member_since).split()[0]
        else:
            member_since = datetime.now().strftime("%Y-%m-%d")

        quick_stats = [
            ("Total Donations", f"${total_donations:.2f}"),
            ("Campaigns Joined", str(campaigns_joined)),
            ("Member Since", member_since)
        ]

        for label, value in quick_stats:
            stat_box = ctk.CTkFrame(stats_container, fg_color="#F9FAFB", corner_radius=10)
            stat_box.pack(side="left", fill="x", expand=True, padx=5)

            ctk.CTkLabel(stat_box, text=value, font=("Arial", 20, "bold"),
                        text_color="#1F2937").pack(pady=(15, 5))
            ctk.CTkLabel(stat_box, text=label, font=("Arial", 11),
                        text_color="#6B7280").pack(pady=(0, 15))

        info_card = ctk.CTkFrame(content, fg_color="white", corner_radius=16)
        info_card.pack(fill="x", pady=10)

        ctk.CTkLabel(info_card, text="Personal Information",
                    font=("Arial", 18, "bold"), text_color="#1F2937",
                    anchor="w").pack(fill="x", padx=30, pady=(25, 20))

        fields = [
            ("First Name", full_user_data.get('first_name', '')),
            ("Last Name", full_user_data.get('last_name', '')),
            ("Email", full_user_data.get('email', '')),
            ("Phone", full_user_data.get('phone', '')),
            ("Address", full_user_data.get('address', '')),
        ]

        entry_fields = {}
        for label, value in fields:
            field_frame = ctk.CTkFrame(info_card, fg_color="transparent")
            field_frame.pack(fill="x", padx=30, pady=8)
            
            ctk.CTkLabel(field_frame, text=label, font=("Arial", 12),
                        text_color="#6B7280", anchor="w").pack(fill="x", pady=(0, 5))
            entry = ctk.CTkEntry(field_frame, height=45, font=("Arial", 13), corner_radius=8)
            entry.insert(0, value if value else "")
            entry.pack(fill="x")
            entry_fields[label] = entry
        
        button_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(20, 30))
        
        def save_changes():
            try:
                success, msg = update_user(
                    self.user_data['id'],
                    first_name=entry_fields["First Name"].get(),
                    last_name=entry_fields["Last Name"].get(),
                    phone=entry_fields["Phone"].get(),
                    address=entry_fields["Address"].get()
                )
                
                if success:
                    messagebox.showinfo("Success", "Profile updated successfully!")
                    self.show_profile_screen()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Error updating profile: {str(e)}")
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Save Changes", height=45,
                                fg_color="#5B72EE", hover_color="#4A5FD8",
                                font=("Arial", 14, "bold"), corner_radius=8,
                                width=150, command=save_changes)
        save_btn.pack(side="left", padx=(0, 10))

if __name__ == "__main__":
    test_user = {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@test.com',
        'role': 'donor'
    }
    app = DonorApp(test_user)
    app.mainloop()