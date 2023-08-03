import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("nutrition.csv")

# Convert timestamp to datetime format
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Subtract 2 hours from each timestamp
df["timestamp"] = df["timestamp"] - pd.DateOffset(hours=2)

# Extract the date from the timestamp
df["date"] = df["timestamp"].dt.date

# Group by date and sum calories
grouped = df.groupby("date")["calories"].sum()

# Plot the data
ax = grouped.plot(kind="bar", ylim=(0, 3000))

# Add horizontal lines at y = 1800 (green), 2200 (yellow), and 2500 (red)
plt.axhline(y=1800, color='green', linestyle='--')
plt.axhline(y=2200, color='yellow', linestyle='--')
plt.axhline(y=2500, color='red', linestyle='--')

# Annotate bars with calorie values
for i, v in enumerate(grouped.values):
    ax.text(i, v + 50, int(v), ha="center")

plt.ylabel("Total Calories")
plt.title("Calories per Day")

# Save the figure as a .png image
plt.savefig("calories.png")
