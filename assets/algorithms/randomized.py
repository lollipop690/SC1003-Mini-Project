import random

def randomized(tutorial_groups: dict):
    randomly_assigned_students = []
    for tg_name, students in tutorial_groups.items():
        random.shuffle(students)
        for i, student in enumerate(students):
            team_number = (i // 5) + 1
            student['Team Assigned'] = team_number
            randomly_assigned_students.append(student)

    return randomly_assigned_students