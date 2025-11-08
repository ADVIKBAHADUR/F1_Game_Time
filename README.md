# F1_Game_Time
An F1 race prediction game where friends compete to be the least wrong 
about DNFs, team results, and driver performance. Built with Python & bad predictions.

## What is it?

A pre-race prediction game where players guess:
- How many DNFs will happen
- Which team scores most points  
- Which drivers will gain positions (you're randomly assigned 2 drivers)

Winner = whoever wins the most categories!

## Features

- Simple desktop interface, optimized for 1920x1200
- 3x4 grid layout for player cards; no more cramped single column
- Category leaderboard with all players visible, live
- Real-time refresh from [f1-dash.com](https://f1-dash.com) (auto-scraping, no manual data entry)
- DNF detection with [DNF] tag by driver name
- Classic F1 points system (top 10)
- Auto team point tally and closest-pick scoring (allows ties)
- Easy to use: Add, randomize drivers, lock, refresh, and finish—all buttons always at the top!

## Installation
```bash
git clone https://github.com/ADVIKBAHADUR/F1_Game_Time.git
cd F1_Game_Time
pip install -r requirements.txt
python src/f1_Gambler.py
```

## Requirements

- Python 3.8+
- For GUI: works on Windows, Ubuntu, Mac (must support tkinter GUIs)
- Internet connection (scrapes live F1 data from f1-dash.com)

## How to Play

1. Add each player, their DNF and team predictions.
2. Assign drivers (randomize or choose).
3. Lock bets before race starts.
4. Use the Refresh button during the race for live updates.
5. See category and overall winners when the race ends.

### Example

- All player cards and controls are always visible at the top.
- DNFs, places gained, and team points update in real-time after each refresh.

## Data Credits

Live race data sourced from [f1-dash.com](https://f1-dash.com).

## Disclaimer

This project is unofficial and not associated with Formula 1, FIA, or any F1 teams or companies. F1, FORMULA ONE, FIA FORMULA ONE WORLD CHAMPIONSHIP and related marks are trademarks of Formula One Licensing B.V.

---

*Built for maximum F1 party fun and rivalry!*
