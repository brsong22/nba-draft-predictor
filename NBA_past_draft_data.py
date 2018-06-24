from lxml import etree as et
from lxml import html
import urllib.request
from datetime import datetime
from slugify import slugify
import configparser
import regex as re

cfg = configparser.ConfigParser()
cfg.read("draft_predict.ini")
nba_url = cfg.get("Base", "Url")
cbb_url = cfg.get("Base", "CbbUrl")

prev_year = datetime.today().year-1
prev_draft_urls = []
for i in range(5):
	prev_draft_urls.append(nba_url + cfg.get("Draft", "DraftPath") + cfg.get("Draft", "PastDraftUrlPrefix") + str(prev_year-i) + cfg.get("Base", "FileExt"))
#only get the first 30 picks (round 1) of the draft 1-indexed
num_rd1_picks = list(range(1, 31))

draft_board = {}
# try:
# with urllib.request.urlopen('https://www.basketball-reference.com/euro/players/terrance-ferguson-1.html') as test:
	# print(test.getcode())
# except urllib.error.HTTPError as e:
# 	print(e.code)
	
# exit()
parser = et.HTMLParser()
for year_i, draft_url in enumerate(prev_draft_urls):
	with urllib.request.urlopen(draft_url) as draft_html:
		draft = et.parse(draft_html, parser)
	for pick_num in num_rd1_picks:
		#get team info
		draft_pick_num = draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[1]/a/text()')[0]
		draft_pick_team_abbr = draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[2]/a/text()')[0]
		draft_pick_team_abbr = 'NJN' if draft_pick_team_abbr == 'BRK' else draft_pick_team_abbr
		draft_pick_team_abbr = 'NOH' if draft_pick_team_abbr == 'NOP' else draft_pick_team_abbr
		draft_pick_team_abbr = 'CHA' if draft_pick_team_abbr == 'CHO' else draft_pick_team_abbr #typo on the webpage
		draft_pick_team_name = draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[2]/a/@title')[0]
		team_link = nba_url + cfg.get("Teams", "TeamPath") + "/" + draft_pick_team_abbr + cfg.get("Teams", "TeamStatRanksPage")
		print(team_link)
		with urllib.request.urlopen(team_link) as stats_html:
			team_stats = et.parse(stats_html, parser)
		rank_3pa = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[17]//text()')[0]
		rank_3pp = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[18]//text()')[0]
		rank_2pa = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[20]//text()')[0]
		rank_2pp = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[21]//text()')[0]
		rank_fta = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[23]//text()')[0]
		rank_ftp = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[24]//text()')[0]
		rank_orb = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[25]//text()')[0]
		rank_drb = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[26]//text()')[0]
		rank_ast = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[28]//text()')[0]
		rank_stl = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[29]//text()')[0]
		rank_blk = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[30]//text()')[0]
		rank_pts = team_stats.xpath('//*[@id="stats"]/tbody/tr[' + str(year_i + 1) + ']/td[33]//text()')[0]

		#get player info
		prospect_stats = {}
		draft_pick_player_name = draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[3]/a/text()')[0]
		player_name_arr = draft_pick_player_name.split(" ")
		print(player_name_arr)
		for i, n in enumerate(player_name_arr):
			player_name_arr[i] = re.sub(r'[^a-zA-Z0-9\-]+', '', n)
		print(player_name_arr)
		player_name_clean = slugify("-".join(player_name_arr))
		player_euro_url = nba_url + cfg.get("Players", "EuroPath") + "/" + player_name_clean + "-1" + cfg.get("Base", "FileExt")
		player_cbb_url = cbb_url + cfg.get("Players", "CbbPath") + "/" + player_name_clean + "-1" + cfg.get("Base", "FileExt")
		euro = False
		print(draft_pick_player_name)
		print(player_euro_url)
		print(player_cbb_url)
		try:
			with urllib.request.urlopen(player_euro_url) as eu:
				print("euro")
				player_url = player_euro_url
				euro = True
		except urllib.error.HTTPError as e:
			print("not euro")
			try:
				with urllib.request.urlopen(player_cbb_url) as us:
					print("us")
					player_url = player_cbb_url
			except urllib.error.HTTPError as e:
				print("not us")
				player_url = ""
		print(player_url)
		if not player_url == "":
			with urllib.request.urlopen(player_url) as player_stats_html:
				player_stats = et.parse(player_stats_html, parser)
			if euro:
				if player_stats.xpath('//*[@id="per_gameEUR0"]/thead/tr/th[2]/text()'):
					p_3pa = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[10]/text()')[0]
					p_3pp = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[11]/text()')[0]
					p_2pa = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[13]/text()')[0]
					p_2pp = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[14]/text()')[0]
					p_fta = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[16]/text()')[0]
					p_ftp = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[17]/text()')[0]
					p_orb = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[18]/text()')[0]
					p_drb = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[19]/text()')[0]
					p_ast = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[21]/text()')[0]
					p_stl = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[22]/text()')[0]
					p_blk = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[23]/text()')[0]
					p_pts = player_stats.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[26]/text()')[0]
				else:
					p_3pa = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[9]/text()')[0]
					p_3pp = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[10]/text()')[0]
					p_2pa = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[12]/text()')[0]
					p_2pp = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[13]/text()')[0]
					p_fta = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[15]/text()')[0]
					p_ftp = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[16]/text()')[0]
					p_orb = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[17]/text()')[0]
					p_drb = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[18]/text()')[0]
					p_ast = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[20]/text()')[0]
					p_stl = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[21]/text()')[0]
					p_blk = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[22]/text()')[0]
					p_pts = player_stats.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[25]/text()')[0]
			else:
				player_3pa = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[13]//text()')[0]
				player_3pp = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[14]//text()')[0]
				player_2pa = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[10]//text()')[0]
				player_2pp = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[11]//text()')[0]
				player_fta = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[16]//text()')[0]
				player_ftp = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[17]//text()')[0]
				player_orb = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[18]//text()')[0]
				player_drb = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[19]//text()')[0]
				player_ast = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[21]//text()')[0]
				player_stl = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[22]//text()')[0]
				player_blk = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[23]//text()')[0]
				player_pts = player_stats.xpath('//*[@id="players_per_game"]/tfoot/tr/td[26]//text()')[0]
		else:
			player_3pa = '0'
			player_3pp = '0'
			player_2pa = '0'
			player_2pp = '0'
			player_fta = '0'
			player_ftp = '0'
			player_orb = '0'
			player_drb = '0'
			player_ast = '0'
			player_stl = '0'
			player_blk = '0'
			player_pts = '0'
		prospect_stats[draft_pick_player_name] = {'3pa': player_3pa,
												  '3pp': player_3pp,
												  '2pa': player_2pa,
												  '2pp': player_2pp,
												  'fta': player_fta,
												  'ftp': player_ftp,
												  'orb': player_orb,
												  'drb': player_drb,
												  'ast': player_ast,
												  'stl': player_stl,
												  'blk': player_blk,
												  'pts': player_pts}

	# with open(str(prev_year - year_i) + '_Draft Prospects Stats.csv', 'w+') as prosp_file:
	# 	for p_name, p_stats in prospect_stats.items():
	# 		prosp_file.write(p_name + ",")
	# 		prosp_file.write(",".join(list(p_stats.values())))
	# 		prosp_file.write("\n")
	# prosp_file.close()

