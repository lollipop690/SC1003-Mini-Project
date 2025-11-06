import random
import csv
import os

def randomized(tutorial_groups: dict):
    """Creates a random team allocation to serve as a baseline for comparison."""
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