from db import get_connection

def list_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no FROM students")
    students = cursor.fetchall()
    print("\n👥 Students:")
    for idx, (sid, name, roll) in enumerate(students, 1):
        print(f"   {idx}. {name} (Roll: {roll})")
    conn.close()
    return students

def list_subjects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()
    print("\n📚 Subjects:")
    for idx, (sid, name) in enumerate(subjects, 1):
        print(f"   {idx}. {name}")
    conn.close()
    return subjects

def add_student(name, roll):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, roll_no) VALUES (%s, %s)", (name, roll))
    conn.commit()
    print("✅ Student added successfully.")
    conn.close()

def add_subject(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
    conn.commit()
    print("✅ Subject added.")
    conn.close()

def enter_marks():
    # Show students and select one
    students = list_students()
    if not students:
        print("❌ No students found.")
        return
    try:
        stu_choice = int(input("Select student number: "))
        if not (1 <= stu_choice <= len(students)):
            print("❌ Invalid student selection.")
            return
    except ValueError:
        print("❌ Invalid input.")
        return
    student_id, student_name, student_roll = students[stu_choice - 1]

    # Show subjects and select one
    subjects = list_subjects()
    if not subjects:
        print("❌ No subjects found.")
        return
    try:
        sub_choice = int(input("Select subject number: "))
        if not (1 <= sub_choice <= len(subjects)):
            print("❌ Invalid subject selection.")
            return
    except ValueError:
        print("❌ Invalid input.")
        return
    subject_id, subject_name = subjects[sub_choice - 1]

    # Enter marks
    try:
        marks = int(input(f"Enter marks for {student_name} in {subject_name}: "))
    except ValueError:
        print("❌ Invalid marks.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO marks (student_id, subject_id, marks_obtained) VALUES (%s, %s, %s)",
                   (student_id, subject_id, marks))
    conn.commit()
    print("✅ Marks entered.")
    conn.close()

def view_result(roll_no):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM students WHERE roll_no = %s", (roll_no,))
    student = cursor.fetchone()
    if not student:
        print("❌ Student not found.")
        conn.close()
        return

    print(f"\n📘 Result for {student[1]} (Roll: {roll_no}):")

    cursor.execute("""
        SELECT subjects.name, marks.marks_obtained
        FROM marks
        JOIN subjects ON marks.subject_id = subjects.id
        WHERE marks.student_id = %s
    """, (student[0],))
    results = cursor.fetchall()

    total = 0
    for sub, mark in results:
        print(f"   {sub}: {mark}")
        total += mark

    if results:
        gpa = total / len(results)
        print(f"📊 GPA: {gpa:.2f}")
    else:
        print("No marks found.")
    conn.close()

# 🧪 Simple CLI Menu
if __name__ == "__main__":
    while True:
        print("\n--- Student Result Management System ---")
        print("1. Add Student")
        print("2. Add Subject")
        print("3. Enter Marks")
        print("4. View Result")
        print("5. Show Students")
        print("6. Show Subjects")
        print("7. Exit")

        choice = input("Select an option: ")
        if choice == '1':
            add_student(input("Student Name: "), input("Roll No: "))
        elif choice == '2':
            add_subject(input("Subject Name: "))
        elif choice == '3':
            enter_marks()
        elif choice == '4':
            view_result(input("Student Roll No: "))
        elif choice == '5':
            list_students()
        elif choice == '6':
            list_subjects()
        elif choice == '7':
            break
        else:
            print("❌ Invalid choice.")
