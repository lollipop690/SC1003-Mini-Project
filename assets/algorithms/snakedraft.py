import time
import csv
import random  #for O numbers, N=number of students,G = number of tgs, S = number of students per tg - N = GS

# ==============================================================================
# 1. DATA READING AND PRE-PROCESSING
# ==============================================================================

def read_student_data(file_path="records.csv"): #O(N)
    """
    Reads student data from a CSV file into a list of dictionaries.
    Converts CGPA to a float for numerical operations.
    [cite_start][cite: 25, 34]
    """
    records = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert CGPA to float for sorting and calculations
                row['CGPA'] = float(row['CGPA'])
                records.append(row)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    return records

def group_students_by_tutorial(student_data): #O(N)
    """
    Groups a list of students by their tutorial group.
    This ensures teams are formed only with members from the same group.
    [cite_start][cite: 26]
    """
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

def create_teams_snake_draft(students_in_tg, num_teams=10): #O(SlogS)
    """
    Performs an initial, CGPA-balanced team assignment for one tutorial group.
    It sorts students by CGPA and distributes them using a snake draft to
    [cite_start]balance academic performance from the start. [cite: 30]
    """
    # Sort students by CGPA from highest to lowest
    students_sorted = sorted(students_in_tg, key=lambda s: s['CGPA'], reverse=True)

    # Initialize 10 empty teams
    teams = [[] for _ in range(num_teams)]
    
    current_team_index = 0
    direction = 1  # 1 for forward (0->9), -1 for backward (9->0)

    for student in students_sorted:
        teams[current_team_index].append(student)

        # Move to the next team based on the current direction
        current_team_index += direction

        # Reverse direction when the end of the team list is reached
        if current_team_index == num_teams:
            direction = -1
            current_team_index = num_teams - 1
        elif current_team_index == -1:
            direction = 1
            current_team_index = 0
            
    return teams

def calculate_team_score(team): #O(1)
    """
    Calculates a "penalty" score for a single team based on diversity criteria.
    A perfect team scores 0. Points are added for having a majority
    (3 or more) [cite_start]of one gender or from one school. [cite: 28, 29]
    """
    score = 0
    gender_counts = {}
    school_counts = {}

    # Count occurrences of each gender and school
    for student in team:
        gender = student['Gender']
        school = student['School']
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
        school_counts[school] = school_counts.get(school, 0) + 1

    # Add penalty for gender majority (3 or more members of the same gender)
    for count in gender_counts.values():
        if count >= 3:
            score += (count - 2) * 10  # Penalize each member over the threshold of 2

    # Add penalty for school majority (3 or more members from the same school)
    for count in school_counts.values():
        if count >= 3:
            score += (count - 2) * 10

    return score

def optimize_teams(teams_in_tg): #O(1)
    """
    Iteratively improves team diversity by swapping students between the team
    with the highest penalty score and other teams, aiming to reduce the
    overall score for the tutorial group.
    """
    # A high number of iterations to allow for thorough optimization
    for _ in range(500):
        # Calculate scores for all teams
        scores = [calculate_team_score(team) for team in teams_in_tg]
        total_score = sum(scores)
        
        # If the total score is 0, the teams are perfectly balanced
        if total_score == 0:
            break

        # Find the team with the highest penalty score to improve
        worst_team_index = scores.index(max(scores))
        
        best_improvement = 0
        best_swap_details = None # (other_team_idx, student_from_worst, student_from_other)

        # Try to swap a student from the worst team with a student from any other team
        for other_team_index in range(len(teams_in_tg)):
            if worst_team_index == other_team_index:
                continue

            current_score_sum = scores[worst_team_index] + scores[other_team_index]
            
            # Iterate through all possible student pairings between the two teams
            for s1_idx in range(len(teams_in_tg[worst_team_index])):
                for s2_idx in range(len(teams_in_tg[other_team_index])):
                    
                    # Simulate the swap
                    worst_team = teams_in_tg[worst_team_index]
                    other_team = teams_in_tg[other_team_index]
                    
                    worst_team[s1_idx], other_team[s2_idx] = other_team[s2_idx], worst_team[s1_idx]
                    
                    # Check if the swap is beneficial
                    new_score_sum = calculate_team_score(worst_team) + calculate_team_score(other_team)
                    improvement = current_score_sum - new_score_sum

                    # If this is the best improvement found so far, save it
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_swap_details = (other_team_index, s1_idx, s2_idx)
                    
                    # Swap back to test the next pair
                    worst_team[s1_idx], other_team[s2_idx] = other_team[s2_idx], worst_team[s1_idx]
        
        # If a beneficial swap was found, make it permanent
        if best_swap_details:
            other_idx, s1, s2 = best_swap_details
            worst_team = teams_in_tg[worst_team_index]
            other_team = teams_in_tg[other_idx]
            worst_team[s1], other_team[s2] = other_team[s2], worst_team[s1]
        else:
            # If no improvement found after checking all swaps, break to avoid useless loops
            break

    return teams_in_tg


