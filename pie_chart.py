import matplotlib.pyplot as plt

labels = 'Blue', 'Yellow', 'Red'
sizes = [15, 30, 45]
# explode = (0.02, 0.02, 0.02)
explode = (0, 0, 0)

fig1, ax1 = plt.subplots()
ax1.pie(
    sizes, 
    explode=explode, 
    labels=labels, 
    autopct='%1.1f%%',
    shadow=True, 
    startangle=90,
    colors=['skyblue','lemonchiffon','indianred'])
ax1.axis('equal')

# plt.show()

fig1.savefig("win_percent.png")

