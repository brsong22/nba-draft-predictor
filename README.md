# nba-draft-predictor
attempt to predict draft order of prospects

# Problem:
Can we predict the order nba prospects are drafted based on the team's stats and how the player's college/overseas league stats?

# Hypothesis:
A team will draft a player based on the team's weaknesses and the player's ability to fill weak points in a team's roster 
skillset.

e.g. if Team A lacks 3 point scoring (low attempts/low percentage) and ranks low among other NBA teams in 3 point categories, 
they will target prospects with strong 3 point shooting abilities.

## Stats:
*these are the initial stats gathered and are not guaranteed to all be useful in trying to predict the order players are drafted*

**Per Game** stats averages were gathered for both teams and players

Team per game stats as well as the team's league ranking for the stats were gathered.

Draft order and team stats were gathered for each team on [basketball-reference's](https://www.basketball-reference.com/) 
draft preview for the upcoming draft.

Prospect stats for college, overseas, and amateur (g-league) were collected from [sports-reference](https://www.sports-reference.com/) for each player listed by basketball-reference's draft report.

***Update***: because of the considerations listed at the end, I will also generate player rankings among prospects in order to
determine if there is simply a pattern of drafting the overall best players first due to the real world situation of teams trading.

Stats were gathered for each player drafted in the first round on basketball-reference's pages for past drafts.
###### Basketball stats:
- 3 point attempts
- 3 point percentage
- 2 point attempts
- 2 point percentage
- free throw attempts
- free throw percentage
- offensive rebounds
- defensive rebounds
- assists
- steals
- blocks
- points

###### Additional info:
- pick number (which pick the team had/which pick the player was picked at)
- name (team name/player name)

# Using the Data:
In order to get an idea of what stats may be relevant and what relation they have to each other, 
I will plot the data in various ways to attempt to discover a pattern.

To model the data, I will use previous draft data where we know when players were picked and by what team.

Some initial ideas:
###### Bar graph:
Plotting player stats against team stat may allow us to see how a drafted player's profile stacks up against a team's.
###### Scatterplot linear regression:
Plotting a scatterplot may reveal patterns of correlation between team and player profiles.

# Other considerations:
Something to consider with this methodology is that the draft is not set in stone even when the drafting has completed. 
There are many factors that goes into who a team drafts at what point in the draft that go unconsidered in this project.

For instance:
- teams may trade picks to move positions in the draft.
- teams may draft a player for the sole purpose of trading them.

I also suspect that later in the draft teams will draft players less focused on the player's ability to fill weakpoints
in the team, and more based on potential to develop and overall competencies of the player's skills; which could be considered
more subjective qualities or, at the very least, would require advanced analysis to determine those qualities.

