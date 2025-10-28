import os
import csv
import random
import matplotlib.pyplot as plt

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

def write_output_csv(final_student_list, output_path="final_teams.csv"):
    if not final_student_list:
        print("No data available to write.") #incase of faulty inputs
        return
    
    headers = ["Tutorial Group", "Student ID", "Name", "School", "Gender", "CGPA"] #initialise the headers
    
    output_data = [{header: student.get(header) for header in headers} for student in final_student_list]

    with open(output_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_data) #write file
    print(f"Successfully created GPA-optimized allocation file: {output_path}")

#======================================================================

def modifyCGPA(students, variation): 
    mean = 2.5 # DO NOT CHANGE PLEASE (need to figure out for random.uniform(3, 4))
    sd = 0.1 + 1.9 * variation
    outlier_chance = 0.1 + 0.9 * variation

    for student in students:
        #On a dataset with its data bounded by [0, 5], the max sd = 2.5
        if (random.random() < outlier_chance): #Generate outliers by chance
            if (random.random() < 0.5): #Lower outliers
                student["CGPA"] =  round(random.uniform(-2.5, -2) + mean, 2)
            else: #Uppers outliers
                student["CGPA"] = round(random.uniform(2, 2.5) + mean, 2)
            
        else: #Generate data with standard deviation of the range [-sd, sd]
            student["CGPA"] = round(random.uniform(-sd, sd) + mean, 2) 

    return students

def modifyGender(students, variation):   
    number_of_students = len(students)

    dominant_gender = students[0]["Gender"]
    dominant_count = int(number_of_students // 2 * min(1 + random.uniform(0.95, 1.05) * variation, 2))

    gender = [] 
    for i in range(0, dominant_count):
        gender.append(dominant_gender) #Generate `dominant_count` of the dominant gender

    other_gender = "Female" if dominant_gender == "Male" else "Male" 
    for i in range(0, number_of_students - dominant_count):
        gender.append(other_gender) #Add the remaining non-dominant gender

    random.shuffle(gender)
    for i in range(0, number_of_students):
        students[i]["Gender"] = gender[i] #Assign the generated genders to the students]

    return students

def modifySchool(students, variation): 
    number_of_students = len(students)

    schools_list = []
    for student in students:
        if (student["School"] not in schools_list): schools_list.append(student["School"])

    dominant_school = schools_list[0]
    dominant_count = int(min(random.uniform(0.95, 1.05) * variation * number_of_students, number_of_students))
    
    schools = []
    for i in range(0, dominant_count):
        schools.append(dominant_school) #Generate the dominant school 
    schools_list.pop(0)

    for i in range(0, number_of_students - dominant_count):
        schools.append(random.choice(schools_list)) #Add the remaining schools

    random.shuffle(schools)
    for i in range(0, number_of_students):
        students[i]["School"] = schools[i] #Assign the generated schools to the students

    return students

#======================================================================

records = read_student_data("records.csv")
tutorial_groups = students_by_tg(records)

count = 1
student_list = []
for tg, students in tutorial_groups.items():
    variation = count / 120

    tutorial_groups[tg] = modifyCGPA(students, variation)
    tutorial_groups[tg] = modifyGender(students, variation)
    tutorial_groups[tg] = modifySchool(students, variation)

    count += 1

    for student in students:
        student_list.append(student)

write_output_csv(student_list, "records_modified.csv")

#======================================================================

def total_cgpa_variance(students):
    overall_average = sum(s['CGPA'] for s in students) / len(students) #calculate the average cgpa of the students
    
    variance = sum((s['CGPA'] - overall_average) ** 2 for s in students) / len(students) #calculates the variance of the average tg (standard s^2 variance)
    return variance

def gender_score(students): #grades how diverse each group is(lower better)
    score = 0
    for student in students:
        if (student["Gender"] == "Male"): score += 1
        else: score -= 1

    return abs(score)

def school_score(students): #grades how diverse each group is(lower better)
    score = 0
    school_counts = {}

    for student in students:
        school_counts[student['School']] = school_counts.get(student['School'], 0) + 1

    for count in school_counts.values():
        if count >= 2:
            score += (count - 2) * 10 #every 2nd person onwards of the same school will add 10 to the diversity score

    return score

def plotGraph(tutorial_groups):
    data1, data2, data3 = [], [], []
    for tg, students in tutorial_groups.items():
        cgpa = total_cgpa_variance(students)
        gender = gender_score(students)
        school = school_score(students)

        #Percentage of CGPA variance (Maximum variance for a [0, 5] dataset = 25/4)
        data1.append(cgpa / (25 / 4) * 100)
        data2.append(gender / 50 * 100)
        data3.append(school / 480 * 100)

    fig, axis = plt.subplots(3)

    #CGPA
    axis[0].plot(data1, color = "red")
    axis[0].set_title("CGPA")
    axis[0].set_yticks([0, 25, 50, 75, 100])
    axis[0].set_ylabel("%")

    #GENDER
    axis[1].plot(data2, ",-g")
    axis[1].set_title("GENDER")
    axis[1].set_yticks([0, 25, 50, 75, 100])
    axis[1].set_ylabel("%")

    #SCHOOLS
    axis[2].plot(data3, ",-b")
    axis[2].set_title("SCHOOLS")
    axis[2].set_yticks([0, 25, 50, 75, 100])
    axis[2].set_ylabel("%")

    plt.tight_layout()
    plt.savefig(os.path.join("Mixed.png"))

records = read_student_data("records_modified.csv")
tutorial_groups = students_by_tg(records)

plotGraph(tutorial_groups)