import os
import matplotlib.pyplot as plt

#Measure execution time of each algorithm
def read_execution_time(filename):
    with open(filename, 'r') as file:
        times = []
        
        time = file.readline()
        while (time != ""):
            times.append(float(time))
            time = file.readline()

    return times

fig, ax = plt.subplots(2, 2)
ax[0, 0].plot(read_execution_time("./tmp/snake_draft.txt"), color = 'b')
ax[0, 1].plot(read_execution_time("./tmp/hardgendercap.txt"), color = 'g')
ax[1, 0].plot(read_execution_time("./tmp/outlierfocused.txt"), color = 'm')
ax[1, 1].plot(read_execution_time(".tmp/optimization.txt"), color = 'y')

ax[0, 0].set_title("Snake Draft")
ax[0, 1].set_title("Hard Gender Cap")
ax[1, 0].set_title("Outlier Focused")
ax[1, 1].set_title("GPA Optimized")

ax[0, 0].set_ylabel("seconds")
ax[0, 1].set_ylabel("seconds")
ax[1, 0].set_ylabel("seconds")
ax[1, 1].set_ylabel("seconds")

plt.tight_layout()
plt.savefig(os.path.join("analysis_plots_final", "execution_time.png"))