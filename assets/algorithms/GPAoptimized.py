import time

def snake_draft(students_sorted,num_teams=10):#this function creates a WIP grouping for an individual tg based solely on gpa in a snake draft format
    def _draft(students_sorted, num_teams=10): 
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
    
    if isinstance(students_sorted,dict):
        return {tg: _draft(students ,num_teams) for tg,students in students_sorted.items()}
    else:   
        return _draft(students_sorted, num_teams)

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

def total_cgpa_variance(teams):
    if not teams or not all(teams):
        return 0
    
    team_averages = [sum(s['CGPA'] for s in team) / len(team) for team in teams] #calculate the average cgpa of each group
    overall_average = sum(team_averages) / len(team_averages) #calculate the average cgpa of the tg
    
    variance = sum((avg - overall_average) ** 2 for avg in team_averages) / len(team_averages) #calculates the variance of the average tg (standard s^2 variance)
    return variance

def optimize_teams(teams_in_tg, diversity_weight=0.70, cgpa_weight=0.30):
    DIVERSITY_WEIGHT = diversity_weight
    CGPA_WEIGHT = cgpa_weight #set weights

    for k in range(50): #number of tests to run
        current_diversity_score = sum(diversity_score(t) for t in teams_in_tg)
        current_cgpa_variance = total_cgpa_variance(teams_in_tg) #calculates initial score and variance of current teams

        if current_diversity_score == 0 and current_cgpa_variance < 0.001: #if teams are new perfect, dont change
            break 

        best_improvement_score = 0
        best_swap_details = None #instansiation of vars

        for i in range(len(teams_in_tg)):
            for j in range(i + 1, len(teams_in_tg)): #every combination of teams

                for s1_idx in range(len(teams_in_tg[i])):
                    for s2_idx in range(len(teams_in_tg[j])): 
                        team1 = teams_in_tg[i]
                        team2 = teams_in_tg[j]#every combination of students within the chosen teams

                        team1[s1_idx], team2[s2_idx] = team2[s2_idx], team1[s1_idx]#simulate the swap

                        new_diversity_score = sum(diversity_score(t) for t in teams_in_tg)
                        new_cgpa_variance = total_cgpa_variance(teams_in_tg) #new scores for the swap
                        
                        diversity_improvement = current_diversity_score - new_diversity_score #change in diversity score
                        cgpa_improvement = current_cgpa_variance - new_cgpa_variance #change in cgpa variance

                        total_improvement = (diversity_improvement * DIVERSITY_WEIGHT) + (cgpa_improvement * CGPA_WEIGHT)

                        if total_improvement > best_improvement_score:
                            best_improvement_score = total_improvement
                            best_swap_details = (i, j, s1_idx, s2_idx)#if this is the best swap, store it 

                        team1[s1_idx], team2[s2_idx] = team2[s2_idx], team1[s1_idx] #swap back for now to check all other possibilities
        
        if best_swap_details:
            i, j, s1, s2 = best_swap_details
            teams_in_tg[i][s1], teams_in_tg[j][s2] = teams_in_tg[j][s2], teams_in_tg[i][s1]#sets the best swap after checking all
        else:
            break#if there are no good swaps, break the loop to save computational power
            
    return teams_in_tg

# ==============================================================================

def GPAoptimized(tutorial_groups: dict):
    all_optimized_teams = {}
        
    times = []

    for tg_name, students in tutorial_groups.items():
        start = time.time()

        print(f"Processing Tutorial Group: {tg_name}...")
        initial_teams = snake_draft(students)
        optimized_teams = optimize_teams(initial_teams)
        all_optimized_teams[tg_name] = optimized_teams

        times.append(time.time() - start)

    return all_optimized_teams, times
