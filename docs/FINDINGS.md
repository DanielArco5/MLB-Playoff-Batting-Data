# What 50 years of October offense look like

Findings from `data/processed/campaigns.csv`: every MLB team's whole postseason, 1977–2026, as one batting line. That is 374 campaigns across 49 postseasons (1994 had none), 1,426 games and 108,447 plate appearances.

A few terms used throughout:

- **Campaign**: one team's entire postseason in one year, all rounds added together.
- **OPS**: on-base percentage plus slugging percentage, computed from the summed counting stats.
- **Full run**: a campaign of 8 or more games (161 of the 374). Short runs swing too wildly to rank, as the last section shows.
- **Pooled OPS**: the OPS of a group of campaigns with all their at-bats added together, so long runs count for more than short ones.

## 1. October is hard to hit in

The pooled OPS of all 374 campaigns is **.698**. The median full run is .715. Only 18 of the 161 full runs reached .800, and 8 finished under .600.

| Best full runs | G | OPS | Finish |
|---|---|---|---|
| 2007 Red Sox | 14 | .911 | Won the World Series |
| 1999 Red Sox | 10 | .900 | Lost the ALCS |
| 1989 Athletics | 9 | .893 | Won the World Series |
| 2002 Angels | 16 | .879 | Won the World Series |
| 2004 Astros | 12 | .851 | Lost the NLCS |

| Worst full runs | G | OPS | Finish |
|---|---|---|---|
| 2017 Cubs | 10 | .530 | Lost the NLCS |
| 2012 Yankees | 9 | .557 | Lost the ALCS |
| 2022 Yankees | 9 | .579 | Lost the ALCS |
| 2026 Rays | 14 | .584 | Lost the World Series |
| 2019 Cardinals | 9 | .588 | Lost the NLCS |

All 8 full runs under .600 came in 2012 or later. Nothing before 2012 was that bad over 8 or more games.

## 2. The shape of October offense changed, even where OPS did not

| Era | Campaigns | Pooled OPS | Batting average | Strikeouts per 100 PA | Home runs per 100 PA | Runs per game |
|---|---|---|---|---|---|---|
| 1977–84 | 36 | .689 | .252 | 14.5 | 2.08 | 3.85 |
| 1985–93 | 36 | .699 | .251 | 16.8 | 2.10 | 4.12 |
| 1995–2003 | 72 | .707 | .245 | 19.1 | 2.67 | 4.20 |
| 2004–11 | 64 | .736 | .251 | 19.1 | 2.94 | 4.40 |
| 2012–19 | 80 | .669 | .227 | 23.7 | 2.81 | 3.92 |
| 2020–26 | 86 | .691 | .230 | 24.6 | 3.23 | 4.05 |

- **Strikeouts rose by about 70%.** A postseason hitter struck out in 14.5% of plate appearances in 1977–84 and 24.6% in 2020–26. The single-season low was 13.3% (1982); the high was 27.0% (2022).
- **Batting average fell about 20 points, and home runs made up the difference.** Home runs were 9% of all postseason hits in 1977–84 and 16% in 2020–26.
- **2004–11 was the high point.** It has the best pooled OPS (.736), the most runs per game, and 6 of the 18 full runs at .800 or better.
- **2012–19 was the low point.** The expanded wild-card field arrived at the same time as the strikeout surge, and pooled OPS dropped 67 points from the era before.

The best and worst single Octobers:

| Year | Teams | Pooled OPS |
|---|---|---|
| 2002 | 8 | .788 |
| 2004 | 8 | .786 |
| 1993 | 4 | .777 |
| … | | |
| 2012 | 10 | .639 |
| 2026 | 12 | .630 |
| 1983 | 4 | .614 |

**2026 was the second-weakest hitting postseason of the 49**, behind only 1983. Teams hit .217 as a group.

## 3. Hitting goes with winning, but less than you would think

| Finish | Campaigns | Pooled OPS | Median OPS |
|---|---|---|---|
| Won the World Series | 49 | .739 | .733 |
| Lost the World Series | 49 | .709 | .700 |
| Lost the League Championship Series | 98 | .702 | .697 |
| Lost the Division Series | 132 | .650 | .655 |
| Lost the Wild Card round | 46 | .569 | .537 |

The ladder is real, but read it with care: this is each team's OPS over its *whole* run, and a team advances by winning games, which usually means it hit in them. Teams that went out early are in the low rows partly *because* they did not hit. The table describes who advanced; it does not show that a good offense going in predicts a title.

