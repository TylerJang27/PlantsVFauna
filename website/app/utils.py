import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta as td
import random

def create_graph(times, filename):
    fig = plt.figure(num=1, clear=True)
    ax = fig.add_subplot(1, 1, 1)
    ax.hist(times, bins=10, edgecolor = "black")
    ax.set(xlabel="Time", ylabel="Pests Detected")
    ax.set_title("Pests Detected in Last 24 Hours")
    # ax.grid(True)
    fig.tight_layout()
    fig.savefig(filename)

if __name__ == "__main__":
    filename="here.png"
    times = []
    t = dt.now()
    for k in range(20):
        t -= td(minutes=(12*random.randint(0, 3)))
        times += [t]
    create_graph(times, filename)


