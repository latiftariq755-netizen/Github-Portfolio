admin = "ecat_admin"
admin_password = "admin123"

student = "student"
student_password = "student123"

Correct_marks = 4
Wrong_marks = -1
Skip_marks = 0

student_results = {}
questions = []

questions.append({
    "id" : 1,
    "Subject" : "Maths",
    "question" : "5 - 2 = ?",
    "choices" : {
        "A" : "2",
        "B" : "3",
        "C" : "4",
        "D" : "1"
    },
    "answer" : "B"
})

questions.append({
    "id" : 2,
    "Subject" : "Computer Science",
    "question" : "Which one is the fastest memory?",
    "choices" : {
        "A" : "RAM",
        "B" : "ROM",
        "C" : "Cache",
        "D" : "Hard Disk"
    },
    "answer" : "C"
})

questions.append({
    "id" : 3,
    "Subject" : "Physics",
    "question" : "What is the SI unit of acceleration?",
    "choices": {
        "A" : "m/s",
        "B" : "m/s^3",
        "C" : "km/h",
        "D" : "m/s^2"
    },
    "answer" : "D" 
})

questions.append({
    "id" : 4,
    "Subject" : "English",
    "question" : "What is the synonym of 'Intricate'?",
    "choices" : {
        "A" : "Simple",
        "B" : "Complex",
        "C" : "Easy",
        "D" : "Straightforward"
    },
    "answer" : "B"
})  

questions.append({
    "id" : 5,
    "Subject" : "Maths",
    "question" : "What is the formula of Volume?",
    "choices" : {
        "A" : "A * W",
        "B" : "L * W * H",
        "C" : "A ^ 2",
        "D" : "L ^ 2",
    },
    "answer" : "B"
})

questions.append({
    "id" : 6,
    "Subject" : "Computer Science",
    "question" : "Which unit controls mathematical calculations of computer?",
    "choices" : {
        "A" : "ALU",
        "B" : "CU",
        "C" : "RAM",
        "D" : "ROM"
    },
    "answer" : "A"
})

questions.append({
    "id" :7,
    "Subject" : "Physics",
    "question" : "What is the speed of light in vacuum?",
    "choices" : {
        "A" : "3 x 10^5 m/s",
        "B" : "3 x 10^6 m/s",
        "C" : "3 x 10^8 m/s",
        "D" : "3 x 10^7 m/s"
    },
    "answer" : "C"
})

questions.append({
    "id" : 8,
    "Subject" : "English",
    "question" : "What is the antonym of 'Abundant'?",
    "choices" : {
        "A" : "Plentiful",
        "B" : "Scarce",
        "C" : "Ample",
        "D" : "Copious"
    },
    "answer" : "B"
})

questions.append({
    "id" : 9,
    "Subject" : "Maths",
    "question" : "What is the derivative of 2x^2?",
    "choices" : {
        "A" : "4x",
        "B" : "2x",
        "C" : "4x^2",
        "D" : "2x^2"
    },
    "answer" : "A"
})

questions.append({
    "id" : 10,
    "Subject" : "Computer Science",
    "question" : "Which of the following is a programming language?",
    "choices" : {
        "A" : "HTML",
        "B" : "CSS",
        "C" : "Python",
        "D" : "SQL"
    },
    "answer" : "C"
})

def view_questions():
    if not questions:
        print("No questions available.")
        return
    for q in questions:
        print(f"ID: {q['id']}, Subject: {q['Subject']}, Question: {q.get('question', 'Missing Question')}")
        for choice, text in q.get('choices', {}).items():
            print(f"  {choice}: {text}")
        print(f"Answer: {q['answer']}")

def add_questions():
    try:
        new_id = max(q['id'] for q in questions) + 1 if questions else 1
        subject = input("Enter subject:")
        question_text = input("Enter question:")
        choices = {}
        for option in ['A', 'B', 'C', 'D']:
            choices[option] = input(f"Enter choice {option}:")
        answer = input("Enter correct answer (A/B/C/D):").upper()
        if answer not in choices:
            print("Invalid answer choice! Question not added.")
            return
        new_question = {
            "id": new_id,
            "Subject": subject,
            "question": question_text,
            "choices": choices,
            "answer": answer
        }
        questions.append(new_question)
        print("Question added successfully.")
    except Exception as e:
        print("Error adding question:", e)

