import csv
import random
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.animation import FuncAnimation

# ==============================================================================
# 1. CONFIGURATION AND UTILITY FUNCTIONS
# ==============================================================================

# Consistent color scheme for all five methods being compared
PALETTE = {
    'Snake Draft': 'skyblue',
    'Gender Priority': 'lightgreen',
    'Outlier Focused': 'plum',
    'GPA Optimized': 'khaki',
    'Random': 'salmon'
}
LABELS = list(PALETTE.keys())

def read_allocation_data(file_path):
    """Reads a team allocation CSV into a list of dictionaries."""
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure all allocation scripts have been run.")
        return None

def group_data_by_team(student_data):
    """Groups a flat list of students into a dictionary of teams."""
    teams = {}
    if not student_data:
        return teams
    for student in student_data:
        team_id = f"{student.get('Tutorial Group', 'N/A')}-Team-{student.get('Team Assigned', 'N/A')}"
        if team_id not in teams:
            teams[team_id] = []
        student['CGPA'] = float(student['CGPA'])
        teams[team_id].append(student)
    return teams

# ==============================================================================
# 3. ANALYSIS AND STATISTICS
# ==============================================================================

def calculate_team_stats(teams_data):
    """Calculates statistics for each team (avg CGPA, gender/school counts)."""
    stats = {'avg_cgpas': [], 'gender_compositions': [], 'school_majorities': []}
    for team_id, students in teams_data.items():
        if not students: continue
        # CGPA Analysis
        cgpas = [s['CGPA'] for s in students]
        stats['avg_cgpas'].append(sum(cgpas) / len(cgpas))

        # Gender Analysis
        gender_counts = {'Male': 0, 'Female': 0}
        for s in students:
            gender_counts[s['Gender']] += 1
        comp_str = f"{gender_counts['Female']}F-{gender_counts['Male']}M"
        stats['gender_compositions'].append(comp_str)
        
        # School Analysis
        school_counts = {}
        for s in students:
            school_counts[s['School']] = school_counts.get(s['School'], 0) + 1

        #This one time checker if else if else is a bane to my existence
        if any(count >= 3 for count in school_counts.values()):
            if (len(stats["school_majorities"]) == 0): stats['school_majorities'].append(1)
            else: stats['school_majorities'].append(stats["school_majorities"][len(stats["school_majorities"]) - 1] + 1)
        else:
            if (len(stats["school_majorities"]) == 0): stats['school_majorities'].append(0)
            stats["school_majorities"].append(stats["school_majorities"][len(stats["school_majorities"]) - 1])
            
    return stats

#Measure execution time of each algorithm
def read_execution_time(filename):
    with open(filename, 'r') as file:
        times = []
        
        time = file.readline()
        while (time != ""):
            times.append(float(time))
            time = file.readline()

    return times

# ==============================================================================
# 4. PLOTTING FUNCTIONS
# ==============================================================================

def plot_cgpa_distribution(all_stats, save_path):
    """Creates a comparative box plot of average team CGPAs for all methods."""
    fig, ax = plt.subplots(figsize=(16, 8))

    def update(frame):
        ax.clear()
        ax.set_xticks(range(len(LABELS)), LABELS, rotation=15)
        ax.set_title(f"Comparison of Average Team CGPA Distribution (Frame: {frame + 1}/1200)", fontsize=16)
        ax.set_ylabel('Average CGPA')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        sns.boxplot([stats["avg_cgpas"][0:frame] for stats in all_stats], palette=list(PALETTE.values()))

        return ax,

    ani = FuncAnimation(fig, update, frames=1200, interval=50, repeat=True, blit=False)
    ani.save(save_path, writer="ffmpeg", fps=144)
    print(f"Saved CGPA distribution plot to {save_path}")

def plot_gender_balance(all_stats, save_path):
    """Creates a comparative bar chart of team gender compositions."""
    fig, ax = plt.subplots(figsize=(18, 10))
    
    width = 0.15
    offsets = [-2 * width, -width, 0, width, 2 * width]

    def update(frame):
        all_counts = [{k: stats['gender_compositions'][0:frame].count(k) for k in set(stats['gender_compositions'])} for stats in all_stats]

        all_keys = sorted(list(set.union(*(set(counts.keys()) for counts in all_counts))))

        ax.clear()
        ax.set_ylim(0, 800)
        ax.set_ylabel('Number of Teams')
        ax.set_title(f"Comparison of Team Gender Composition (Frame: {frame + 1}/1200)", fontsize=16)
        ax.set_xticks(range(len(all_keys)))
        ax.set_xticklabels(all_keys, rotation=45, ha="right")
        #ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for i, (label, counts) in enumerate(zip(LABELS, all_counts)):
            values = [counts.get(k, 0) for k in all_keys]
            ax.bar([j + offsets[i] for j in range(len(all_keys))], values, width, label=label, color=PALETTE[label])
        
        return ax,

    ani = FuncAnimation(fig, update, frames=1200, interval=50, repeat=True, blit=False)
    ani.save(save_path, writer="ffmpeg", fps=144)
    print(f"Saved gender balance plot to {save_path}")

