# F1_Game_Time
An F1 race prediction game where friends compete to be the least wrong 
about DNFs, team results, and driver performance. Built with Python & bad predictions.
## What is it?

A pre-race prediction game where players guess:
- How many DNFs will happen
- Which team scores most points  
- Which drivers will gain positions (you're randomly assigned 2 drivers)

Winner = whoever wins the most categories!

## Installation
``
git clone https://github.com/yourusername/pit-stop-prophets.git
cd pit-stop-prophets
pip install tkinter selenium webdriver-manager beautifulsoup4
python f1_prediction_game_v2.py
``
## How to Play

**Before Race:**
1. Add players and their predictions
2. Randomize driver assignments
3. Lock bets

**After Race:**
1. Get race results CSV
2. Upload it in the app
3. See who won!

**CSV Format:**
``
Driver,Team,StartPosition,FinishPosition,Points,Status
Max Verstappen,Red Bull Racing,1,1,25,Finished
Charles Leclerc,Ferrari,5,15,0,DNF - Engine
``

## Scoring

- **DNF Category**: Exact match or closest guess wins
- **Team Category**: Correct team prediction wins
- **Places Gained**: Your 2 drivers' combined position changes

Most categories won = Champion 🏆

## Tech

Python 3.11+ | tkinter | Selenium | BeautifulSoup4

## Credits

Live timing data from [f1-dash.com](https://f1-dash.com) - amazing F1 live timing dashboard

## Disclaimer

This project is unofficial and not associated with Formula 1, FIA, or any F1 teams/companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trademarks of Formula One Licensing B.V.

## License

MIT License

---

*Built for race day fun with friends 🏁*
