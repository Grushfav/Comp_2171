from db.db_manager import DBManager
from datetime import datetime, timedelta

def setup_test_data():
    print("Initializing database...")
    db = DBManager("church_school.db")
    db.initialize_db()  # Initialize the database tables first
    
    print("Adding test data...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Add a test user
            cursor.execute('''
                INSERT INTO users (username, password, first_name, last_name, email, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('john_doe', 'password123', 'John', 'Doe', 'john@example.com', 'student'))
            
            user_id = cursor.lastrowid
            
            # Add a test student
            cursor.execute('''
                INSERT INTO students (user_id, contact_number, emergency_contact)
                VALUES (?, ?, ?)
            ''', (user_id, '123-456-7890', 'Jane Doe: 123-555-0000'))
            
            student_id = cursor.lastrowid
            
            # Add a test course
            cursor.execute('''
                INSERT INTO courses (course_name, description, start_date, end_date, location, max_capacity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('Sunday School', 'Basic religious education', 
                  datetime.now().date(), 
                  (datetime.now() + timedelta(days=90)).date(),
                  'Room 101', 30))
            
            conn.commit()
            
            print("\nTest data has been added successfully!")
            print(f"Student ID: {student_id}")
            print(f"Course ID: {cursor.lastrowid}")
            print("\nYou can now run main.py to use the system.")
            
        except Exception as e:
            print(f"Error adding test data: {e}")
            conn.rollback()

if __name__ == "__main__":
    setup_test_data() 