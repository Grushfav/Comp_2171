from db.db_manager import DBManager
from controllers.attendance_controller import AttendanceController
from controllers.auth_controller import AuthController
from controllers.course_controller import CourseController
from datetime import datetime, time

def display_menu(is_admin: bool):
    print("\nChurch School Attendance System")
    if not is_admin:
        print("1. Record Daily Attendance")
        print("2. View My Attendance")
        print("3. View Available Courses")
        print("4. Add/Drop Course")
        print("5. View Today's Attendance Status")
        print("6. Logout")

    else:
        print("1. Create New Course")
        print("2. View All Courses")
        print("3. Generate Course Report")
        print("4. View Student Attendance")
        print("5. Set Expected Arrival Time")
        print("6. Generate Late Attendance Report")
        print("7. Logout")

def handle_signup(auth_controller: AuthController):
    print("\nSign Up")
    role = input("Enter role (student/admin): ").lower()
    if role not in ['student', 'admin']:
        print("Invalid role!")
        return

    username = input("Enter username: ")
    password = input("Enter password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")

    if role == 'student':
        contact = input("Enter contact number: ")
        emergency = input("Enter emergency contact: ")
        if auth_controller.signup(username, password, first_name, last_name, 
                                email, role, contact, emergency):
            print("\nStudent registration successful!")
            print("Please log in to continue.")
    else:
        if auth_controller.signup(username, password, first_name, last_name, 
                                email, role):
            print("\nAdmin registration successful!")
            print("Please log in to continue.")

def handle_login(auth_controller: AuthController):
    print("\nLogin")
    username = input("Enter username: ")
    password = input("Enter password: ")
    user = auth_controller.login(username, password)
    if user:
        print(f"\nWelcome, {user['first_name']}!")
        if user.get('student_id'):
            print(f"Your Student ID is: {user['student_id']}")
            print(f"Role: Student")
        else:
            print(f"Role: {user['role'].capitalize()}")
        return user  # Return the user data
    print("Invalid credentials!")
    return None

