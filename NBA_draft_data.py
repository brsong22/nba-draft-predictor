from lxml import etree as et
from lxml import html
from urllib.request import urlopen
import configparser

Config = configparser.ConfigParser()
Config.read("bball.ini")
bball_ref_url = Config.get("Stats", "Url")
draft_preview_url = bball_ref_url + Config.get("Stats", "DraftPath")
num_rd1_picks = 31
teams = {}

parser = et.HTMLParser()
with urlopen(draft_preview_url) as f:
	tree = et.parse(f, parser)

#bball-ref draft preview source code has the entire html blocked as a comment
#need to get the comment block and then reparse as html
c = html.tostring(tree.xpath('//*[@id="all_picks"]/comment()')[0], method="text")
c_tree = et.HTML(c, parser)
print("getting first round team order")
for i in range(1,num_rd1_picks):
	pick_num = c_tree.xpath('//*[@id="picks"]/tbody[1]/tr['+str(i)+']/td[1]/a/text()')[0]
	team = c_tree.xpath('//*[@id="picks"]/tbody[1]/tr['+str(i)+']/td[2]/a/text()')[0]
	team_link = c_tree.xpath('//*[@id="picks"]/tbody[1]/tr['+str(i)+']/td[2]/a/@href')[0]
	teams[str(pick_num)] = {'team_name':team,'team_link':team_link}

team_ranks_url = Config.get("Stats", "TeamStatRanks")
team_ranks = {}
#3pa:18, 3p%:19, 2pa:21, 2p%:22, fta:24, ft%:25, orb:26, drb:27, ast:29, stl:30, blk:31, pts:34
#//*[@id="stats"]/thead/tr/th[18]
print("getting team season rankings")
for k, d in teams.items():
	team_info = d['team_link'].split('/')
	real_abbr = team_info[2]
	team_abbr = 'NJN' if team_info[2] == 'BRK' else team_info[2]
	team_path = "/" + team_info[1] + "/" + team_abbr
	team_link = bball_ref_url + team_path + team_ranks_url
	team_key = d['team_name'] + " (" + real_abbr + ")"
	if not team_key in team_ranks:
		print("obtaining " + real_abbr + "'s rankings")
		with urlopen(team_link) as r:
			r_tree = et.parse(r, parser)

		#use //text() because bball-ref nests a <span> for rank 1s so we need to just get the deepest child's text
		r_3pa = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[17]//text()')[0]
		r_3pp = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[18]//text()')[0]
		r_2pa = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[20]//text()')[0]
		r_2pp = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[21]//text()')[0]
		r_fta = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[23]//text()')[0]
		r_ftp = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[24]//text()')[0]
		r_orb = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[25]//text()')[0]
		r_drb = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[26]//text()')[0]
		r_ast = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[28]//text()')[0]
		r_stl = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[29]//text()')[0]
		r_blk = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[30]//text()')[0]
		r_pts = r_tree.xpath('//*[@id="stats"]/tbody/tr[1]/td[33]//text()')[0]

		team_ranks[team_key] = {'3pa':r_3pa,
								'3pp':r_3pp,
								'2pa':r_2pa,
								'2pp':r_2pp,
								'fta':r_fta,
								'ftp':r_ftp,
								'orb':r_orb,
								'drb':r_drb,
								'ast':r_ast,
								'stl':r_stl,
								'blk':r_blk,
								'pts':r_pts}

with open('2017-18 Draft Team Ranks.csv', 'w+') as team_file:
	for k, d in team_ranks.items():
		team_file.write(k + ",")
		team_file.write(",".join(list(d.values())))
		team_file.write("\n")
team_file.close()

#prospect pre-nba stats
num_prospects = 50
prospects = {}
p = html.tostring(tree.xpath('//*[@id="all_prospects"]/comment()')[0], method="text")
p_tree = et.HTML(p, parser)

#get prospects and stats link
for p in range(1,num_prospects):
	prosp_name = p_tree.xpath('//*[@id="prospects"]/tbody/tr[' + str(p) + ']/td[1]//text()')[0]
	prosp_link = p_tree.xpath('//*[@id="prospects"]/tbody/tr[' + str(p) + ']/td[1]//@href')
	prosp_link = prosp_link[0] if len(prosp_link) > 0 else ""
	if not prosp_link == "":
		print("obtaining " + prosp_name + "'s stats")
		link = prosp_link.split("/")
		if link[0] == "":
			euro = True
			prosp_link = bball_ref_url + prosp_link
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

			prospects[prosp_name] = {'3pa':p_3pa,
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
		print(prosp_name + " no stats available")
with open('2017-18 Draft Prospects Stats.csv', 'w+') as prosp_file:
	for k, d in prospects.items():
		prosp_file.write(k + ",")
		prosp_file.write(",".join(list(d.values())))
		prosp_file.write("\n")
prosp_file.close()