# ==============================================================================
# 3. DATA FINALIZATION AND OUTPUT
# ==============================================================================

def assign_team_numbers_and_flatten(all_optimized_tgs): #O(N)
    """
    Takes the final optimized team structures, assigns a team number (1-10)
    to each student, and flattens the data back into a single list for export.
    [cite_start][cite: 38, 39]
    """
    final_student_list = []
    
    # Sort tutorial groups for consistent output order
    sorted_tg_names = sorted(all_optimized_tgs.keys())

    for tg_name in sorted_tg_names:
        list_of_teams = all_optimized_tgs[tg_name]
        for team_index, team in enumerate(list_of_teams):
            team_number = team_index + 1
            for student in team:
                # Add the new "Team Assigned" column to each student's record
                student["Team Assigned"] = team_number
                final_student_list.append(student)
                
    return final_student_list

def write_output_csv(final_student_list, output_path): #O(N)
    """
    Writes the final list of students with assigned teams to a new CSV file.
    [cite_start]The headers match the project requirements. [cite: 38]
    """
    if not final_student_list:
        print("No data available to write to CSV.")
        return

    headers = ["Tutorial Group", "Team Assigned", "Student ID", "Name", "School", "Gender", "CGPA"]
    
    # Create a list of dictionaries with the correct header order
    output_data = []
    for student in final_student_list:
        ordered_student = {header: student.get(header) for header in headers}
        output_data.append(ordered_student)

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_data)
    print(f"Successfully created team allocation file: {output_path}")

# ==============================================================================
# 4. MAIN EXECUTION BLOCK 
# ==============================================================================

if __name__ == "__main__":
    # --- Step 1: Read and Group Data ---
    all_students = read_student_data("records.csv")
    
    if all_students:
        tutorial_groups = group_students_by_tutorial(all_students)
        
        all_optimized_teams = {}
        
        # --- Step 2: Process Each Tutorial Group ---
        times = []

        for tg_name, students in tutorial_groups.items():
            start = time.time()

            print(f"Processing Tutorial Group: {tg_name}...")
            
            # Create initial teams balanced by CGPA
            initial_teams = create_teams_snake_draft(students)
            
            # Optimize for gender and school diversity
            optimized_teams = optimize_teams(initial_teams)
            
            all_optimized_teams[tg_name] = optimized_teams

            times.append(time.time() - start)

        # --- Step 3: Finalize and Export ---
        final_list = assign_team_numbers_and_flatten(all_optimized_teams)
        write_output_csv(final_list, "./tmp/final_teams_snake_draft.csv")

        with open('./tmp/snake_draft.txt', 'w') as file:
            for t in times:
                file.write(f"{t}\n")

#==========================================================================
# Overall Time Complexity = O(N+NlogS)
#==========================================================================