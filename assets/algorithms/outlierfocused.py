import os
import time
import csv

# ==============================================================================
# 1. DATA READING AND PRE-PROCESSING
# ==============================================================================

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

# ==============================================================================
# 2. CORE TEAM ALLOCATION LOGIC
# ==============================================================================

def check_team_validity(team, student_to_add):
    """Checks if adding a student violates gender or school majority rules."""
    if len(team) >= 5:
        return False  # Team is full

    # Check gender constraint
    gender_count = sum(1 for s in team if s['Gender'] == student_to_add['Gender'])
    if gender_count >= 2: # Adding this student would make it 3 (a majority)
        return False

    # Check school constraint
    school_count = sum(1 for s in team if s['School'] == student_to_add['School'])
    if school_count >= 2: # Adding this student would make it 3 (a majority)
        return False
        
    return True

def create_outlier_focused_teams(students_in_tg, num_teams=10):
    """
    Forms teams by placing academic outliers first, then filling remaining slots
    by matching each team's average CGPA to the group's overall average.
    """
    # Calculate the target average CGPA for the tutorial group
    total_cgpa = sum(s['CGPA'] for s in students_in_tg)
    target_avg_cgpa = total_cgpa / len(students_in_tg)

    # Sort students and separate outliers from the middle pack
    students_sorted = sorted(students_in_tg, key=lambda s: s['CGPA'], reverse=True)
    outliers_high = students_sorted[:num_teams]
    outliers_low = students_sorted[-num_teams:]
    middle_students = students_sorted[num_teams:-num_teams]

    teams = [[] for _ in range(num_teams)]

    # Step 1: Place the outliers using a snake draft to create a balanced foundation
    for i in range(num_teams):
        teams[i].append(outliers_high[i])
        teams[-(i + 1)].append(outliers_low[i])

    # Step 2: Iteratively place middle students into the "best fit" team
    unplaced_students = []
    for student in middle_students:
        best_team_idx = -1
        min_diff = float('inf')

        # Find the best valid team for the current student
        for i, team in enumerate(teams):
            if check_team_validity(team, student):
                # Calculate the team's future average CGPA if the student is added
                future_sum = sum(s['CGPA'] for s in team) + student['CGPA']
                future_avg = future_sum / (len(team) + 1)
                diff = abs(future_avg - target_avg_cgpa)

                if diff < min_diff:
                    min_diff = diff
                    best_team_idx = i
        
        if best_team_idx != -1:
            teams[best_team_idx].append(student)
        else:
            unplaced_students.append(student)

    # Step 3: Handle any students that couldn't be placed due to strict rules
    for student in unplaced_students:
        # Fallback: Place in the first team with a free slot, ignoring school rule if necessary
        placed = False
        for team in teams:
            if len(team) < 5:
                team.append(student)
                placed = True
                break
        if not placed:
             # This case should be rare, but as a last resort, add to the first team.
             teams[0].append(student)
             
    return teams

# ==============================================================================
# 3. DATA FINALIZATION AND OUTPUT
# ==============================================================================

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

def write_output_csv(final_student_list, output_path="final_teams_outlier_focused.csv"):
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
    print(f"Successfully created outlier-focused allocation file: {output_path}")

# ==============================================================================
# 4. MAIN EXECUTION BLOCK
# ==============================================================================

def outlierfocused(file_in):
    all_students = read_student_data(file_in)
    
    if all_students:
        tutorial_groups = group_students_by_tutorial(all_students)
        all_final_teams = {}
        
        times = []

        for tg_name, students in tutorial_groups.items():
            start = time.time()

            print(f"Processing Tutorial Group: {tg_name}...")
            final_teams = create_outlier_focused_teams(students)
            all_final_teams[tg_name] = final_teams

            times.append(time.time() - start)

        final_list = assign_team_numbers_and_flatten(all_final_teams)

        output_path = os.path.dirname(__file__).replace("algorithms", "") + "tmp"
        write_output_csv(final_list, f"{output_path}/final_teams_outlier_focused.csv")

        with open(f"{output_path}/outlierfocused.txt", 'w') as file:
            for t in times:
                file.write(f"{t}\n")