import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Load team metrics
metrics = pd.read_csv('team_metrics.csv')

# Sorted Win Rate Difference
wr_sorted = metrics['win_rate_diff'].sort_values()
teams = wr_sorted.index.tolist()
diffs = wr_sorted.values

teams       = metrics['home_team'].tolist()
home_wr     = metrics['home_win_rate']
away_wr     = metrics['away_win_rate']
score_diff  = metrics['score_diff']
x = list(range(len(teams)))
plt.figure()
plt.bar([i-0.2 for i in x], home_wr, width=0.4, label='Home Win Rate')
plt.bar([i+0.2 for i in x], away_wr, width=0.4, label='Away Win Rate')
plt.xticks(x, teams, rotation=45, ha='right')
plt.ylabel('Win Rate')
plt.title('Home vs Away Win Rates by Team')
plt.legend()
plt.tight_layout()
plt.show()

metrics = pd.read_csv('team_metrics.csv').set_index('home_team')
# Prepare figure
fig, ax = plt.subplots(figsize=(8, 6))
y_pos = list(range(len(teams)))
bars = ax.barh(y_pos, diffs, color='#0060B0')
ax.axvline(0, color='gray', linewidth=1)

# Remove default labels
ax.set_yticks(y_pos)
ax.set_yticklabels([])

# Determine logo x-position (just at left margin)
x_min, x_max = ax.get_xlim()
x_logo = x_min + (x_max - x_min) * 0.02  # 2% in from left edge

# Map team names to logo file paths
logo_paths = {
    "CTBC Brothers":    "logos/logo_brothers.png",
    "WeiChuan Dragons": "logos/logo_dragon.png",
    "Rakuten Monkeys":  "logos/logo_monkeys.png",
    "Uni-Lions":        "logos/logo_lions.png",
    "Fubon Guardians":  "logos/logo_fubon.png"
}

# Add logos at original label positions
for y, team in zip(y_pos, teams):
    img = plt.imread(logo_paths[team])
    imagebox = OffsetImage(img, zoom=0.25)  # increase zoom for larger logos
    ab = AnnotationBbox(
        imagebox, 
        (x_logo, y),
        frameon=False,
        xycoords='data'
    )
    ax.add_artist(ab)

ax.set_xlabel('Win Rate Difference (Home - Away)')
ax.set_title('Win Rate Difference by Team (Logos as Labels)')
plt.tight_layout()
plt.show()

# Repeat for Score Difference
sd_sorted = metrics['score_diff'].sort_values()
teams_sd = sd_sorted.index.tolist()
diffs_sd = sd_sorted.values

fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.barh(teams_sd, diffs_sd, color='#05AF7A')  # CPBL green

# Remove default labels and add logos
ax.set_yticks(y_pos)
ax.set_yticklabels([])
x_min, x_max = ax.get_xlim()
x_logo = x_min + (x_max - x_min) * 0.02
for y, team in zip(y_pos, teams_sd):
    img = plt.imread(logo_paths[team])
    imagebox = OffsetImage(img, zoom=0.25)
    ab = AnnotationBbox(imagebox, (x_logo, y), frameon=False, xycoords='data')
    ax.add_artist(ab)

ax.axvline(0, color='gray', linewidth=1)
ax.set_xlabel('Score Difference (Home - Away)')
ax.set_title('Score Difference by Team (Logos as Labels)')
plt.tight_layout()
plt.show()
