from lxml import etree as et
from lxml import html
import urllib.request
from datetime import datetime
import configparser

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
prospect_stats = {}

parser = et.HTMLParser()
for year_i, draft_url in enumerate(prev_draft_urls):
	with urllib.request.urlopen(draft_url) as draft_html:
		draft = et.parse(draft_html, parser)
	for pick_num in num_rd1_picks:
		#get team info
		draft_pick_team_abbr = draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[2]/a/text()')[0]
		draft_pick_team_abbr = 'NJN' if draft_pick_team_abbr == 'BRK' else draft_pick_team_abbr
		draft_pick_team_abbr = 'NOH' if draft_pick_team_abbr == 'NOP' else draft_pick_team_abbr
		draft_pick_team_abbr = 'CHA' if draft_pick_team_abbr == 'CHO' else draft_pick_team_abbr #typo on the webpage?
		draft_pick_team_abbr = 'CHA' if draft_pick_team_abbr == 'CHH' else draft_pick_team_abbr #charlotte hornets team re-name
		draft_pick_team_name = draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[2]/a/@title')[0]
		team_link = nba_url + cfg.get("Teams", "TeamPath") + "/" + draft_pick_team_abbr + cfg.get("Teams", "TeamStatRanksPage")
		
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
		draft_board[str(pick_num)] = {'team': draft_pick_team_name,
								 	  '3pa':rank_3pa,
								 	  '3pp':rank_3pp,
								 	  '2pa':rank_2pa,
								 	  '2pp':rank_2pp,
								 	  'fta':rank_fta,
								 	  'ftp':rank_ftp,
								 	  'orb':rank_orb,
								 	  'drb':rank_drb,
								 	  'ast':rank_ast,
								 	  'stl':rank_stl,
								 	  'blk':rank_blk,
								 	  'pts':rank_pts}
		#get player info
		draft_pick_player_name = draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[3]/a/text()')[0]
		pick_player_ref_link = nba_url + draft.xpath('//*[@id="stats"]/tbody/tr[' + str(pick_num) + ']/td[3]/a/@href')[0]
		with urllib.request.urlopen(pick_player_ref_link) as player_html:
			player_page = et.parse(player_html, parser)
		player_link_ele = player_page.xpath('//*[@id="inner_nav"]/ul/li[2]/div/ul[8]/li/a/@href')
		if len(player_link_ele) > 0:
			player_am_link = player_link_ele[0]
			if "euro" in player_am_link.split("/"):
				euro = True
			else:
				if "gleague" in player_am_link.split("/"):
					minor_team = cfg.get("Teams", "Minor_Team")
					gleague = True
				else:
					minor_team = cfg.get("Teams", "Cbb_Team")
					gleague = False
				euro = False
		else:
			player_am_link = ""
		if not player_am_link == "":
			with urllib.request.urlopen(player_am_link) as player_stats_html:
				player_stats = et.parse(player_stats_html, parser)
			if euro:
				euro_stat_columns = [7, 8, 10, 11, 13, 14, 15, 16, 18, 19, 20, 23]
				base_num_stat_cols = 24
				club = player_stats.xpath('//*[@id="' + cfg.get("Teams", "Club_Club") + '"]/thead/tr/th')
				euro = player_stats.xpath('//*[@id="' + cfg.get("Teams", "Club_Euro") + '"]/thead/tr/th')
				euroclub = player_stats.xpath('//*[@id="' + cfg.get("Teams", "Club_All") + '"]/thead/tr/th')
				if len(club) > 0:
					tbl_id = cfg.get("Teams", "Club_Club")
					euro_extra_cols = len(club) - base_num_stat_cols
				elif len(euro) > 0:
					tbl_id = cfg.get("Teams", "Club_Euro")
					euro_extra_cols = len(euro) - base_num_stat_cols
				elif len(euroclub) > 0:
					tbl_id = cfg.get("Teams", "Club_All")
					euro_extra_cols = len(euroclub) - base_num_stat_cols
				p_3pa = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[0] + euro_extra_cols) + ']/text()')[0]
				if(float(p_3pa) > 0):
					p_3pp = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[1] + euro_extra_cols) + ']/text()')[0]
				else:
					p_3pp = 'n/a'
				p_2pa = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[2] + euro_extra_cols) + ']/text()')[0]
				p_2pp = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[3] + euro_extra_cols) + ']/text()')[0]
				p_fta = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[4] + euro_extra_cols) + ']/text()')[0]
				p_ftp = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[5] + euro_extra_cols) + ']/text()')[0]
				p_orb = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[6] + euro_extra_cols) + ']/text()')[0]
				p_drb = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[7] + euro_extra_cols) + ']/text()')[0]
				p_ast = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[8] + euro_extra_cols) + ']/text()')[0]
				p_stl = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[9] + euro_extra_cols) + ']/text()')[0]
				p_blk = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[10] + euro_extra_cols) + ']/text()')[0]
				p_pts = player_stats.xpath('//*[@id="' + tbl_id + '"]/tfoot/tr/td[' + str(euro_stat_columns[11] + euro_extra_cols) + ']/text()')[0]
			else:
				cbb_stat_cols = [13, 14, 10, 11, 16, 17, 18, 19, 21, 22, 23, 26]
				if gleague:
					cbb_stat_cols = [x-1 for x in cbb_stat_cols]
				player_3pa = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[0])+ ']//text()')[0]
				if(float(player_3pa) > 0):
					player_3pp = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[1])+ ']//text()')[0]
				else:
					player_3pp = 'n/a'
				player_2pa = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[2])+ ']//text()')[0]
				player_2pp = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[3])+ ']//text()')[0]
				player_fta = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[4])+ ']//text()')[0]
				player_ftp = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[5])+ ']//text()')[0]
				player_orb = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[6])+ ']//text()')[0]
				player_drb = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[7])+ ']//text()')[0]
				player_ast = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[8])+ ']//text()')[0]
				player_stl = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[9])+ ']//text()')[0]
				player_blk = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[10]) + ']//text()')[0]
				player_pts = player_stats.xpath('//*[@id="' + minor_team + '"]/tfoot/tr/td[' + str(cbb_stat_cols[11]) + ']//text()')[0]
		else:
			player_3pa = 'n/a'
			player_3pp = 'n/a'
			player_2pa = 'n/a'
			player_2pp = 'n/a'
			player_fta = 'n/a'
			player_ftp = 'n/a'
			player_orb = 'n/a'
			player_drb = 'n/a'
			player_ast = 'n/a'
			player_stl = 'n/a'
			player_blk = 'n/a'
			player_pts = 'n/a'
		prospect_stats[str(pick_num)] = {'name': draft_pick_player_name,
									'3pa': player_3pa,
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
		print("[[" + str(prev_year - year_i) + "]] with pick [#" + str(pick_num) + "], the [" + draft_pick_team_name + "] select [" + draft_pick_player_name + "]")
	with open('[' + str(prev_year - year_i) + '] Team Draft Order and Stats.csv', 'a') as team_file:
		team_file.write(cfg.get("Base", "Stats") + "\n")
		for num, t_stats in draft_board.items():
			team_file.write(num + ",")
			team_file.write(",".join(list(t_stats.values())))
			team_file.write("\n")
	team_file.close()
	with open('[' + str(prev_year - year_i) + '] Drafted Player Stats.csv', 'w+') as prosp_file:
		prosp_file.write(cfg.get("Base", "Stats") + "\n")
		for num, p_stats in prospect_stats.items():
			prosp_file.write(num + ",")
			prosp_file.write(",".join(list(p_stats.values())))
			prosp_file.write("\n")
	prosp_file.close()

