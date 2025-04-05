import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.attendance_controller import AttendanceController
from db.db_manager import DBManager

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Church School Attendance System")
        self.root.geometry("800x600")
        
        # Initialize database and controller
        self.db = DBManager("church_school.db")
        self.controller = AttendanceController(self.db)
        
        self.create_login_frame()
        
    def create_login_frame(self):
        self.login_frame = ttk.Frame(self.root, padding="10")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(self.login_frame, text="Login", command=self.handle_login).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(self.login_frame, text="Sign Up", command=self.show_signup).grid(row=3, column=0, columnspan=2)
        
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        user = self.controller.login(username, password)
        if user:
            self.login_frame.destroy()
            if user['role'].lower() == 'student':
                self.create_student_dashboard(user)
            else:
                self.create_admin_dashboard(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            
    def create_student_dashboard(self, user):
        self.dashboard_frame = ttk.Frame(self.root, padding="10")
        self.dashboard_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Welcome message
        welcome_label = ttk.Label(
            self.dashboard_frame,
            text=f"Welcome, {user['first_name']} {user['last_name']}!\nStudent ID: {user['student_id']}"
        )
        welcome_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Record attendance button
        ttk.Button(
            self.dashboard_frame,
            text="Record Today's Attendance",
            command=lambda: self.record_attendance(user['student_id'])
        ).grid(row=1, column=0, pady=5)
        
        # View attendance history button
        ttk.Button(
            self.dashboard_frame,
            text="View Attendance History",
            command=lambda: self.show_attendance_history(user['student_id'])
        ).grid(row=2, column=0, pady=5)
        
        # Logout button
        ttk.Button(
            self.dashboard_frame,
            text="Logout",
            command=self.logout
        ).grid(row=3, column=0, pady=5)
        
    def create_admin_dashboard(self, user):
        self.dashboard_frame = ttk.Frame(self.root, padding="10")
        self.dashboard_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Welcome message
        welcome_label = ttk.Label(
            self.dashboard_frame,
            text=f"Welcome, {user['first_name']} {user['last_name']}!"
        )
        welcome_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Set attendance time button
        ttk.Button(
            self.dashboard_frame,
            text="Set Expected Arrival Time",
            command=self.show_set_time_dialog
        ).grid(row=1, column=0, pady=5)
        
        # Generate report button
        ttk.Button(
            self.dashboard_frame,
            text="Generate Attendance Report",
            command=self.show_report_dialog
        ).grid(row=2, column=0, pady=5)
        
        # Logout button
        ttk.Button(
            self.dashboard_frame,
            text="Logout",
            command=self.logout
        ).grid(row=3, column=0, pady=5)
        
    def record_attendance(self, student_id):
        if self.controller.record_attendance(student_id):
            status = self.controller.get_daily_attendance_status(student_id)
            if status['status'] == 'late':
                messagebox.showinfo(
                    "Attendance Recorded",
                    f"Attendance recorded - Late arrival at {status['sign_in_time']}"
                )
            else:
                messagebox.showinfo(
                    "Attendance Recorded",
                    f"Attendance recorded - On time at {status['sign_in_time']}"
                )
        else:
            messagebox.showerror("Error", "Failed to record attendance")
            
    def show_attendance_history(self, student_id):
        history_window = tk.Toplevel(self.root)
        history_window.title("Attendance History")
        history_window.geometry("600x400")
        
        # Create treeview
        columns = ('date', 'status', 'time')
        tree = ttk.Treeview(history_window, columns=columns, show='headings')
        
        # Define headings
        tree.heading('date', text='Date')
        tree.heading('status', text='Status')
        tree.heading('time', text='Time')
        
        # Add data
        records = self.controller.get_student_attendance(student_id)
        for record in records:
            tree.insert('', tk.END, values=(
                record['attendance_date'],
                record['status'],
                record['sign_in_time']
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
    def show_set_time_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Expected Arrival Time")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Hour (0-23):").grid(row=0, column=0, padx=5, pady=5)
        hour_spinbox = ttk.Spinbox(dialog, from_=0, to=23, width=5)
        hour_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Minute (0-59):").grid(row=1, column=0, padx=5, pady=5)
        minute_spinbox = ttk.Spinbox(dialog, from_=0, to=59, width=5)
        minute_spinbox.grid(row=1, column=1, padx=5, pady=5)
        
        def set_time():
            try:
                hour = int(hour_spinbox.get())
                minute = int(minute_spinbox.get())
                if self.controller.set_daily_attendance_time(hour, minute):
                    messagebox.showinfo("Success", "Expected arrival time updated")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update time")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        ttk.Button(dialog, text="Set Time", command=set_time).grid(row=2, column=0, columnspan=2, pady=10)
        
    def show_report_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Attendance Report")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        start_entry = ttk.Entry(dialog)
        start_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        end_entry = ttk.Entry(dialog)
        end_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def generate_report():
            start_date = start_entry.get()
            end_date = end_entry.get()
            records = self.controller.generate_late_report(start_date, end_date)
            
            if records:
                report_window = tk.Toplevel(self.root)
                report_window.title("Attendance Report")
                report_window.geometry("800x600")
                
                # Create treeview
                columns = ('date', 'student', 'status', 'time')
                tree = ttk.Treeview(report_window, columns=columns, show='headings')
                
                # Define headings
                tree.heading('date', text='Date')
                tree.heading('student', text='Student')
                tree.heading('status', text='Status')
                tree.heading('time', text='Time')
                
                # Add data
                for record in records:
                    tree.insert('', tk.END, values=(
                        record['attendance_date'],
                        f"{record['first_name']} {record['last_name']}",
                        record['status'],
                        record['sign_in_time'] if record['status'] == 'Late' else ''
                    ))
                
                tree.pack(fill=tk.BOTH, expand=True)
                dialog.destroy()
            else:
                messagebox.showinfo("No Data", "No attendance records found for this period")
        
        ttk.Button(dialog, text="Generate Report", command=generate_report).grid(row=2, column=0, columnspan=2, pady=10)
        
    def logout(self):
        self.controller.logout()
        self.dashboard_frame.destroy()
        self.create_login_frame()
        
    def show_signup(self):
        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")
        signup_window.geometry("400x300")
        
        # Add signup form fields and logic here
        # Similar to the login form but with more fields 