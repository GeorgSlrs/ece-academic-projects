import csv
import matplotlib.pyplot as plt


filenames = ["realisation1.csv", "realisation2.csv", "realisation3.csv", "realisation4.csv"]


def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        
        return [float(row[0]) for row in reader]


fig, axs = plt.subplots(len(filenames), 1, figsize=(10, 8), sharex=True)

for i, filename in enumerate(filenames):
    data = read_csv(filename)
    

    mean_value = sum(data) / len(data)
    
    axs[i].plot(data)
    axs[i].axhline(y=mean_value, color='r', linestyle='--', label=f"Mean: {mean_value:.2f}")
    axs[i].set_title(filename)
    axs[i].grid(True)
    axs[i].legend()


plt.tight_layout()
plt.xlabel("Sample index")
plt.show()
