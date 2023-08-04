import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("nutrition.csv")

# Convert timestamp to datetime format in UTC
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

# Subtract 2 hours from each timestamp to make 00:00 to 02:00 as previous day
df["timestamp"] = df["timestamp"] - pd.DateOffset(hours=2)

# Define function to categorize time of day
def time_of_day(t):
    if 2 <= t.hour < 12:
        return '2-12'
    elif 12 <= t.hour < 17:
        return '12-17'
    elif 17 <= t.hour < 22:
        return '17-22'
    else:
        return '22-2'  # now this includes 00:00 to 02:00 as it is part of previous day

# Apply function to timestamp
df["time_of_day"] = df["timestamp"].apply(time_of_day)

# Extract the date from the timestamp
df["date"] = df["timestamp"].dt.date

# Group by date and time of day and sum calories
grouped = df.groupby(["date", "time_of_day"])["calories"].sum().unstack().fillna(0)

# Check if the columns exist, if not add them with default value of 0
for col in ['2-12', '12-17', '17-22', '22-2']:
    if col not in grouped.columns:
        grouped[col] = 0

# Order the columns
grouped = grouped[['2-12', '12-17', '17-22', '22-2']]

# Calculate total calories for each day
grouped['Total'] = grouped.sum(axis=1)

# Plot the data
ax = grouped[['2-12', '12-17', '17-22', '22-2']].plot(kind="bar", stacked=True, ylim=(0, 3000))

# Annotate bars with total calorie values
for i, v in enumerate(grouped['Total'].values):
    ax.text(i, v + 50, int(v), ha="center")

# Add horizontal lines at y = 1800 (green), 2200 (yellow), and 2500 (red)
plt.axhline(y=1800, color='green', linestyle='--')
plt.axhline(y=2200, color='yellow', linestyle='--')
plt.axhline(y=2500, color='red', linestyle='--')

plt.ylabel("Total Calories")
plt.title("Calories per Day")

# Save the figure as a .png image
plt.savefig("calories.png")