def plot_school_diversity(all_stats, save_path):
    """Compares the number of teams with a school majority."""
    labels = ['Majority Exists', 'No Majority']
    x = range(len(labels))
    width = 0.15
    offsets = [-2 * width, -width, 0, width, 2 * width]

    fig, ax = plt.subplots(figsize=(12, 8))

    def update(frame):
        ax.clear()
        ax.set_ylim(0, 1200)
        ax.set_ylabel('Number of Teams')
        ax.set_title(f"Comparison of School Diversity in Teams (Majority >= 3) (Frame: {frame + 1}/1200)", fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        #ax.legend()
        
        for i, (label, stats) in enumerate(zip(LABELS, all_stats)):
            values = [stats['school_majorities'][frame], frame - stats['school_majorities'][frame]]
            ax.bar([j + offsets[i] for j in x], values, width, label=label, color=PALETTE[label])

    ani = FuncAnimation(fig, update, frames=1200, interval=50, repeat=True, blit=False)
    ani.save(save_path, writer="ffmpeg", fps=144)
    print(f"Saved school diversity plot to {save_path}")

def plot_execution_time(option):
    input_path = os.path.dirname(__file__) + f"/tmp"

    fig, ax = plt.subplots(2, 2)
    ax[0, 0].plot(read_execution_time(f"{input_path}/snakedraft.txt"), color = 'b')
    ax[0, 1].plot(read_execution_time(f"{input_path}/hardgendercap.txt"), color = 'g')
    ax[1, 0].plot(read_execution_time(f"{input_path}/outlierfocused.txt"), color = 'm')
    ax[1, 1].plot(read_execution_time(f"{input_path}/GPAoptimized.txt"), color = 'y')

    ax[0, 0].set_title("Snake Draft")
    ax[0, 1].set_title("Hard Gender Cap")
    ax[1, 0].set_title("Outlier Focused")
    ax[1, 1].set_title("GPA Optimized")

    ax[0, 0].set_ylabel("seconds")
    ax[0, 1].set_ylabel("seconds")
    ax[1, 0].set_ylabel("seconds")
    ax[1, 1].set_ylabel("seconds")

    plt.tight_layout()

    output_path = os.path.dirname(__file__) + f"/analysis_plots_final/{option}"
    plt.savefig(f"{output_path}/execution_time.png")

# ==============================================================================
# 5. MAIN EXECUTION BLOCK
# ==============================================================================

def data_visualization(option):
    input_path = os.path.dirname(__file__) + f"/tmp"
    FILES = {
        'Snake Draft': f"{input_path}/final_teams_snake_draft.csv",
        'Gender Priority': f"{input_path}/final_teams_gender_priority.csv",
        'Outlier Focused': f"{input_path}/final_teams_outlier_focused.csv",
        'GPA Optimized': f"{input_path}/final_teams_gpa_optimized.csv",
        "Random": f"{input_path}/finals_teams_randomized.csv"
    }
    
    all_data = {label: read_allocation_data(path) for label, path in FILES.items()}

    if all(all_data.values()):
        print("\n--- Analyzing All Allocations ---")
        
        all_teams = {label: group_data_by_team(data) for label, data in all_data.items()}
        all_stats = [calculate_team_stats(all_teams[label]) for label in LABELS]

        output_path = os.path.dirname(__file__) + f"/analysis_plots_final/{option}"

        plot_cgpa_distribution(all_stats, f"{output_path}/final_comparison_cgpa.mp4")
        plot_gender_balance(all_stats, f"{output_path}/final_comparison_gender.mp4")
        plot_school_diversity(all_stats, f"{output_path}/final_comparison_school.mp4")
        plot_execution_time(option)
            
        print(f"\nAll final comparison plots have been saved in the '{output_path}' folder.")
