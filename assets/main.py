import os

from algorithms.snakedraft import snakedraft
from algorithms.hardgendercap import hardgendercap
from algorithms.outlierfocused import outlierfocused
from algorithms.GPAoptimized import GPAoptimized
from algorithms.randomized import randomized

from data_visualization import data_visualization

FILES = {
    "Normal": "records_normal.csv",
    "CGPA": "records_cgpa.csv",
    "GENDER": "records_gender.csv",
    "SCHOOL": "records_school.csv",
    "MIXED": "records_mixed.csv"
}

filepath = os.path.dirname(__file__) + "/analysis_plots_final"

for option, filename in FILES.items():
    snakedraft(f"{filepath}/{option}/{filename}")
    hardgendercap(f"{filepath}/{option}/{filename}")
    outlierfocused(f"{filepath}/{option}/{filename}")
    GPAoptimized(f"{filepath}/{option}/{filename}")
    randomized(f"{filepath}/{option}/{filename}")

    data_visualization(option)

    print(f"\nProcessed {option}!!!\n")
