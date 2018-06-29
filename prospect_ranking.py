import matplotlib.pyplot as plt
import numpy as np
import csv


def update_annotation(bar):
	x = bar.get_x()+bar.get_width()/2
	y = bar.get_y()+bar.get_height()
	annotations.xy = (x,y)
	text = "pick:{}\nname:{}\nrating:{:.2f}".format(int(x)+1, rank_by_rating[int(x)][1], float(rank_by_rating[int(x)][2]))
	annotations.set_text(text)
	annotations.get_bbox_patch().set_alpha(1)

def hover(event):
	visible = annotations.get_visible()
	if event.inaxes == ax:
		for bar in bar_chart:
			container, index = bar.contains(event)
			if container:
				update_annotation(bar)
				annotations.set_visible(True)
				fig.canvas.draw_idle()
				return
	if visible:
		annotations.set_visible(False)
		fig.canvas.draw_idle()

#player rating formula taken from 
#https://support.fantasypros.com/hc/en-us/articles/115001315747-How-are-the-NBA-Player-Rater-scores-calculated-
years = ['2017', '2016', '2015', '2014', '2013']
for i, y in enumerate(years):
	with open('[' + y + '] Drafted Player Stats.csv', newline='') as player_totals_file:
		stats_headers = []
		player_stat_rows = csv.reader(player_totals_file, delimiter=',')
		player_stat_totals = {}
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

	stat_means = {}
	for p_key, p_stats in player_stat_totals.items():
		for stat_name, stat_value in p_stats.items():
			if not stat_name == 'name':
				if stat_name not in stat_means:
					stat_means[stat_name] = [stat_value]
				else:
					stat_means[stat_name].append(stat_value)

	for key, value_list in stat_means.items():
		stat_vals = list(map(float, value_list))
		stat_vals_clean = [x for x in stat_vals if not np.isnan(x)]
		stat_means[key] = np.mean(stat_vals_clean)

	player_ratings = {}
	for pick_num, player_stats in player_stat_totals.items():
		player_name = player_stats.get('name')
		player_overall = 0.0
		for stat in player_stats:
			if not stat == 'name':
				player_stat = float(player_stats.get(stat))
				player_stat = 0.0 if np.isnan(player_stat) else player_stat
				player_overall += player_stat - stat_means.get(stat)
		player_ratings[pick_num] = {'name': player_stats.get('name'), 'rating': str(player_overall)}


	with open('[' + y + '] Player Overall Rankings.csv', 'w+') as ranking_file:
			ranking_file.write("pick,name,rating\n")
			for num, vals in player_ratings.items():
				ranking_file.write(num + ",")
				ranking_file.write(",".join(list(vals.values())))
				ranking_file.write("\n")
	ranking_file.close()

	rank_by_rating = []
	for pick_num, player in player_ratings.items():
		rank_by_rating.append((pick_num, player.get('name'), player.get('rating')))

	#let's implement the sorting ourselves for FUN!?
	rank_by_rating.sort(key=lambda tup: float(tup[0]))

	fig, ax = plt.subplots(figsize=(10, 5))
	x_ind = np.arange(len(rank_by_rating)+1) #x-coords
	# y_ind = np.arange(np.floor(float(min(rank_by_rating, key=lambda tup: float(tup[2]))[2]))-3, np.ceil(float(max(rank_by_rating, key=lambda tup: float(tup[2]))[2]))+3, 1)
	bar_chart = ax.bar([x[0] for x in rank_by_rating], [int(round(float(x[2]))) for x in rank_by_rating], width=1, color='r', edgecolor='black', label='Rating')
	# for i, t in enumerate(rank_by_rating):
	# 	pct.text(i-.21, val+2, str(val), color='black', va='center', fontweight='bold')
	annotations = ax.annotate("", xy=(0,0), xytext=(0,-10), xycoords='data', textcoords="offset points",
							  bbox=dict(boxstyle="square", fc="white", ec="black", lw=2),
							  arrowprops=dict(arrowstyle="-"))
	annotations.set_visible(False)

	fig.canvas.mpl_connect("motion_notify_event", hover)

	ax.set_title('Rating of Drafted Players')
	ax.set_xlabel('Pick Number')
	ax.set_ylabel('Rating')
	ax.set_xticklabels([x[0] for x in rank_by_rating])
	ax.legend()

	fig_name = '[' + y + '] player ranking draft order.png'
	plt.savefig(fig_name)
	plt.show()
