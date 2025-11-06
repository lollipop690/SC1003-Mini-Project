import time

def is_school_placement_valid(team, student):
    school_count = 0
    for member in team:
        if member['School'] == student['School']:
            school_count += 1
    return school_count < 2

def create_gender_balanced_teams(students_in_tg, num_teams=10):
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
                    # Search for a suitable team to place the student
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

# ==============================================================================

def genderpriority(tutorial_groups: dict):
    all_final_teams = {}

    times = []
    
    for tg_name, students in tutorial_groups.items():
        start = time.time()

        print(f"Processing Tutorial Group: {tg_name}...")
        final_teams = create_gender_balanced_teams(students)
        all_final_teams[tg_name] = final_teams

        times.append(time.time() - start)

    return all_final_teams, times