Within that limit:

- **The champion out-hit the team it beat in the World Series in 35 of 49 years.**
- **The champion had the best OPS of its year's field only 16 times.** It was in the top three 42 times.
- **Seven champions hit below the average of their own postseason**: the 1977 and 1978 Yankees, 1980 Phillies, 1981 Dodgers, 1986 Mets, 1988 Dodgers and 2014 Giants. The 1986 Mets won it all at .609, the lowest of any champion and 133 points below the Red Sox team they beat.
- **Great offenses do lose.** The 1999 Red Sox (.900) and the 2004 Astros (.851) are the second- and fifth-best full runs here, and neither reached the World Series.
- **The latest World Series was a mismatch on paper that held.** The 2026 Brewers hit .742. The Rays reached the Series at .584, the lowest OPS of any pennant winner in the set.

## 4. Which organizations hit in October

Pooled over every postseason game each organization played in the window (organizations with at least 8 campaigns):

| Top | Campaigns | Titles | Pooled OPS |
|---|---|---|---|
| Boston Red Sox | 19 | 4 | .745 |
| Toronto Blue Jays | 11 | 2 | .737 |
| New York Yankees | 31 | 7 | .723 |
| Philadelphia Phillies | 16 | 2 | .719 |
| Los Angeles Angels | 10 | 1 | .715 |

| Bottom | Campaigns | Titles | Pooled OPS |
|---|---|---|---|
| Cincinnati Reds | 8 | 1 | .643 |
| Chicago Cubs | 13 | 1 | .667 |
| Tampa Bay Rays | 10 | 0 | .672 |
| New York Mets | 9 | 1 | .672 |
| Baltimore Orioles | 9 | 1 | .674 |

- **Boston stands apart.** The Red Sox own the two best full runs in the set (2007 and 1999) and four of the best twelve.
- **The Yankees are the volume leader.** 31 campaigns and 275 games, more than any other club, at a pooled .723.
- **Regular presence does not mean October hitting.** Campaigns that were part of a streak of four or more straight postseasons pooled to .707, against .694 for the rest: a small edge. Atlanta (14 straight) and St. Louis both sit in the bottom half of the organization table.

### Cleveland

Cleveland has 16 campaigns in the window and no title. Its pooled OPS is .680, about 20th of the 30 organizations and level with Milwaukee, Miami and San Francisco.

- **Best:** 2007, .799 over 11 games, 19th of the 161 full runs. It lost the ALCS in seven.
- **Worst:** 2018, .418 in a three-game Division Series sweep, 359th of all 374 campaigns.
- **The three pennants were won without much hitting:** .674 in 1995, .707 in 1997 and .663 in 2016.
- Cleveland beat its year's postseason average in 7 of its 16 campaigns.

## 5. Why short runs are not ranked

| Games played | Campaigns | Lowest OPS | Highest OPS | Spread (standard deviation) |
|---|---|---|---|---|
| 1–3 | 86 | .256 | .938 | .144 |
| 4–7 | 127 | .429 | .857 | .091 |
| 8–12 | 86 | .530 | .900 | .075 |
| 13+ | 75 | .584 | .911 | .063 |

Both ends of the full table belong to one-game wild-card teams: the 2017 Rockies (.938, lost anyway) and the 2015 Yankees (.256). A three-game sample says very little, so the project ranks only full runs of 8 or more games against each other, and shows the rest with their game count.

Even among full runs, playing longer barely goes with hitting better (correlation .13 between games and OPS). Across all campaigns, OPS tracks runs per game closely (correlation .85), which is the reason for using it as the single height measure.

## How the numbers were checked

- Lahman's postseason batting file, summed per team, matches the MLB Stats API on every counting stat for **358 of 362** team-seasons from 1977 to 2025. The four that differ (2023 Rangers, Astros and Twins; 2024 Guardians) are incomplete in Lahman and use the API totals instead.
- The finished table matches the API's own games played and OPS for **all 374** campaigns.
- Plate appearances differ by one in 20 campaigns. The API counts something our formula (AB + BB + HBP + SF + SH) leaves out, most likely catcher's interference. OPS is not affected.
- Seven campaigns were also checked by hand against StatMuse; all agree to within .002.
- The 2026 World Series result (Brewers over Rays) was entered by hand in `data/ref/results_manual.csv`.

Run `python src/compare_sources.py` and `python src/validate.py` to repeat the checks.

Data: Lahman Baseball Database (CC BY-SA 3.0) and the public MLB Stats API.
