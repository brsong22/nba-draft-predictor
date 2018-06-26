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

fig, (pct, vol) = plt.subplots(1, 2)


team_pct_totals = [float(team_stat_totals[str(1)].get(x))*100 for x in pct_stats]
team_vol_totals = [float(team_stat_totals[str(1)].get(x)) for x in vol_stats]

player_pct_totals = [float(player_stat_totals[str(1)].get(x))*100 for x in pct_stats]
player_vol_totals = [float(player_stat_totals[str(1)].get(x)) for x in vol_stats]

x_ind = np.arange(len(pct_stats))
y_ind = np.arange(0, 101, 10)

team_pct_graph = pct.bar(x_ind, team_pct_totals, width=-.25, align='edge', color='b', edgecolor='black')
for i, val in enumerate(team_pct_totals):
	pct.text(i-.21, val+2, str(val), color='black', va='center', fontweight='bold')
player_pct_graph= pct.bar(x_ind, player_pct_totals, width=.25, align='edge', color='r', edgecolor='black')
for i, val in enumerate(player_pct_totals):
	pct.text(i+.05, val+2, str(val), color='black', va='center', fontweight='bold')
pct.set_title('Shot percentage by Team and Drafted Player')
pct.set_xlabel('Stat Category')
pct.set_ylabel('Percent (%)')
pct.set_xticks(x_ind)
pct.set_xticklabels(pct_stats)
pct.set_yticks(y_ind)
pct.legend((team_pct_graph[0], player_pct_graph[0]), (team_stat_totals['1'].get('name'), player_stat_totals['1'].get('name')))

x_ind = np.arange(len(vol_stats))
y_ind = np.arange(0, 200, 20)
team_vol_graph = vol.bar(x_ind, team_vol_totals, width=-.5, align='edge', color='green', edgecolor='black')
for i, val in enumerate(team_vol_totals):
	vol.text(i-.5, val+2, str(val), color='black', va='center', fontweight='bold')
player_vol_graph = vol.bar(x_ind, player_vol_totals, width=.5, align='edge', color='orange', edgecolor='black')
for i, val in enumerate(player_pct_totals):
	vol.text(i, val+2, str(val), color='black', va='center', fontweight='bold')
	pct.set_title('Shot percentage by Team and Drafted Player')
vol.set_xlabel('Stat Category')
vol.set_ylabel('Number of Attempts')
vol.set_xticks(x_ind)
vol.set_xticklabels(vol_stats)
vol.set_yticks(y_ind)
vol.legend((team_vol_graph[0], player_vol_graph[0]), (team_stat_totals['1'].get('name'), player_stat_totals['1'].get('name')))
plt.show()