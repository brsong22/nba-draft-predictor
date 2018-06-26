import csv
import matplotlib.pyplot as plt
import numpy as np

#read csv data (just test with one year's data for now)
#[2018] Draft Prospect Stats.csv
#[2018] Draft Team Order and Stats Rankings.csv
#[2018] Draft Team Order and Stats Totals.csv
team_stat_totals = {}
with open('[2017] Team Draft Order and Stats Totals.csv', newline='') as stat_totals_file:
	stats_headers = []
	team_stat_rows = csv.reader(stat_totals_file, delimiter=',')
	for row_index, stat_row in enumerate(team_stat_rows):
		if row_index == 0:
			stats_headers = stat_row
		else:
			team_stat_totals[stat_row[0]] = {stats_headers[1]: stat_row[1],
											 stats_headers[2]: stat_row[2],
											 stats_headers[3]: stat_row[3],
											 stats_headers[4]: stat_row[4],
											 stats_headers[5]: stat_row[5],
											 stats_headers[6]: stat_row[6],
											 stats_headers[7]: stat_row[7],
											 stats_headers[8]: stat_row[8],
											 stats_headers[9]: stat_row[9],
											 stats_headers[10]: stat_row[10],
											 stats_headers[11]: stat_row[11],
											 stats_headers[12]: stat_row[12]}

player_stat_totals = {}
with open('[2017] Drafted Player Stats.csv', newline='') as player_totals_file:
	stats_headers = []
	player_stat_rows = csv.reader(player_totals_file, delimiter=',')
	for row_index, stat_row in enumerate(player_stat_rows):
		if row_index == 0:
			stats_headers = stat_row
		else:
			player_stat_totals[stat_row[0]] = {stats_headers[1]: stat_row[1],
											   stats_headers[2]: stat_row[2],
											   stats_headers[3]: stat_row[3],
											   stats_headers[4]: stat_row[4],
											   stats_headers[5]: stat_row[5],
											   stats_headers[6]: stat_row[6],
											   stats_headers[7]: stat_row[7],
											   stats_headers[8]: stat_row[8],
											   stats_headers[9]: stat_row[9],
											   stats_headers[10]: stat_row[10],
											   stats_headers[11]: stat_row[11],
											   stats_headers[12]: stat_row[12]}

pct_stats = ['3pp', '2pp', 'ftp']
vol_stats = ['3pa', '2pa', 'fta', 'orb', 'drb', 'ast', 'stl', 'blk']


team_pct_totals = [float(team_stat_totals[str(1)].get(x))*100 for x in pct_stats]
print(team_pct_totals)
team_vol_totals = [float(team_stat_totals[str(1)].get(x))*100 for x in vol_stats]

player_pct_totals = [float(player_stat_totals[str(1)].get(x))*100 for x in pct_stats]
print(player_pct_totals)
player_vol_totals = [float(player_stat_totals[str(1)].get(x))*100 for x in vol_stats]

x_ind = np.arange(len(pct_stats))
y_ind = np.arange(0, 101, 10)
fig, ax = plt.subplots()
team_pct_graph = ax.bar(x_ind, team_pct_totals, width=-.25, align='edge', color='b', edgecolor='black')
for i, val in enumerate(team_pct_totals):
	ax.text(i-.21, val+2, str(val), color='black', va='center', fontweight='bold')
player_pct_graph= ax.bar(x_ind, player_pct_totals, width=.25, align='edge', color='r', edgecolor='black')
for i, val in enumerate(player_pct_totals):
	ax.text(i+.05, val+2, str(val), color='black', va='center', fontweight='bold')
ax.set_title('Shot percentage by Team and Drafted Player')
ax.set_xlabel('Stat Category')
ax.set_ylabel('Percent (%)')
ax.set_xticks(x_ind)
ax.set_xticklabels(pct_stats)
ax.set_yticks(y_ind)
ax.legend((team_pct_graph[0], player_pct_graph[0]), (team_stat_totals['1'].get('name'), player_stat_totals['1'].get('name')))
plt.show()