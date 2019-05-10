import os
import re
import glob

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set(
    color_codes=True,
    style="ticks", 
    palette="pastel")


f, ax = plt.subplots(figsize=(7, 7))
ax.set(xscale="linear", yscale="log")

times = glob.glob("{}/*times*.csv".format(os.getcwd()))

players = {}
for f in times:
    player_name = re.match(r"^.*?([A-Za-z\{\}]+)_.*$", os.path.basename(f)).group(1)
    if player_name == "{}": # just a bug, move on
        continue
    players[player_name] = pd.read_csv(f)

data = []
for name, times in players.items():
    for time in times.values:
        data.append([name, time[0]])

df = pd.DataFrame(data, columns=['name','time'])
plot = sns.boxplot(
    x="name", 
    y="time", 
    palette=['b','y','r'],
    data=df)

sns.despine(offset=10, trim=True)


figure = plot.get_figure()

figure.suptitle('Player Turn Time Taken')
plt.xlabel('Player')
plt.ylabel('Time (ms)')

figure.savefig("time_evaluation.png")