def delete_questions():
    try:
        q_id = int(input("Enter the ID of the question to delete:"))
        for q in questions:
            if q['id'] == q_id:
                questions.remove(q)
                print("Question deleted successfully.")
                return
        print("Question ID not found!")
    except ValueError:
        print("Invalid input! Please enter a valid question ID.")

def question_bank_statistics():
    if not questions:
        print("No questions available for statistics.")
        return
    subject_count = {}
    for q in questions:
        subject = q['Subject']
        subject_count[subject] = subject_count.get(subject, 0) + 1
    print("Question Bank Statistics:")
    for subject, count in subject_count.items():
        print(f"{subject}: {count} questions")

def view_results():
    if not student_results:
        print("No student results available.")
        return
    print("Student Results:")
    for q_id, marks in student_results.items():
        print(f"Question ID: {q_id}, Marks: {marks}")
def admin_login():
    attempt = 0
    while attempt < 3:
        username = input("Enter your username:")
        password = input("Enter your password:")

        if username == admin and password == admin_password:
            print("Login successful. Welcome!")
            return True
        else:
            attempt += 1
            print("Invalid credentials, Attempts left:", 3 - attempt)
    print("Admin account locked.")
    return False

def admin_menu():
    while True:
        print("\n====================")
        print("Admin Menu")
        print("====================")
        print("1. View all questions")
        print("2. Add questions")
        print("3. Delete questions")
        print("4. Question bank statistics")
        print("5. View all student results")
        print("6. Logout")

        choice = input("Enter your choice:").strip()

        if choice == "1":
            view_questions()
        elif choice == "2":
            add_questions()
        elif choice == "3":
            delete_questions()
        elif choice == "4":
            question_bank_statistics()
        elif choice == "5":
            view_results()
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid choice! Please try again.")

# Student functions

def take_exam():
    name = input("Enter your name:")
    roll_number = input("Enter your roll number:")
    score = 0
    for index, q in enumerate(questions, start=1):
        print(f"Question {index}: {q['question']}")
        for choice, text in q['choices'].items():
            print(f"  {choice}: {text}")
        answer = input("Enter your answer (A/B/C/D) or 'S' to skip:").upper()
        if answer == 'S':
            student_results[q['id']] = Skip_marks
        elif answer == q['answer']:
            student_results[q['id']] = Correct_marks
        else:
            student_results[q['id']] = Wrong_marks
    total_score = sum(student_results.values())
    print(f"Thank you {name} for taking the exam.")
    #return to student menu after exam
    student_menu()

def view_results():
    if not student_results:
        print("No results available.")
        return
    print("Your Exam Results:")
    for result in student_results:
        print(f"Question ID: {result}, Marks: {student_results[result]}")
def student_login():
    attempt = 0
    while attempt < 3:
        username = input("Enter your username:")
        password = input("Enter your password:")

        if username == student and password == student_password:
            print("Login successful. Welcome!")
            return True
        else:
            attempt += 1
            print("Invalid credentials, Attempts left:", 3 - attempt)
    print("Student account locked.")
    return False

def student_menu():
    while True:
        print("\n====================")
        print("Student Menu")
        print("====================")
        print("1. Take Exam")
        print("2. View Results")
        print("3. Logout")

        choice = input("Enter your choice:").strip()

        if choice == "1":
            take_exam()
        elif choice == "2":
            view_results()
        elif choice == "3":
            print("Logging out...")
            break
        else:
            print("Invalid choice! Please try again.")
while True:
        print("\n====================")
        print("Ecat Exam Management System")
        print("====================")
        print("1. Student Login")
        print("2. Admin Login")
        print("3. Exit")
        choice = input("Enter your choice:").strip()
        if choice == "1":
            if student_login():
                student_menu()
        elif choice == "2":
            if admin_login():
                admin_menu()
        elif choice == "3":
            print("Exiting the system. Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")