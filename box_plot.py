import seaborn as sns
import matplotlib.pyplot as plt

sns.set(
    color_codes=True,
    style="ticks", 
    palette="pastel")


f, ax = plt.subplots(figsize=(7, 7))
ax.set(xscale="linear", yscale="log")


tips = sns.load_dataset("tips")
plot = sns.boxplot(
    x="day", 
    y="total_bill", 
    palette=["m"],
    data=tips)

sns.despine(offset=10, trim=True)


figure = plot.get_figure()

figure.suptitle('Player Turn Time Taken')
plt.xlabel('Player')
plt.ylabel('Time (ms)')

figure.savefig("time_evaluation.png")
