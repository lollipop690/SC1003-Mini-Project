import os
import time
import csv

def read_student_data(file_path="records.csv"):
    """Reads student data and converts CGPA to float."""
    records = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['CGPA'] = float(row['CGPA'])
                records.append(row)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    return records

def group_students_by_tutorial(student_data):
    """Groups a list of students by their tutorial group."""
    tutorial_groups = {}
    for student in student_data:
        tg = student["Tutorial Group"]
        if tg not in tutorial_groups:
            tutorial_groups[tg] = []
        tutorial_groups[tg].append(student)
    return tutorial_groups

def is_school_placement_valid(team, student):
    """Checks if adding a student violates the school majority rule."""
    school_count = 0
    for member in team:
        if member['School'] == student['School']:
            school_count += 1
    return school_count < 2

def create_gender_balanced_teams(students_in_tg, num_teams=10):
    """
    Creates teams by prioritizing gender balance first, then handling
    school diversity and CGPA balance.
    """
    males = sorted([s for s in students_in_tg if s['Gender'] == 'Male'], key=lambda x: x['CGPA'], reverse=True)
    females = sorted([s for s in students_in_tg if s['Gender'] == 'Female'], key=lambda x: x['CGPA'], reverse=True)

    teams = [[] for _ in range(num_teams)]
    unplaced_students = []

    # Determine which gender is the minority
    if len(males) < len(females):
        minority_gender_list = males
        majority_gender_list = females
    else:
        minority_gender_list = females
        majority_gender_list = males

    # Step 1: Distribute all students from the minority gender list first
    for i, student in enumerate(minority_gender_list):
        teams[i % num_teams].append(student)

    # Step 2: Place students from the majority gender list
    all_students_to_place = list(majority_gender_list)
    
    # Fill teams until they all have 5 members
    team_idx = 0
    while any(len(t) < 5 for t in teams):
        if not all_students_to_place:
            break # Stop if we run out of students

        student_to_place = all_students_to_place.pop(0) # Get the next student by CGPA

        # Try to place the student in a valid team
        placed = False
        for i in range(num_teams):
            current_team_idx = (team_idx + i) % num_teams
            if len(teams[current_team_idx]) < 5 and is_school_placement_valid(teams[current_team_idx], student_to_place):
                teams[current_team_idx].append(student_to_place)
                placed = True
                break
        
        if not placed:
            # If no direct placement works (due to school constraint), add to unplaced list for now
            unplaced_students.append(student_to_place)
            
        team_idx = (team_idx + 1) % num_teams

    # Step 3: Handle any unplaced students by forcing swaps
    for student in unplaced_students:
        placed = False
        for team in teams:
            if len(team) < 5:
                team.append(student)
                placed = True
                break
        if placed: continue

        # If all teams are full, find a swap
        for team_to_swap_with in teams:
            for member_to_swap_idx, member in enumerate(team_to_swap_with):
                # Check if swapping this member with the unplaced student is valid
                original_member = team_to_swap_with.pop(member_to_swap_idx)
                
                if is_school_placement_valid(team_to_swap_with, student):
                    team_to_swap_with.insert(member_to_swap_idx, student)
                    # Now, try to place the original_member somewhere else
                    # This is a simplified fallback; a full implementation might need more complex logic
                    # For this project, we'll place it in the first available slot
                    for other_team in teams:
                        if len(other_team) < 5:
                            other_team.append(original_member)
                            placed = True
                            break
                else:
                    # Swap was not valid, revert
                    team_to_swap_with.insert(member_to_swap_idx, original_member)

                if placed: break
            if placed: break

    return teams

def assign_team_numbers_and_flatten(all_final_tgs):
    """Assigns team numbers and flattens the data structure for CSV writing."""
    final_student_list = []
    sorted_tg_names = sorted(all_final_tgs.keys())

    for tg_name in sorted_tg_names:
        list_of_teams = all_final_tgs[tg_name]
        for team_index, team in enumerate(list_of_teams):
            team_number = team_index + 1
            for student in team:
                student["Team Assigned"] = team_number
                final_student_list.append(student)
    return final_student_list

def write_output_csv(final_student_list, output_path):
    """Writes the final list of students to a new CSV file."""
    if not final_student_list:
        print("No data to write.")
        return
    headers = ["Tutorial Group", "Team Assigned", "Student ID", "Name", "School", "Gender", "CGPA"]
    
    output_data = [{header: student.get(header) for header in headers} for student in final_student_list]

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_data)
    print(f"Successfully created gender-priority allocation file: {output_path}")


def hardgendercap(file_in):
    all_students = read_student_data(file_in)
    
    if all_students:
        tutorial_groups = group_students_by_tutorial(all_students)
        
        all_final_teams = {}

        times = []
        
        for tg_name, students in tutorial_groups.items():
            start = time.time()

            print(f"Processing Tutorial Group: {tg_name}...")
            final_teams = create_gender_balanced_teams(students)
            all_final_teams[tg_name] = final_teams

            times.append(time.time() - start)

        final_list = assign_team_numbers_and_flatten(all_final_teams)

        output_path = os.path.dirname(__file__).replace("algorithms", "") + "tmp"
        write_output_csv(final_list, f"{output_path}/final_teams_gender_priority.csv")

        with open(f"{output_path}/hardgendercap.txt", 'w') as file:
            for t in times:
                file.write(f"{t}\n")