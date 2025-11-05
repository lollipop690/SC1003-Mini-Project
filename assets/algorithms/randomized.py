import random
import csv
import os

def randomized(file_in):
    """Creates a random team allocation to serve as a baseline for comparison."""
    print("Generating a random allocation for comparison...")
    try:
        with open(file_in, mode='r', newline='', encoding='utf-8') as file:
            all_students = list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"Error: The original records file '{file_in}' was not found.")
        return None

    tutorial_groups = {}
    for student in all_students:
        tg = student["Tutorial Group"]
        if tg not in tutorial_groups:
            tutorial_groups[tg] = []
        tutorial_groups[tg].append(student)

    randomly_assigned_students = []
    for tg_name, students in tutorial_groups.items():
        random.shuffle(students)
        for i, student in enumerate(students):
            team_number = (i // 5) + 1
            student['Team Assigned'] = team_number
            randomly_assigned_students.append(student)

    """Writes the final list of students to a new CSV file."""
    if not randomly_assigned_students:
        print("No data to write.")
        return
    headers = ["Tutorial Group", "Team Assigned", "Student ID", "Name", "School", "Gender", "CGPA"]
    
    output_data = [{header: student.get(header) for header in headers} for student in randomly_assigned_students]

    output_path = os.path.dirname(__file__).replace("algorithms", "") + "tmp" + "/finals_teams_randomized.csv"
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_data)
    print(f"Successfully created outlier-focused allocation file: {output_path}")