def main():
    db = DBManager("church_school.db")
    db.initialize_db()
    
    auth_controller = AuthController(db)
    attendance_controller = AttendanceController(db)
    course_controller = CourseController(db)

    while True:
        if not auth_controller.get_current_user():
            print("\n1. Login")
            print("2. Sign Up")
            print("3. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                user = handle_login(auth_controller)
                if user:
                    # Share the complete user data with attendance controller
                    attendance_controller._current_user = user.copy()
                else:
                    continue
            elif choice == "2":
                handle_signup(auth_controller)
                continue
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice!")
                continue

        # User is logged in
        is_admin = auth_controller.is_admin()
        display_menu(is_admin)
        
        choice = input("Enter your choice: ")
        
        if is_admin:
            if choice == "1":
                # Create new course
                print("\nCreate New Course")
                name = input("Enter course name: ")
                desc = input("Enter description: ")
                start = input("Enter start date (YYYY-MM-DD): ")
                end = input("Enter end date (YYYY-MM-DD): ")
                loc = input("Enter location: ")
                cap = int(input("Enter maximum capacity: "))
                
                if course_controller.create_course(name, desc, start, end, loc, cap):
                    print("Course created successfully!")
                else:
                    print("Failed to create course.")

            elif choice == "2":
                # View all courses
                courses = course_controller.list_courses()
                print("\nAll Courses:")
                for course in courses:
                    print(f"\nCourse ID: {course['course_id']}")
                    print(f"Name: {course['course_name']}")
                    print(f"Location: {course['location']}")
                    print(f"Capacity: {course['max_capacity']}")

            elif choice == "3":
                course_id = int(input("Enter Course ID: "))
                report = attendance_controller.generate_course_report(course_id)
                if report:
                    print("\nCourse Report:")
                    print(f"Total Sessions: {report['total_sessions']}")
                    print(f"Present Count: {report['present_count']}")
                    print(f"Late Count: {report['late_count']}")

            elif choice == "4":
                student_id = int(input("Enter Student ID: "))
                records = attendance_controller.get_student_attendance(student_id)
                if records:
                    print("\nAttendance Records:")
                    for record in records:
                        print(f"Date: {record['attendance_date']}")
                        print(f"Course: {record['course_name']}")
                        print(f"Status: {record['status']}")
                        print("---")

            elif choice == "5":
                course_id = int(input("Enter Course ID: "))
                
                # Add validation for hour input
                while True:
                    try:
                        hour = int(input("Enter hour (0-23): "))
                        if 0 <= hour <= 23:
                            break
                        print("Hour must be between 0 and 23!")
                    except ValueError:
                        print("Please enter a valid number!")

                # Add validation for minute input
                while True:
                    try:
                        minute = int(input("Enter minute (0-59): "))
                        if 0 <= minute <= 59:
                            break
                        print("Minute must be between 0 and 59!")
                    except ValueError:
                        print("Please enter a valid number!")
                
                expected_time = time(hour, minute)
                
                if attendance_controller.set_daily_attendance_time(course_id, expected_time):
                    print(f"Successfully set attendance time to {expected_time.strftime('%H:%M')} for course {course_id}!")
                else:
                    print("Failed to set attendance time.")

            elif choice == "6":
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")
                attendance_records = attendance_controller.generate_late_report(start_date, end_date)
                
                if attendance_records:
                    print("\nAttendance Report")
                    print(f"Period: {start_date} to {end_date}")
                    print("-" * 50)
                    
                    current_date = None
                    for record in attendance_records:
                        # Print date header when date changes
                        if current_date != record['attendance_date']:
                            current_date = record['attendance_date']
                            print(f"\nDate: {current_date}")
                            print("-" * 30)
                        
                        # Print student attendance info
                        print(f"Student: {record['first_name']} {record['last_name']}")
                        print(f"Status: {record['status']}")
                        if record['status'] == 'Late':
                            print(f"Arrival Time: {record['sign_in_time']}")
                        print("---")
                else:
                    print("No attendance records found for this period.")

            elif choice == "7":
                auth_controller.logout()
                print("Logged out successfully!")

        else:  # Student menu
            if choice == "1":  # Record Daily Attendance
                current_user = auth_controller.get_current_user()
                if current_user and 'student_id' in current_user:
                    try:
                        student_id = current_user['student_id']
                        if attendance_controller.record_attendance(student_id):
                            print("\nDaily attendance recorded successfully!")
                            status = attendance_controller.get_daily_attendance_status(student_id)
                            if status['status'] == 'late':
                                print(f"Note: You were marked as late (Arrived at {status['sign_in_time']})")
                            else:
                                print(f"You arrived on time at {status['sign_in_time']}")
                        else:
                            print("\nFailed to record attendance.")
                    except Exception as e:
                        print(f"\nError recording attendance: {e}")
                else:
                    print("Error: Please log in as a student to record attendance")

            elif choice == "2":  # View My Attendance
                current_user = attendance_controller.get_current_user()
                if not current_user:
                    current_user = auth_controller.get_current_user()
                    
                if current_user and current_user.get('student_id'):
                    student_id = current_user['student_id']
                    records = attendance_controller.get_student_attendance(student_id)
                    if records:
                        print("\nYour Attendance Records:")
                        for record in records:
                            print(f"\nDate: {record['attendance_date']}")
                            print(f"Time: {record['sign_in_time']}")
                            print(f"Status: {record['status']}")
                            if record['is_late']:
                                print("Note: Late arrival")
                            print("---")
                    else:
                        print("No attendance records found.")
                else:
                    print("Error: Student ID not found")

            elif choice == "3":
                courses = course_controller.list_courses()
                print("\nAvailable Courses:")
                for course in courses:
                    print(f"\nCourse ID: {course['course_id']}")
                    print(f"Name: {course['course_name']}")
                    print(f"Location: {course['location']}")
                    print(f"Capacity: {course['max_capacity']}")

            elif choice == "5":  # View Today's Status
                current_user = attendance_controller.get_current_user()
                if not current_user:
                    current_user = auth_controller.get_current_user()
                    
                if current_user and current_user.get('student_id'):
                    student_id = current_user['student_id']
                    status = attendance_controller.get_daily_attendance_status(student_id)
                    
                    print("\nToday's Attendance Status:")
                    if status['status'] == 'late':
                        print(f"Status: Late (Arrived at {status['sign_in_time']})")
                    elif status['status'] == 'present':
                        print(f"Status: Present (Arrived at {status['sign_in_time']})")
                    else:
                        print("Status: Not yet signed in today")
                else:
                    print("Error: Student ID not found")

            elif choice == "6":
                auth_controller.logout()
                print("Logged out successfully!")

            elif choice == "4":
                print("\n1. Add Course")
                print("2. Drop Course")
                enroll_choice = input("Enter choice: ")
                
                course_id = int(input("Enter Course ID: "))
                student_id = int(input("Enter your Student ID: "))
                
                if enroll_choice == "1":
                    if attendance_controller.enroll_student_in_course(student_id, course_id):
                        print("Successfully enrolled in course!")
                    else:
                        print("Failed to enroll in course.")
                elif enroll_choice == "2":
                    if attendance_controller.drop_course(student_id, course_id):
                        print("Successfully dropped course!")
                    else:
                        print("Failed to drop course.")

if __name__ == "__main__":
    main()
