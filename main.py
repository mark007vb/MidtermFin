
import csv


class Student:
    def __init__(self, id_student, name, email):
        self.id = id_student
        self.name = name
        self.email = email
        self.courses = {}

    def add_course(self, course):
        self.courses[course.id] = course

    def get_courses(self):
        return self.courses


class Course:
    def __init__(self, id_course, name, credit):
        self.id = id_course
        self.name = name
        self.credit = credit
        self.students = {}
        self.grades = {}

    def add_student(self, student):
        self.students[student.id] = student

    def get_students(self):
        return self.students

    def add_grade(self, student, grade):
        self.grades[student.id] = grade

    def get_grades(self):
        return self.grades


class Enrollment:
    def __init__(self, student, course, semester, grade=None):
        self.student = student
        self.course = course
        self.semester = semester
        self.grade = grade

    def set_grade(self, grade):
        self.grade = grade


class SchoolManager:
    """
    School Manager
    """

    def __init__(self, students_file, courses_file, enrollments_file):
        self.students = {}
        self.courses = {}
        self.enrollments = {}
        self.students_file = students_file
        self.courses_file = courses_file
        self.enrollments_file = enrollments_file
        self._load_students()
        self._load_courses()
        self._load_enrollments()

    def _load_students(self):
        """
        Loading students from the database
        :return:
        """
        filename = self.students_file

        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i != 0:
                    id_student, name, email = row

                    student = Student(id_student, name, email)
                    self.students[id_student] = student

    def _load_courses(self):
        """
        Loading courses from the database
        :return:
        """
        filename = self.courses_file

        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i != 0:
                    id_course, name, credit = row

                    course = Course(id_course, name, credit)
                    self.courses[id_course] = course

    def _load_enrollments(self):
        """
        Downloading information about student participation in courses from the database
        :return:
        """
        filename = self.enrollments_file

        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i != 0:
                    student_id, course_id, semester, grade = row

                    student = self.students.get(student_id)
                    course = self.courses.get(course_id)
                    enrollment = Enrollment(student, course, semester, grade)
                    self.enrollments[(student_id, course_id)] = enrollment

                    student.add_course(course)
                    course.add_student(student)
                    if grade:
                        course.add_grade(student, grade)

    def _write_student(self, student):
        with open(self.students_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([student.id, student.name, student.email])

    def _write_grade(self, student_id, course_id, semester, grade, enrollment, course, student):

        with open(self.enrollments_file, 'r', newline='') as file:
            dt = csv.DictReader(file)
            up_dt = []
            is_added = False
            for r in dt:

                if r['student_id'] == student_id and r['course_id'] == course_id and r['semester'] == semester:
                    row = {'student_id': r['student_id'],
                           'course_id': r['course_id'],
                           'semester': r['semester'],
                           'grade': grade,
                           }
                    enrollment.set_grade(grade)
                    course.add_grade(student, grade)
                    is_added = True
                else:
                    row = {'student_id': r['student_id'],
                           'course_id': r['course_id'],
                           'semester': r['semester'],
                           'grade': r['grade'],
                           }
                up_dt.append(row)

        if is_added:
            print("Grade recorded")

        else:
            print("Error, please check student ID, course ID or semester.")


        with open(self.enrollments_file, "w", newline='') as file:
            headers = ['student_id', 'course_id', 'semester', 'grade', ]
            data = csv.DictWriter(file, delimiter=',', fieldnames=headers)
            data.writerow(dict((heads, heads) for heads in headers))
            data.writerows(up_dt)

    def _write_enrollment(self, enrollment):
        with open(self.enrollments_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([enrollment.student.id, enrollment.course.id, enrollment.semester, enrollment.grade])

    def add_student(self):
        with open(self.students_file, 'r', newline='') as file:
            dt = csv.DictReader(file)

            student_id = str(len([r for r in dt]) + 1)
        print()
        print(f"Student ID will be: {student_id}")

        name = input("Enter student name: ")
        email = input("Enter student email: ")

        student = Student(student_id, name, email)
        self.students[student_id] = student
        self._write_student(student)

    def enroll_student(self):
        print()
        student_id = input("Enter Student ID: ")
        course_id = input("Enter Course ID: ")
        semester = input("Enter semester: ")

        student = self.students.get(student_id)
        if student is None:
            print('There is no such student')
            return

        course = self.courses.get(course_id)
        if course is None:
            print('No such course')
            return

        enrollment = Enrollment(student, course, semester)
        if enrollment is None:
            print("Student not enrolled in course")
            return
        self.enrollments[(student_id, course_id)] = enrollment

        student.add_course(course)
        course.add_student(student)
        self._write_enrollment(enrollment)

    def grade_student(self):
        print()
        student_id = input("Enter Student ID: ")
        course_id = input("Enter Course ID: ")
        semester = input("Enter Semester: ")
        grade = input("Enter Grade: ")
        student = self.students.get(student_id)

        if student is None:
            print("There is no such student")
            return

        course = self.courses.get(course_id)
        if course is None:
            print("No such course")
            return

        enrollment = self.enrollments.get((student_id, course_id))
        if enrollment is None:
            print("Student not enrolled in course")
            return

        self._write_grade(student_id, course_id, semester, grade, enrollment, course, student)

    def display_student(self):
        print()
        id_student = input("Enter Student ID: ")
        student = self.students.get(id_student)
        if student is None:
            print("There is no such student")
            return
        courses = student.get_courses()
        print(f"Student: {student.name} ({student.email})")
        print("Courses:")
        for course in courses.values():
            grades = course.get_grades()
            grade = grades.get(id_student)
            if grade:
                print(f"- {course.name} ({course.credit} credits), grade: {grade}")
            else:
                print(f"- {course.name} ({course.credit} credits)")

    def display_course(self):
        print()
        course_id = input("Enter Course ID: ")
        course = self.courses.get(course_id)
        if course is None:
            print("No such course")
            return
        students = course.get_students()
        print(f"Course: {course.name} ({course.credit} credits)")
        print("Students:")
        for student in students.values():
            enrollments = self.enrollments.get((student.id, course_id))
            grade = enrollments.grade
            if grade:
                print(f"- {student.name} ({student.email}), grade: {grade}")
            else:
                print(f"- {student.name} ({student.email})")

    def menu(self):
        try:
            while True:
                print("\nMenu:")
                print("1. Add Student")
                print("2. Enroll Student to Course")
                print("3. Grade Student")
                print("4. Display Student")
                print("5. Display Course")
                print("0. EXIT")
                choice = input("Choose an option: ")
                if choice == "1":
                    self.add_student()
                elif choice == "2":
                    self.enroll_student()
                elif choice == "3":
                    self.grade_student()
                elif choice == "4":
                    self.display_student()
                elif choice == "5":
                    self.display_course()
                elif choice == "0":
                    print("\nGoodbye!")
                    break
        except KeyboardInterrupt:
            print("\nGoodbye!")


if __name__ == '__main__':
    manager = SchoolManager(f'database/Students.csv', f'database/Courses.csv', f'database/Enrollments.csv')
    manager.menu()
