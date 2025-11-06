import time

def check_team_validity(team, student_to_add):
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
    # Calculate the target average CGPA for the tutorial group
    total_cgpa = sum(s['CGPA'] for s in students_in_tg)
    target_avg_cgpa = total_cgpa / len(students_in_tg)

    # Sort students and separate outliers from the middle pack
    students_sorted = sorted(students_in_tg, key=lambda s: s['CGPA'], reverse=True)
    outliers_low = students_sorted[:num_teams]
    outliers_high = students_sorted[-num_teams:]
    middle_students = students_sorted[num_teams:-num_teams]

    teams = [[] for _ in range(num_teams)]

    # Step 1: Place the outliers using a snake draft to create a balanced foundation
    for i in range(num_teams):
        teams[i].append(outliers_low[i])
        teams[i].append(outliers_high[-(i + 1)])

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

def outlierfocused(tutorial_groups: dict):
    all_final_teams = {}
    
    times = []

    for tg_name, students in tutorial_groups.items():
        start = time.time()

        print(f"Processing Tutorial Group: {tg_name}...")
        final_teams = create_outlier_focused_teams(students)
        all_final_teams[tg_name] = final_teams

        times.append(time.time() - start)

    return all_final_teams, times
