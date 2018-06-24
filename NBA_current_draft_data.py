from lxml import etree as et
from lxml import html
from urllib.request import urlopen
from datetime import datetime
import configparser

cfg = configparser.ConfigParser()
cfg.read("draft_predict.ini")
nba_url = cfg.get("Base", "Url")
# cbb_url = cfg.get("Base", "CbbUrl")
curr_draft_url = nba_url + cfg.get("Draft", "DraftPath") + cfg.get("Draft", "CurrentDraftPage")

curr_year = datetime.today().year
#only get the first 30 picks (round 1) of the draft 1-indexed
num_rd1_picks = list(range(1, 31))
#get top 49 prospects
num_prospects = list(range(1, 50))

team_draft_order = {}
prospects = {}

parser = et.HTMLParser()
with urlopen(curr_draft_url) as f:
	tree = et.parse(f, parser)

#current draft source code has the entire html blocked as a comment
#need to get the comment block and then reparse as html
draft_board = html.tostring(tree.xpath('//*[@id="all_picks"]/comment()')[0], method="text")
draft_order = et.HTML(draft_board, parser)

for pick_num in num_rd1_picks:
	pick_num = draft_order.xpath('//*[@id="picks"]/tbody[1]/tr[' + str(pick_num) + ']/td[1]/a/text()')[0]
	team = draft_order.xpath('//*[@id="picks"]/tbody[1]/tr[' + str(pick_num) + ']/td[2]/a/text()')[0]
	team_link = draft_order.xpath('//*[@id="picks"]/tbody[1]/tr[' + str(pick_num) + ']/td[2]/a/@href')[0]
	team_draft_order[str(pick_num)] = {'team_name':team, 'team_link':team_link}

