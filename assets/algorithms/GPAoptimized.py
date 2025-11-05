import os
import time
import csv

def read_student_data(file_path="records.csv"): # opens file called records.csv
    records = [] #generates empty list
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader: 
                row['CGPA'] = float(row['CGPA'])#changes cgpa data type from str to flt, so we can iterate on it
                records.append(row)#puts the list into the records list, creating list of lists
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")#handles situation where file is gone
        return None
    return records

def students_by_tg(student_data): #reads the output list of list from the previous function
    tutorial_groups = {} #empty dict
    for student in student_data:
        tg = student["Tutorial Group"] #initialising tg variable to the tg of indv students
        if tg not in tutorial_groups: 
            tutorial_groups[tg] = [] #creates new tg if not already present
        tutorial_groups[tg].append(student) #adds the student to their tg
    return tutorial_groups

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

def total_cgpa_variance(teams):
    if not teams or not all(teams):
        return 0
    
    team_averages = [sum(s['CGPA'] for s in team) / len(team) for team in teams] #calculate the average cgpa of each group
    overall_average = sum(team_averages) / len(team_averages) #calculate the average cgpa of the tg
    
    variance = sum((avg - overall_average) ** 2 for avg in team_averages) / len(team_averages) #calculates the variance of the average tg (standard s^2 variance)
    return variance

def optimize_teams_with_gpa_check(teams_in_tg):
    DIVERSITY_WEIGHT = 0.70
    CGPA_WEIGHT = 0.30  #weights

    for k in range(50): #this number is the number of tests to run
        current_diversity_score = sum(diversity_score(t) for t in teams_in_tg)
        current_cgpa_variance = total_cgpa_variance(teams_in_tg) #calculate the initial score and variance for this instance here

        if current_diversity_score == 0 and current_cgpa_variance < 0.001: #near perfect criteria, prevents unnecessary recursions
            break 

        best_improvement_score = 0
        best_swap_details = None #instansiation of vars

        for i in range(len(teams_in_tg)):
            for j in range(i + 1, len(teams_in_tg)): #every possible combination of teams

                for s1_idx in range(len(teams_in_tg[i])):
                    for s2_idx in range(len(teams_in_tg[j])): 
                        team1 = teams_in_tg[i]
                        team2 = teams_in_tg[j] #every possible combination of students within the teams

                        team1[s1_idx], team2[s2_idx] = team2[s2_idx], team1[s1_idx] #simulate the swap

                        new_diversity_score = sum(diversity_score(t) for t in teams_in_tg)
                        new_cgpa_variance = total_cgpa_variance(teams_in_tg) #new scores for the swap
                        
                        diversity_improvement = current_diversity_score - new_diversity_score # change in diversity score, we want this to be positive 
                        cgpa_improvement = current_cgpa_variance - new_cgpa_variance # change in variance, we want this to be positive

                        total_improvement = (diversity_improvement * DIVERSITY_WEIGHT) + (cgpa_improvement * CGPA_WEIGHT)#weighted improvement

                        if total_improvement > best_improvement_score:
                            best_improvement_score = total_improvement
                            best_swap_details = (i, j, s1_idx, s2_idx) #stores the swap details if this is the best possible swap

                        team1[s1_idx], team2[s2_idx] = team2[s2_idx], team1[s1_idx]#swap back to check the other possibilities before moving on
        
        if best_swap_details:
            i, j, s1, s2 = best_swap_details
            teams_in_tg[i][s1], teams_in_tg[j][s2] = teams_in_tg[j][s2], teams_in_tg[i][s1]#sets the best swap found
        else:
            break #if we cant find an improvement, stops the loop
            
    return teams_in_tg

def data_compilation(all_optimized_tgs): #prepares data for csv writing and assigns team numbers
    final_student_list = []
    sorted_tg_names = sorted(all_optimized_tgs.keys())

    for tg_name in sorted_tg_names:
        list_of_teams = all_optimized_tgs[tg_name]#grabs the list of teams in a tg
        for team_index, team in enumerate(list_of_teams):
            team_number = team_index + 1 # adds a group number 
            for student in team:
                student["Team Assigned"] = team_number #assigns the group number to the student
                final_student_list.append(student) #adds the student, with all their data into the list as a list
    return final_student_list

def write_output_csv(final_student_list, output_path="final_teams_gpa_optimized.csv"):
    if not final_student_list:
        print("No data available to write.") #incase of faulty inputs
        return
    
    headers = ["Tutorial Group", "Team Assigned", "Student ID", "Name", "School", "Gender", "CGPA"] #initialise the headers
    
    output_data = [{header: student.get(header) for header in headers} for student in final_student_list]

    with open(output_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_data) #write file
    print(f"Successfully created GPA-optimized allocation file: {output_path}")

def GPAoptimized(file_in):
    data = read_student_data(file_in) #reads data
    
    if data: #incase the data is invalid
        tutorial_groups = students_by_tg(data)
        all_optimized_teams = {}
            
        times = []

        for tg_name, students in tutorial_groups.items():
            start = time.time()

            print(f"Processing Tutorial Group: {tg_name}...")
            initial_teams = snake_draft(students)
            optimized_teams = optimize_teams_with_gpa_check(initial_teams)
            all_optimized_teams[tg_name] = optimized_teams

            times.append(time.time() - start)

        final_list = data_compilation(all_optimized_teams)
        output_path = os.path.dirname(__file__).replace("algorithms", "") + "tmp"
        write_output_csv(final_list, f"{output_path}/final_teams_gpa_optimized.csv")

        with open(f"{output_path}/GPAoptimized.txt", 'w') as file:
            for t in times:
                file.write(f"{t}\n")