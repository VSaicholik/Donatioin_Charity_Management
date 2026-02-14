
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
from PIL import Image

# PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: reportlab not installed. PDF reports will be saved as images.")

from utils import (
    get_dashboard_stats, get_all_campaigns, create_campaign,
    update_campaign, get_campaign_donations, get_campaign_stats,
    get_db_connection, close_connection, get_user_donations
)

from config import CATEGORIES


class AdminDashboard(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.current_view = "dashboard"  # Track current view
        self.title("Admin Dashboard - Donation Management System")
        self.geometry("1200x800")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Create reports folder if it doesn't exist
        if not os.path.exists("reports"):
            os.makedirs("reports")

        self.show_dashboard()

    def clear_window(self):
        """Clear all widgets"""
        for widget in self.winfo_children():
            widget.destroy()

    def create_header(self):
        """Create admin dashboard header with navigation"""
        header = ctk.CTkFrame(self, height=70, fg_color="#3D4A5C", corner_radius=0)
        header.pack(fill="x")

        # Left side - User info and nav buttons
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
        
        ctk.CTkLabel(info_frame, text="Admin Dashboard",
                    font=("Arial", 18, "bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"Welcome back, {self.user_data['first_name']}",
                    font=("Arial", 12), text_color="#B0B8C1").pack(anchor="w")

        # Middle - Navigation buttons
        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="left", padx=30)

        dashboard_btn = ctk.CTkButton(nav_frame, text="📊 Dashboard", width=120, height=45,
                                     fg_color="#5B72EE" if self.current_view == "dashboard" else "#4A5766",
                                     hover_color="#5B72EE",
                                     corner_radius=10, font=("Arial", 11),
                                     command=self.show_dashboard)
        dashboard_btn.pack(side="left", padx=5)

        reports_btn = ctk.CTkButton(nav_frame, text="📈 Reports", width=120, height=45,
                                   fg_color="#7C3AED" if self.current_view == "reports" else "#4A5766",
                                   hover_color="#7C3AED",
                                   corner_radius=10, font=("Arial", 11),
                                   command=self.show_reports)
        reports_btn.pack(side="left", padx=5)

        # Right side - Logout button
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=10)

        logout_btn = ctk.CTkButton(right_frame, text="🚪 Logout", width=100, height=45,
                                  fg_color="#FF6B6B", hover_color="#FF5252",
                                  corner_radius=10, font=("Arial", 12),
                                  command=self.logout)
        logout_btn.pack(side="right")

    def show_dashboard(self):
        """Display admin dashboard"""
        self.current_view = "dashboard"
        self.clear_window()
        self.create_header()

        content = ctk.CTkScrollableFrame(self, fg_color="#F5F7FA")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        stats = get_dashboard_stats()

        stats_frame = ctk.CTkFrame(content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        stat_cards = [
            ("💵", "Total Donations", f"${stats['total_donations']:.0f}", "This month", "+18.2%", "#10B981"),
            ("📋", "Active Campaigns", str(stats['active_campaigns']), "3 ending soon", "Active", "#5B72EE"),
            ("👥", "Registered Donors", str(stats['total_donors']), "847 new this month", "+12.8%", "#7C3AED"),
            ("❤️", "Beneficiaries", str(stats['total_beneficiaries']), "1,234 this month", "Lives", "#F59E0B")
        ]

        for icon, title, value, subtitle, badge, color in stat_cards:
            card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12)
            card.pack(side="left", fill="both", expand=True, padx=5)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=20, pady=15)

            icon_label = ctk.CTkLabel(top, text=icon, font=("Arial", 22),
                                      fg_color=color, text_color="white",
                                      width=45, height=45, corner_radius=8)
            icon_label.pack(side="left")

            badge_label = ctk.CTkLabel(top, text=badge, font=("Arial", 10),
                                      fg_color="#E8F5E9" if "+" in badge else "#E8EEFF",
                                      text_color=color,
                                      corner_radius=12, padx=10, pady=4)
            badge_label.pack(side="right")

            ctk.CTkLabel(card, text=title, font=("Arial", 11),
                        text_color="#6B7280", anchor="w").pack(fill="x", padx=20, pady=(0, 5))
            ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"),
                        text_color="#1F2937", anchor="w").pack(fill="x", padx=20, pady=(0, 5))
            ctk.CTkLabel(card, text=subtitle, font=("Arial", 10),
                        text_color="#9CA3AF", anchor="w").pack(fill="x", padx=20, pady=(0, 15))

        campaigns_card = ctk.CTkFrame(content, fg_color="white", corner_radius=12)
        campaigns_card.pack(fill="both", expand=True, pady=(20, 0))

        header_frame = ctk.CTkFrame(campaigns_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 15))

        ctk.CTkLabel(header_frame, text="Top Performing Campaigns",
                    font=("Arial", 18, "bold"), text_color="#1F2937",
                    anchor="w").pack(side="left")

        add_campaign_btn = ctk.CTkButton(header_frame, text="+ New Campaign", height=35,
                                        fg_color="#5B72EE", hover_color="#4A5FD8",
                                        font=("Arial", 11),
                                        command=self.show_create_campaign)
        add_campaign_btn.pack(side="right")

        campaigns = get_all_campaigns()

        if not campaigns:
            ctk.CTkLabel(campaigns_card, text="No campaigns yet. Create one to get started!",
                        font=("Arial", 12), text_color="#9CA3AF",
                        anchor="center").pack(fill="both", expand=True, pady=30)
        else:
            campaigns_scroll = ctk.CTkScrollableFrame(campaigns_card, fg_color="transparent")
            campaigns_scroll.pack(fill="both", expand=True, padx=20, pady=10)

            for campaign in campaigns[:5]:
                stats_campaign = get_campaign_stats(campaign['id'])
                percent = stats_campaign.get('percentage', 0)

                camp_frame = ctk.CTkFrame(campaigns_scroll, fg_color="#F9FAFB", corner_radius=10)
                camp_frame.pack(fill="x", padx=0, pady=8)

                header = ctk.CTkFrame(camp_frame, fg_color="transparent")
                header.pack(fill="x", padx=15, pady=(12, 8))

                ctk.CTkLabel(header, text=campaign['title'], font=("Arial", 14, "bold"),
                            text_color="#1F2937", anchor="w").pack(side="left", fill="x", expand=True)

                donor_label = ctk.CTkLabel(header, text=f"{stats_campaign.get('donors_count', 0)} donors",
                                          font=("Arial", 11), text_color="#6B7280")
                donor_label.pack(side="right", padx=(0, 15))

                ctk.CTkLabel(header, text=f"{percent:.0f}%", font=("Arial", 13, "bold"),
                            text_color="#1F2937").pack(side="right")

                ctk.CTkLabel(camp_frame, text="Progress", font=("Arial", 10),
                            text_color="#6B7280", anchor="w").pack(fill="x", padx=15, pady=(0, 5))

                bar_container = ctk.CTkFrame(camp_frame, fg_color="transparent")
                bar_container.pack(fill="x", padx=15, pady=(0, 8))

                bar_bg = ctk.CTkFrame(bar_container, height=8, fg_color="#E5E7EB", corner_radius=4)
                bar_bg.pack(fill="x")

                bar_fill = ctk.CTkFrame(bar_bg, fg_color="#D97706", corner_radius=4)
                bar_fill.place(relx=0, rely=0, relwidth=min(percent/100, 1.0), relheight=1)

                amount_frame = ctk.CTkFrame(camp_frame, fg_color="transparent")
                amount_frame.pack(fill="x", padx=15, pady=(0, 12))

                current = stats_campaign.get('current_amount', 0)
                goal = stats_campaign.get('goal_amount', 0)

                ctk.CTkLabel(amount_frame, text=f"${current:.0f}", font=("Arial", 14, "bold"),
                            text_color="#1F2937").pack(side="left")
                ctk.CTkLabel(amount_frame, text=f"of ${goal:.0f}", font=("Arial", 11),
                            text_color="#6B7280").pack(side="left", padx=(5, 0))

                def view_details(cid=campaign['id']):
                    self.show_campaign_details(cid)

                detail_btn = ctk.CTkButton(amount_frame, text="View Details", height=30, width=100,
                                          fg_color="#E8EEFF", text_color="#5B72EE",
                                          hover_color="#D8DEFF", font=("Arial", 10),
                                          command=view_details)
                detail_btn.pack(side="right")

    def show_reports(self):
        """Display reports page with charts and statistics"""
        self.current_view = "reports"
        self.clear_window()
        self.create_header()

        content = ctk.CTkScrollableFrame(self, fg_color="#F5F7FA")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(content, text="📊 Donation Reports & Analytics",
                    font=("Arial", 22, "bold"), text_color="#1F2937").pack(anchor="w", pady=(0, 20))

        # Get statistics
        stats = get_dashboard_stats()
        campaigns = get_all_campaigns()

        # Report buttons
        button_frame = ctk.CTkFrame(content, fg_color="white", corner_radius=12)
        button_frame.pack(fill="x", padx=0, pady=(0, 20))

        ctk.CTkLabel(button_frame, text="Generate & Download Reports (PDF)",
                    font=("Arial", 14, "bold"), text_color="#1F2937",
                    anchor="w").pack(fill="x", padx=20, pady=(15, 10))

        btn_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(0, 20))

        btn1 = ctk.CTkButton(btn_container, text="📈 Donation Trends", height=40,
                            fg_color="#5B72EE", hover_color="#4A5FD8",
                            command=self.generate_donation_trends)
        btn1.pack(side="left", padx=5, fill="x", expand=True)

        btn2 = ctk.CTkButton(btn_container, text="🥧 Campaign Performance", height=40,
                            fg_color="#7C3AED", hover_color="#6D28D9",
                            command=self.generate_campaign_performance)
        btn2.pack(side="left", padx=5, fill="x", expand=True)

        btn3 = ctk.CTkButton(btn_container, text="👥 Donor Statistics", height=40,
                            fg_color="#10B981", hover_color="#059669",
                            command=self.generate_donor_stats)
        btn3.pack(side="left", padx=5, fill="x", expand=True)

        btn4 = ctk.CTkButton(btn_container, text="📋 Full Report", height=40,
                            fg_color="#F59E0B", hover_color="#D97706",
                            command=self.generate_full_report)
        btn4.pack(side="left", padx=5, fill="x", expand=True)

        # Statistics section
        stats_card = ctk.CTkFrame(content, fg_color="white", corner_radius=12)
        stats_card.pack(fill="x", padx=0, pady=(0, 20))

        ctk.CTkLabel(stats_card, text="Key Statistics",
                    font=("Arial", 14, "bold"), text_color="#1F2937",
                    anchor="w").pack(fill="x", padx=20, pady=(15, 10))

        stats_data = [
            ("Total Donations", f"${stats['total_donations']:.2f}"),
            ("Total Donors", f"{stats['total_donors']} users"),
            ("Active Campaigns", f"{stats['active_campaigns']} campaigns"),
            ("Average Donation", f"${stats['total_donations']/max(stats['total_donors'], 1):.2f}")
        ]

        for label, value in stats_data:
            row = ctk.CTkFrame(stats_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)

            ctk.CTkLabel(row, text=label, font=("Arial", 12),
                        text_color="#6B7280", anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=value, font=("Arial", 12, "bold"),
                        text_color="#1F2937", anchor="e").pack(side="right")

        # Download folder info
        info_card = ctk.CTkFrame(content, fg_color="#E8F5FF", corner_radius=10)
        info_card.pack(fill="x", padx=0)

        ctk.CTkLabel(info_card, text="ℹ️ Reports are saved to the 'reports' folder in your project directory. All reports are generated as PDF files.",
                    font=("Arial", 11), text_color="#0369A1").pack(padx=15, pady=15, anchor="w")

    def generate_donation_trends(self):
        """Generate donation trends PDF report"""
        try:
            campaigns = get_all_campaigns()
            
            if PDF_AVAILABLE:
                # Create PDF
                filename = f"reports/donation_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = []
                
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=20,
                    textColor=colors.HexColor('#1F2937'),
                    spaceAfter=30,
                    alignment=TA_CENTER
                )
                
                elements.append(Paragraph("Donation Trends Report", title_style))
                elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                         styles['Normal']))
                elements.append(Spacer(1, 0.3 * inch))
                
                # Create campaign data table
                elements.append(Paragraph("Top Campaigns by Donations", styles['Heading2']))
                
                campaign_data = [['Campaign Name', 'Current Amount', 'Goal Amount', 'Progress %', 'Donors']]
                for campaign in campaigns[:10]:
                    stats = get_campaign_stats(campaign['id'])
                    campaign_data.append([
                        campaign['title'][:30],
                        f"${stats['current_amount']:.2f}",
                        f"${stats['goal_amount']:.2f}",
                        f"{stats['percentage']:.1f}%",
                        str(stats['donors_count'])
                    ])
                
                table = Table(campaign_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1*inch, 0.6*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5B72EE')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.3 * inch))
                
                # Add summary statistics
                stats = get_dashboard_stats()
                elements.append(Paragraph("Summary Statistics", styles['Heading2']))
                
                summary_data = [
                    ['Metric', 'Value'],
                    ['Total Donations', f"${stats['total_donations']:.2f}"],
                    ['Total Donors', str(stats['total_donors'])],
                    ['Active Campaigns', str(stats['active_campaigns'])],
                    ['Average Donation', f"${stats['total_donations']/max(stats['total_donors'], 1):.2f}"]
                ]
                
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5B72EE')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(summary_table)
                
                doc.build(elements)
                messagebox.showinfo("Success", f"Report saved to:\n{filename}")
            else:
                messagebox.showwarning("Info", "PDF library not installed. Install reportlab: pip install reportlab")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")

    def generate_campaign_performance(self):
        """Generate campaign performance PDF report"""
        try:
            campaigns = get_all_campaigns()
            
            if PDF_AVAILABLE:
                filename = f"reports/campaign_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = []
                
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=20,
                    textColor=colors.HexColor('#1F2937'),
                    spaceAfter=30,
                    alignment=TA_CENTER
                )
                
                elements.append(Paragraph("Campaign Performance Report", title_style))
                elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                         styles['Normal']))
                elements.append(Spacer(1, 0.3 * inch))
                
                # Create campaign performance table
                elements.append(Paragraph("Campaign Performance Summary", styles['Heading2']))
                
                perf_data = [['Campaign', 'Category', 'Status', 'Goal', 'Raised', 'Progress', 'Donors']]
                for campaign in campaigns[:12]:
                    stats = get_campaign_stats(campaign['id'])
                    perf_data.append([
                        campaign['title'][:20],
                        campaign['category'][:15],
                        campaign['status'],
                        f"${stats['goal_amount']:.0f}",
                        f"${stats['current_amount']:.0f}",
                        f"{stats['percentage']:.0f}%",
                        str(stats['donors_count'])
                    ])
                
                table = Table(perf_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F4F6')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                elements.append(table)
                
                doc.build(elements)
                messagebox.showinfo("Success", f"Report saved to:\n{filename}")
            else:
                messagebox.showwarning("Info", "PDF library not installed. Install reportlab: pip install reportlab")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")

    def generate_donor_stats(self):
        """Generate donor statistics PDF report"""
        try:
            stats = get_dashboard_stats()
            campaigns = get_all_campaigns()
            
            if PDF_AVAILABLE:
                filename = f"reports/donor_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = []
                
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=20,
                    textColor=colors.HexColor('#1F2937'),
                    spaceAfter=30,
                    alignment=TA_CENTER
                )
                
                elements.append(Paragraph("Donor Statistics Report", title_style))
                elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                         styles['Normal']))
                elements.append(Spacer(1, 0.3 * inch))
                
                # Summary Stats
                summary_text = f"""
                <b>Total Donors:</b> {stats['total_donors']} users<br/>
                <b>Active Campaigns:</b> {stats['active_campaigns']} campaigns<br/>
                <b>Total Beneficiaries:</b> {stats['total_beneficiaries']} people<br/>
                <b>Total Donations:</b> ${stats['total_donations']:.2f}<br/>
                <b>Average Donation per User:</b> ${stats['total_donations']/max(stats['total_donors'], 1):.2f}<br/>
                <b>Campaigns with Donations:</b> {len([c for c in campaigns if get_campaign_stats(c['id'])['current_amount'] > 0])}
                """
                
                elements.append(Paragraph(summary_text, styles['Normal']))
                elements.append(Spacer(1, 0.3 * inch))
                
                # Top campaigns
                elements.append(Paragraph("Top Campaigns by Donations", styles['Heading2']))
                
                campaign_data = [['Rank', 'Campaign Name', 'Total Donations', 'Donor Count']]
                campaign_sorted = sorted([(c['title'], get_campaign_stats(c['id'])['current_amount'], 
                                          get_campaign_stats(c['id'])['donors_count']) for c in campaigns],
                                        key=lambda x: x[1], reverse=True)
                
                for i, (name, amount, donor_count) in enumerate(campaign_sorted[:10], 1):
                    campaign_data.append([str(i), name[:40], f"${amount:.2f}", str(donor_count)])
                
                table = Table(campaign_data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECFDF5')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                
                doc.build(elements)
                messagebox.showinfo("Success", f"Report saved to:\n{filename}")
            else:
                messagebox.showwarning("Info", "PDF library not installed. Install reportlab: pip install reportlab")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")

    def generate_full_report(self):
        """Generate comprehensive full PDF report"""
        try:
            stats = get_dashboard_stats()
            campaigns = get_all_campaigns()
            
            if PDF_AVAILABLE:
                filename = f"reports/full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = []
                
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#1F2937'),
                    spaceAfter=10,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                )
                
                subtitle_style = ParagraphStyle(
                    'Subtitle',
                    parent=styles['Normal'],
                    fontSize=12,
                    textColor=colors.HexColor('#6B7280'),
                    alignment=TA_CENTER,
                    spaceAfter=30
                )
                
                # Title
                elements.append(Paragraph("DONATION MANAGEMENT SYSTEM", title_style))
                elements.append(Paragraph("Comprehensive Report", subtitle_style))
                elements.append(Spacer(1, 0.2 * inch))
                
                # Executive Summary
                elements.append(Paragraph("Executive Summary", styles['Heading2']))
                
                summary_text = f"""
                This report provides a comprehensive overview of the donation management system as of {datetime.now().strftime('%B %d, %Y')}.<br/><br/>
                <b>Key Metrics:</b><br/>
                • Total Platform Value: ${stats['total_donations']:.2f}<br/>
                • Active Fundraisers: {stats['active_campaigns']}<br/>
                • Community Members: {stats['total_donors']}<br/>
                • Lives Impacted: {stats['total_beneficiaries']}<br/>
                • Average Donation: ${stats['total_donations']/max(stats['total_donors'], 1):.2f}<br/>
                """
                
                elements.append(Paragraph(summary_text, styles['Normal']))
                elements.append(Spacer(1, 0.2 * inch))
                
                # Campaign Overview
                elements.append(Paragraph("Campaign Overview", styles['Heading2']))
                
                camp_data = [['Campaign', 'Category', 'Status', 'Goal', 'Raised', 'Progress %', 'Donors']]
                for campaign in campaigns[:8]:
                    stats_c = get_campaign_stats(campaign['id'])
                    camp_data.append([
                        campaign['title'][:25],
                        campaign['category'][:12],
                        campaign['status'],
                        f"${stats_c['goal_amount']:.0f}",
                        f"${stats_c['current_amount']:.0f}",
                        f"{stats_c['percentage']:.0f}%",
                        str(stats_c['donors_count'])
                    ])
                
                camp_table = Table(camp_data, colWidths=[1.4*inch, 0.9*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.5*inch])
                camp_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FEF3C7')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                
                elements.append(camp_table)
                elements.append(Spacer(1, 0.3 * inch))
                
                # Report footer
                footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Admin Dashboard"
                elements.append(Paragraph(footer_text, styles['Normal']))
                
                doc.build(elements)
                messagebox.showinfo("Success", f"Full report saved to:\n{filename}")
            else:
                messagebox.showwarning("Info", "PDF library not installed. Install reportlab: pip install reportlab")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")

    def show_create_campaign(self):
        """Show campaign creation form"""
        create_window = ctk.CTkToplevel(self)
        create_window.title("Create New Campaign")
        create_window.geometry("600x700")

        frame = ctk.CTkFrame(create_window, fg_color="#F5F7FA")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Create New Campaign", font=("Arial", 20, "bold"),
                    text_color="#1F2937").pack(pady=(0, 20))

        ctk.CTkLabel(frame, text="Campaign Title *", font=("Arial", 12),
                    text_color="#1F2937", anchor="w").pack(fill="x", pady=(0, 5))
        title_entry = ctk.CTkEntry(frame, placeholder_text="Enter campaign title", height=40, corner_radius=8)
        title_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Description *", font=("Arial", 12),
                    text_color="#1F2937", anchor="w").pack(fill="x", pady=(0, 5))
        desc_entry = ctk.CTkTextbox(frame, height=100, corner_radius=8)
        desc_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Goal Amount ($) *", font=("Arial", 12),
                    text_color="#1F2937", anchor="w").pack(fill="x", pady=(0, 5))
        goal_entry = ctk.CTkEntry(frame, placeholder_text="Enter goal amount", height=40, corner_radius=8)
        goal_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Category *", font=("Arial", 12),
                    text_color="#1F2937", anchor="w").pack(fill="x", pady=(0, 5))
        category_var = ctk.StringVar(value=CATEGORIES[0])
        category_menu = ctk.CTkOptionMenu(frame, values=CATEGORIES, variable=category_var,
                                         height=40, font=("Arial", 12))
        category_menu.pack(fill="x", pady=(0, 15))

        error_label = ctk.CTkLabel(frame, text="", font=("Arial", 10),
                                  text_color="#FF6B6B")
        error_label.pack(fill="x", pady=(0, 10))

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        def create():
            title = title_entry.get().strip()
            desc = desc_entry.get("0.0", "end").strip()
            goal_str = goal_entry.get().strip()
            category = category_var.get()

            error_label.configure(text="")

            if not title or not desc or not goal_str:
                error_label.configure(text="Please fill in all required fields")
                return

            try:
                goal = float(goal_str)
                if goal <= 0:
                    error_label.configure(text="Goal amount must be greater than 0")
                    return
            except ValueError:
                error_label.configure(text="Invalid goal amount")
                return

            success, msg, campaign_id = create_campaign(
                title, desc, goal, category, self.user_data['id'], None, None
            )

            if success:
                messagebox.showinfo("Success", f"Campaign created successfully!")
                create_window.destroy()
                self.show_dashboard()
            else:
                error_label.configure(text=msg)

        create_btn = ctk.CTkButton(button_frame, text="Create Campaign", height=45,
                                  fg_color="#5B72EE", hover_color="#4A5FD8",
                                  font=("Arial", 13, "bold"), command=create)
        create_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", height=45,
                                  fg_color="white", text_color="#6B7280",
                                  hover_color="#F3F4F6", font=("Arial", 13),
                                  border_width=2, border_color="#E5E7EB",
                                  command=create_window.destroy)
        cancel_btn.pack(side="left", fill="x", expand=True)

    def show_campaign_details(self, campaign_id):
        """Show detailed campaign view"""
        from utils import get_campaign_by_id
        
        campaign = get_campaign_by_id(campaign_id)
        if not campaign:
            messagebox.showerror("Error", "Campaign not found")
            return

        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Campaign Details - {campaign['title']}")
        details_window.geometry("700x800")

        frame = ctk.CTkScrollableFrame(details_window, fg_color="#F5F7FA")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=campaign['title'], font=("Arial", 22, "bold"),
                    text_color="#1F2937").pack(anchor="w", pady=(0, 10))

        stats = get_campaign_stats(campaign_id)

        stats_frame = ctk.CTkFrame(frame, fg_color="white", corner_radius=12)
        stats_frame.pack(fill="x", pady=(0, 15))

        stats_data = [
            ("Goal Amount", f"${stats.get('goal_amount', 0):.2f}"),
            ("Current Amount", f"${stats.get('current_amount', 0):.2f}"),
            ("Progress", f"{stats.get('percentage', 0):.1f}%"),
            ("Total Donors", str(stats.get('donors_count', 0)))
        ]

        for label, value in stats_data:
            row_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=8)

            ctk.CTkLabel(row_frame, text=label, font=("Arial", 12),
                        text_color="#6B7280", anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row_frame, text=value, font=("Arial", 12, "bold"),
                        text_color="#1F2937", anchor="e").pack(side="right")

        donations = get_campaign_donations(campaign_id)

        ctk.CTkLabel(frame, text="Recent Donations", font=("Arial", 14, "bold"),
                    text_color="#1F2937", anchor="w").pack(fill="x", pady=(15, 10))

        if not donations:
            ctk.CTkLabel(frame, text="No donations yet",
                        font=("Arial", 11), text_color="#9CA3AF").pack(pady=10)
        else:
            for donation in donations[:10]:
                donation_item = ctk.CTkFrame(frame, fg_color="white", corner_radius=8)
                donation_item.pack(fill="x", padx=0, pady=5)

                info = ctk.CTkFrame(donation_item, fg_color="transparent")
                info.pack(fill="x", padx=10, pady=8)

                ctk.CTkLabel(info, text=donation['donor_name'], font=("Arial", 11, "bold"),
                            text_color="#1F2937", anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(info, text=f"${donation['amount']:.2f}", font=("Arial", 11, "bold"),
                            text_color="#10B981", anchor="e").pack(side="right")

    def logout(self):
        """Logout function"""
        from login_register_screens import AuthScreen

        self.destroy()
        app = AuthScreen()
        app.mainloop()


if __name__ == "__main__":
    test_user = {
        'id': 1,
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@test.com',
        'role': 'admin'
    }

    app = AdminDashboard(test_user)
    app.mainloop()