team_ranks_url = cfg.get("Teams", "TeamStatRanksPage")
team_stat_ranks = {}
#3pa:18, 3p%:19, 2pa:21, 2p%:22, fta:24, ft%:25, orb:26, drb:27, ast:29, stl:30, blk:31, pts:34
# print("getting team season rankings")
for t_key, t_values in team_draft_order.items():
	team_info = t_values['team_link'].split('/')
	real_abbr = team_info[2]
	#nets and pelicans had recent name changes not reflected in URL
	team_abbr = 'NJN' if team_info[2] == 'BRK' else team_info[2]
	team_abbr = 'NOH' if team_info[2] == 'NOP' else team_abbr
	team_path = "/" + team_info[1] + "/" + team_abbr
	team_link = nba_url + team_path + team_ranks_url
	team_key = t_values['team_name']
	if not team_key in team_stat_ranks:
		# print("obtaining " + real_abbr + "'s rankings")
		print(team_link)
		with urlopen(team_link) as r:
			stat_rank_tree = et.parse(r, parser)
		#use //text() because bball-ref nests a <span> for rank 1s so we need to just get the deepest child's text
		rank_3pa = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[17]//text()')[0]
		rank_3pp = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[18]//text()')[0]
		rank_2pa = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[20]//text()')[0]
		rank_2pp = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[21]//text()')[0]
		rank_fta = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[23]//text()')[0]
		rank_ftp = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[24]//text()')[0]
		rank_orb = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[25]//text()')[0]
		rank_drb = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[26]//text()')[0]
		rank_ast = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[28]//text()')[0]
		rank_stl = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[29]//text()')[0]
		rank_blk = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[30]//text()')[0]
		rank_pts = stat_rank_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[33]//text()')[0]

		team_stat_ranks[team_key] = {'3pa':rank_3pa,
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

save_name = str(curr_year) + '_Draft Team Stats Ranks.csv'
with open(save_name, 'w+') as team_file:
	for pick, t_info in team_draft_order.items():
		team_file.write(pick + "," + t_info['team_name'])
		team_file.write(",".join(list(team_stat_ranks[t_info['team_name']].values())))
		team_file.write("\n")
team_file.close()

# #end draft team ranks loop

#prospect pre-nba stats
prospects_list = {}
prospects = html.tostring(tree.xpath('//*[@id="all_prospects"]/comment()')[0], method="text")
prospects_tree = et.HTML(prospects, parser)

#get prospects and stats link
for p in num_prospects:
	prosp_name = prospects_tree.xpath('//*[@id="prospects"]/tbody/tr[' + str(p) + ']/td[1]//text()')[0]
	prosp_link = prospects_tree.xpath('//*[@id="prospects"]/tbody/tr[' + str(p) + ']/td[1]//@href')
	prosp_link = prosp_link[0] if len(prosp_link) > 0 else ""
	if not prosp_link == "":
		# print("obtaining " + prosp_name + "'s stats")
		link_parts = prosp_link.split("/")
		if link_parts[0] == "":
			euro = True
			prosp_link = nba_url + prosp_link
		else:
			euro = False
		with urlopen(prosp_link) as l:
			prosp_tree = et.parse(l, parser)
			if not euro:
				p_3pa = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[13]/text()')[0]
				p_3pp = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[14]/text()')[0]
				p_2pa = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[10]/text()')[0]
				p_2pp = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[11]/text()')[0]
				p_fta = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[16]/text()')[0]
				p_ftp = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[17]/text()')[0]
				p_orb = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[18]/text()')[0]
				p_drb = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[19]/text()')[0]
				p_ast = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[21]/text()')[0]
				p_stl = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[22]/text()')[0]
				p_blk = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[23]/text()')[0]
				p_pts = prosp_tree.xpath('//*[@id="players_per_game"]/tfoot/tr/td[26]/text()')[0]
			else:
				#some euro players have a 'clubs' column. check for existence of element
				if prosp_tree.xpath('//*[@id="per_gameEUR0"]/thead/tr/th[2]/text()'):
					p_3pa = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[10]/text()')[0]
					p_3pp = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[11]/text()')[0]
					p_2pa = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[13]/text()')[0]
					p_2pp = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[14]/text()')[0]
					p_fta = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[16]/text()')[0]
					p_ftp = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[17]/text()')[0]
					p_orb = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[18]/text()')[0]
					p_drb = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[19]/text()')[0]
					p_ast = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[21]/text()')[0]
					p_stl = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[22]/text()')[0]
					p_blk = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[23]/text()')[0]
					p_pts = prosp_tree.xpath('//*[@id="per_gameEUR0"]/tfoot/tr/td[26]/text()')[0]
				else:
					p_3pa = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[9]/text()')[0]
					p_3pp = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[10]/text()')[0]
					p_2pa = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[12]/text()')[0]
					p_2pp = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[13]/text()')[0]
					p_fta = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[15]/text()')[0]
					p_ftp = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[16]/text()')[0]
					p_orb = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[17]/text()')[0]
					p_drb = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[18]/text()')[0]
					p_ast = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[20]/text()')[0]
					p_stl = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[21]/text()')[0]
					p_blk = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[22]/text()')[0]
					p_pts = prosp_tree.xpath('//*[@id="per_gameALL0"]/tfoot/tr/td[25]/text()')[0]

			prospects_list[prosp_name] = {'3pa':p_3pa,
									 '3pp':p_3pp,
									 '2pa':p_2pa,
									 '2pp':p_2pp,
									 'fta':p_fta,
									 'ftp':p_ftp,
									 'orb':p_orb,
									 'drb':p_drb,
									 'ast':p_ast,
									 'stl':p_stl,
									 'blk':p_blk,
									 'pts':p_pts}
	else:
		prospects_list[prosp_name] = {'3pa':'n/a',
									 '3pp':'n/a',
									 '2pa':'n/a',
									 '2pp':'n/a',
									 'fta':'n/a',
									 'ftp':'n/a',
									 'orb':'n/a',
									 'drb':'n/a',
									 'ast':'n/a',
									 'stl':'n/a',
									 'blk':'n/a',
									 'pts':'n/a'}
with open(str(curr_year) + '_Draft Prospects Stats.csv', 'w+') as prosp_file:
	for p_name, p_stats in prospects_list.items():
		prosp_file.write(p_name + ",")
		prosp_file.write(",".join(list(p_stats.values())))
		prosp_file.write("\n")
prosp_file.close()

