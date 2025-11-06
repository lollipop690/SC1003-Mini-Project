import time

def snake_draft(students_in_tg, num_teams=10): #this function creates a WIP grouping for an individual tg based solely on gpa in a snake draft format
    students_sorted = sorted(students_in_tg, key=lambda s: s['CGPA'], reverse=True) #essentially, this lambda function will pull every student in order of their cgpa from lowest to highest, which is then reversed. note that a lambda function is just a function as a key in a dict
    teams = [[] for tm in range(num_teams)] # generates an empty list for each team
    
    current_team_index = 0
    direction = 1

    for student in students_sorted:
        teams[current_team_index].append(student) #adds the student at current index to the current group(ungrouped student with the lowest index-highest gpa)
        current_team_index += direction

        if current_team_index == num_teams: #block to reverse direction, creating the snake draft
            direction = -1
            current_team_index = num_teams - 1
        elif current_team_index == -1:
            direction = 1
            current_team_index = 0
            
    return teams

def diversity_score(team): #grades how diverse each group is(lower better)
    score = 0
    gender_counts = {}
    school_counts = {}

    for student in team:
        gender_counts[student['Gender']] = gender_counts.get(student['Gender'], 0) + 1
        school_counts[student['School']] = school_counts.get(student['School'], 0) + 1

    for count in gender_counts.values():
        if count >= 3:
            score += (count - 2) * 10 #every 3rd person onwards of the same gender will add 10 to the diversity score

    for count in school_counts.values():
        if count >= 2:
            score += (count - 2) * 10 #every 2nd person onwards of the same school will add 10 to the diversity score

    return score

def optimize_teams(teams_in_tg): 
    # A high number of iterations to allow for thorough optimization
    for k in range(500):
        # Calculate scores for all teams
        scores = [diversity_score(team) for team in teams_in_tg]
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
                    new_score_sum = diversity_score(worst_team) + diversity_score(other_team)
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

def snakedraft(tutorial_groups: dict):
    all_optimized_teams = {}
    
    # --- Step 2: Process Each Tutorial Group ---
    times = []

    for tg_name, students in tutorial_groups.items():
        start = time.time()

        print(f"Processing Tutorial Group: {tg_name}...")
        initial_teams = snake_draft(students)
        optimized_teams = optimize_teams(initial_teams)
        all_optimized_teams[tg_name] = optimized_teams

        times.append(time.time() - start)

    return all_optimized_teams, times
