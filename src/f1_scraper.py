
#!/usr/bin/env python3
"""
F1 Live Position Tracker - Substring Search
Finds driver codes even when embedded in larger strings
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

# 2025 Driver lineup
DRIVER_CODES = {
    'VER': 'Max Verstappen',
    'LAW': 'Liam Lawson',
    'HAM': 'Lewis Hamilton',
    'RUS': 'George Russell',
    'LEC': 'Charles Leclerc',
    'SAI': 'Carlos Sainz',
    'NOR': 'Lando Norris',
    'PIA': 'Oscar Piastri',
    'ALO': 'Fernando Alonso',
    'STR': 'Lance Stroll',
    'OCO': 'Esteban Ocon',
    'GAS': 'Pierre Gasly',
    'ALB': 'Alexander Albon',
    'BOR': 'Gabriel Bortoleto',
    'HAD': 'Isack Hadjar',
    'BEA': 'Oliver Bearman',
    'ANT': 'Kimi Antonelli',
    'HUL': 'Nico Hulkenberg',
    'TSU': 'Yuki Tsunoda',
    'COL': 'Franco Colapinto'
}

def scrape_f1_positions():
    """Scrape positions by finding driver codes in order (even in substrings)"""

    print("🏎️  F1 Live Position Tracker")
    print("=" * 70)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    print("\n🌐 Loading f1-dash.com...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://f1-dash.com/dashboard")

        print("⏳ Waiting for data (15 seconds)...")
        time.sleep(15)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text()

        print("📊 Searching for driver codes (substring search)...")

        # Save text for debugging
        with open("text_dump.txt", "w", encoding="utf-8") as f:
            f.write(text_content)
        print("   (Saved to text_dump.txt for inspection)")

        # Find all driver codes by searching through the entire text
        # Create a list of (position_in_text, driver_code) tuples
        driver_positions = []

        for code in DRIVER_CODES.keys():
            # Find the first occurrence of this driver code in the text
            index = text_content.find(code)
            if index != -1:
                driver_positions.append((index, code))
                print(f"   ✓ Found {code} at position {index} in text")

        # Sort by position in text (earlier = higher race position)
        driver_positions.sort(key=lambda x: x[0])

        # Create ordered list
        positions = []
        for race_position, (_, driver_code) in enumerate(driver_positions, start=1):
            positions.append({
                'position': race_position,
                'driver_code': driver_code,
                'driver_name': DRIVER_CODES[driver_code]
            })

            # Stop after 20 drivers
            if len(positions) >= 20:
                break

        print(f"\n✓ Found {len(positions)} drivers in order")
        return positions

    finally:
        driver.quit()


def display_positions(positions):
    """Display positions in a formatted table"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 70)
    print(f"🏁 F1 LIVE RACE POSITIONS")
    print(f"⏰ Updated: {timestamp}")
    print("=" * 70)

    if not positions:
        print("\n❌ No position data found!")
        print("   Check text_dump.txt to see what was scraped")
        print("   Make sure there's an active race/session")
        return

    print(f"\n{'POS':<6} {'CODE':<6} {'DRIVER':<30}")
    print("-" * 70)

    for entry in positions:
        pos = f"P{entry['position']}"
        code = entry['driver_code']
        name = entry['driver_name']

        # Add trophy emoji for podium
        if entry['position'] == 1:
            pos = "🥇 " + pos
        elif entry['position'] == 2:
            pos = "🥈 " + pos
        elif entry['position'] == 3:
            pos = "🥉 " + pos

        print(f"{pos:<8} {code:<6} {name:<30}")

    print("-" * 70)
    print(f"📊 Total drivers found: {len(positions)}")
    print("=" * 70)


def get_positions_dict():
    """Return positions as a dictionary for integration with other apps"""
    positions = scrape_f1_positions()

    # Convert to dict format: {driver_name: position}
    result = {}
    for entry in positions:
        result[entry['driver_name']] = entry['position']

    return result


def get_positions_list():
    """Return positions as a simple list for integration"""
    positions = scrape_f1_positions()
    return positions


def main():
    """Main execution"""
    try:
        positions = scrape_f1_positions()
        display_positions(positions)

        print("\n✅ Done!")
        print("\n💡 To use in your F1 prediction app:")
        print("   from f1_live_tracker import get_positions_dict")
        print("   positions = get_positions_dict()  # Returns {driver: position}")
        return positions

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()