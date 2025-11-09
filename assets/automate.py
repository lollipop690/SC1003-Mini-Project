import os
import csv
import copy

from algorithms.snakedraft import snakedraft
from algorithms.genderpriority import genderpriority
from algorithms.outlierfocused import outlierfocused
from algorithms.GPAoptimized import GPAoptimized
from algorithms.randomized import randomized

from data_visualization import data_visualization

# ==============================================================================
# 1. READ AND COMPILE STUDENT DATA
# ==============================================================================

"""
Copied from modify_data.py

Basically the same functions for extracting data from csv file
"""

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

# ==============================================================================
# 2. COMPILE FINALE DATA AND WRITE OUTPUT
# ==============================================================================

"""
Copied form main.ipynb

Has the same functionality of compiling and outputting data into a csv file
"""

def data_compilation(all_optimized_tgs): #prepares data for csv writing and assigns team numbers
    final_student_list = []
    sorted_tg_names = sorted(all_optimized_tgs.keys())

    for tg_name in sorted_tg_names:
        list_of_teams = all_optimized_tgs[tg_name]#grabs the list of teams in a tg
        for team_index, team in enumerate(list_of_teams):
            team_number = team_index + 1 # adds a group number 
            for student in team:
                student["Tutorial Group"] = tg_name
                student["Team Assigned"] = team_number #assigns the group number to the student
                final_student_list.append(student) #adds the student, with all their data into the list as a list
    return final_student_list

def write_output_csv(final_student_list, output_path="final_teams.csv"):
    if not final_student_list:
        print("No data available to write.") #incase of faulty inputs
        return
    
    headers = ["Tutorial Group", "Student ID", "Name", "School", "Gender", "CGPA", "Team Assigned"] #initialise the headers
    
    output_data = [{header: student.get(header) for header in headers} for student in final_student_list]

    with open(output_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_data) #write file
    print(f"Successfully created GPA-optimized allocation file: {output_path}")


"""
INPUT: data: tuple -> data[0] is the resultant data from an algorithm, data[1] is the execution times data

This function is for outputting the results of the algorithm and the execution times data
"""

def write_analysis_data(data, name):
    teams = data[0]
    times = data[1]

    final_list = data_compilation(teams)
    output_path = os.path.dirname(__file__) + "/tmp"
    write_output_csv(final_list, f"{output_path}/final_teams_{name}.csv")

    if (len(times) != 0):
        with open(f"{output_path}/{name}.txt", 'w') as file:
            for t in times:
                file.write(f"{t}\n")


# ==============================================================================
# 3. MAIN
# ==============================================================================


# The Test cases
FILES = {
    "Normal": "records_normal.csv",
    "CGPA": "records_cgpa.csv",
    "GENDER": "records_gender.csv",
    "SCHOOL": "records_school.csv",
    "MIXED": "records_mixed.csv"
}

filepath = os.path.dirname(__file__) + "/analysis_plots_final"

# Iterate through each test cases
for option, filename in FILES.items():

    #Extract the data from a test case
    student_data = read_student_data(f"{filepath}/{option}/{filename}")
    tutorial_groups = students_by_tg(student_data)

    # Algorithms testing for a test case
    write_analysis_data(snakedraft(copy.deepcopy(tutorial_groups)), "snake_draft")
    write_analysis_data(genderpriority(copy.deepcopy(tutorial_groups)), "gender_priority")
    write_analysis_data(outlierfocused(copy.deepcopy(tutorial_groups)), "outlier_focused")
    write_analysis_data(GPAoptimized(copy.deepcopy(tutorial_groups)), "gpa_optimized")

    # Anomaly
    write_output_csv(randomized(copy.deepcopy(tutorial_groups)), f"{os.path.dirname(__file__) + "/tmp"}/final_teams_randomized.csv")

    # Data visualization for a test case
    data_visualization(option)

    print(f"\nProcessed {option}!!!\n")
