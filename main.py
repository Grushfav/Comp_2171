from db.db_manager import DBManager
from controllers.attendance_controller import AttendanceController
from controllers.auth_controller import AuthController
from controllers.course_controller import CourseController
from datetime import datetime

def display_menu(is_admin: bool):
    print("\nChurch School Attendance System")
    if not is_admin:
        print("1. Record Attendance")
        print("2. View My Attendance")
        print("3. View Available Courses")
        print("4. Logout")
    else:
        print("1. Create New Course")
        print("2. View All Courses")
        print("3. Generate Course Report")
        print("4. View Student Attendance")
        print("5. Logout")

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
            print("Student registration successful!")
    else:
        if auth_controller.signup(username, password, first_name, last_name, 
                                email, role):
            print("Admin registration successful!")

def handle_login(auth_controller: AuthController):
    print("\nLogin")
    username = input("Enter username: ")
    password = input("Enter password: ")
    user = auth_controller.login(username, password)
    if user:
        print(f"Welcome, {user['first_name']}!")
        return True
    print("Invalid credentials!")
    return False

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
                if not handle_login(auth_controller):
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
                auth_controller.logout()
                print("Logged out successfully!")

        else:  # Student menu
            if choice == "1":
                student_id = int(input("Enter your Student ID: "))
                course_id = int(input("Enter Course ID: "))
                if attendance_controller.record_attendance(student_id, course_id):
                    print("Attendance recorded successfully!")

            elif choice == "2":
                student_id = int(input("Enter your Student ID: "))
                records = attendance_controller.get_student_attendance(student_id)
                if records:
                    print("\nYour Attendance Records:")
                    for record in records:
                        print(f"Date: {record['attendance_date']}")
                        print(f"Course: {record['course_name']}")
                        print(f"Status: {record['status']}")
                        print("---")

            elif choice == "3":
                courses = course_controller.list_courses()
                print("\nAvailable Courses:")
                for course in courses:
                    print(f"\nCourse ID: {course['course_id']}")
                    print(f"Name: {course['course_name']}")
                    print(f"Location: {course['location']}")
                    print(f"Capacity: {course['max_capacity']}")

            elif choice == "4":
                auth_controller.logout()
                print("Logged out successfully!")

if __name__ == "__main__":
    main()
