import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import json
from datetime import datetime
import os

# Import live tracker functions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import threading

# 2025 Driver lineup with teams
DRIVER_CODES = {
    'VER': ('Max Verstappen', 'Red Bull Racing'),
    'LAW': ('Liam Lawson', 'Red Bull Racing'),
    'HAM': ('Lewis Hamilton', 'Mercedes'),
    'RUS': ('George Russell', 'Mercedes'),
    'LEC': ('Charles Leclerc', 'Ferrari'),
    'SAI': ('Carlos Sainz', 'Ferrari'),
    'NOR': ('Lando Norris', 'McLaren'),
    'PIA': ('Oscar Piastri', 'McLaren'),
    'ALO': ('Fernando Alonso', 'Aston Martin'),
    'STR': ('Lance Stroll', 'Aston Martin'),
    'OCO': ('Esteban Ocon', 'Alpine'),
    'GAS': ('Pierre Gasly', 'Alpine'),
    'ALB': ('Alexander Albon', 'Williams'),
    'BOR': ('Gabriel Bortoleto', 'Kick Sauber'),
    'HAD': ('Isack Hadjar', 'Racing Bulls'),
    'BEA': ('Oliver Bearman', 'Haas'),
    'ANT': ('Kimi Antonelli', 'Mercedes'),
    'HUL': ('Nico Hulkenberg', 'Haas'),
    'TSU': ('Yuki Tsunoda', 'Racing Bulls'),
    'COL': ('Franco Colapinto', 'Williams')
}

# F1 Points system
POINTS_SYSTEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


@dataclass
class Player:
    name: str
    dnf_prediction: int
    team_prediction: str
    assigned_drivers: List[str]
    dnf_score: Optional[int] = None
    team_score: Optional[int] = None
    places_gained_score: Optional[int] = None
    categories_won: Optional[int] = None


class F1PredictionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Race Prediction Game - Sao Paulo GP 2025")
        self.root.geometry("1900x1080")
        
        self.players = []
        self.all_drivers = [name for name, team in DRIVER_CODES.values()]
        self.teams = [
            "Red Bull Racing", "Mercedes", "Ferrari", "McLaren",
            "Aston Martin", "Alpine", "Williams", "Kick Sauber",
            "Haas", "Racing Bulls"
        ]
        
        self.phase = "betting"
        self.starting_grid = {}
        self.current_positions = {}
        self.dnf_drivers = set()
        self.team_points = {}
        self.winning_team = None
        self.category_winners = {}
        self.refresh_count = 0
        self.actual_dnf_count = 0
        
        # Color scheme
        self.bg_color = "#1a1a2e"
        self.fg_color = "#eee"
        self.accent_color = "#e94560"
        self.button_color = "#16213e"
        self.success_color = "#4CAF50"
        self.gold_color = "#FFD700"
        self.silver_color = "#C0C0C0"
        self.bronze_color = "#CD7F32"
        
        self.root.configure(bg=self.bg_color)
        
        self.create_widgets()
        
    def scrape_live_positions(self, detect_dnf=False) -> Tuple[Dict[str, int], set, Dict[str, int]]:
        """Scrape live positions from f1-dash.com"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get("https://f1-dash.com/dashboard")
            time.sleep(15)
            
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            
            driver_positions = []
            
            for code in DRIVER_CODES.keys():
                index = text_content.find(code)
                if index != -1:
                    driver_positions.append((index, code))
            
            driver_positions.sort(key=lambda x: x[0])
            
            positions = {}
            dnf_set = set()
            team_points = {}
            
            for i, (pos_index, driver_code) in enumerate(driver_positions):
                if len(positions) >= 20:
                    break
                
                driver_name, team_name = DRIVER_CODES[driver_code]
                
                if detect_dnf:
                    if i == len(driver_positions) - 1:
                        next_section = text_content[pos_index:pos_index + 200]
                        if "STOPPED" in next_section:
                            dnf_set.add(driver_name)
                    else:
                        next_pos_index = driver_positions[i + 1][0]
                        section_between = text_content[pos_index:next_pos_index]
                        
                        if "STOPPED" in section_between:
                            dnf_set.add(driver_name)
                
                if driver_name not in dnf_set:
                    race_position = len(positions) + 1
                    positions[driver_name] = race_position
                    
                    if race_position in POINTS_SYSTEM:
                        points = POINTS_SYSTEM[race_position]
                        team_points[team_name] = team_points.get(team_name, 0) + points
            
            return positions, dnf_set, team_points
            
        finally:
            driver.quit()
    
    def create_widgets(self):
        # Title with GP name
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=12)
        
        tk.Label(title_frame, text="SAO PAULO GRAND PRIX 2025", 
                font=("Arial", 28, "bold"),
                bg=self.bg_color, fg=self.accent_color).pack()
        tk.Label(title_frame, text="F1 Race Prediction Game - Live Tracker", 
                font=("Arial", 18),
                bg=self.bg_color, fg=self.fg_color).pack(pady=(3, 0))
        
        # Phase indicator
        self.phase_label = tk.Label(self.root, text="PHASE 1: Placing Bets", 
                                   font=("Arial", 15, "bold"),
                                   bg=self.bg_color, fg=self.success_color)
        self.phase_label.pack(pady=5)
        
        # Refresh status
        self.refresh_label = tk.Label(self.root, text="", 
                                      font=("Arial", 13),
                                      bg=self.bg_color, fg="#FFA500")
        self.refresh_label.pack(pady=2)
        
        # Team standings label
        self.team_label = tk.Label(self.root, text="", 
                                   font=("Arial", 13, "bold"),
                                   bg=self.bg_color, fg=self.gold_color)
        self.team_label.pack(pady=2)
        
        # BUTTONS AT TOP
        self.button_frame = tk.Frame(self.root, bg=self.bg_color)
        self.button_frame.pack(pady=12)
        
        self.randomize_btn = tk.Button(self.button_frame, text="Randomize All Drivers", 
                 command=self.randomize_all_drivers,
                 bg=self.button_color, fg=self.fg_color,
                 font=("Arial", 13, "bold"), relief=tk.FLAT,
                 padx=20, pady=12)
        self.randomize_btn.pack(side=tk.LEFT, padx=8)
        
        self.clear_btn = tk.Button(self.button_frame, text="Clear All", 
                 command=self.clear_all,
                 bg=self.button_color, fg=self.fg_color,
                 font=("Arial", 13, "bold"), relief=tk.FLAT,
                 padx=20, pady=12)
        self.clear_btn.pack(side=tk.LEFT, padx=8)
        
        self.lock_btn = tk.Button(self.button_frame, text="Lock Bets & Start Race", 
                 command=self.lock_bets_and_start_race,
                 bg=self.success_color, fg="white",
                 font=("Arial", 14, "bold"), relief=tk.FLAT,
                 padx=30, pady=14)
        self.lock_btn.pack(side=tk.LEFT, padx=8)
        
        # Category Leaderboard
        self.leaderboard_frame = tk.LabelFrame(self.root, text="LIVE CATEGORY LEADERBOARD", 
                                              font=("Arial", 15, "bold"),
                                              bg=self.bg_color, fg=self.accent_color,
                                              relief=tk.RIDGE, borderwidth=3)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Left side - Player Entry
        self.left_frame = tk.LabelFrame(main_frame, text="Add Player", 
                                   font=("Arial", 16, "bold"),
                                   bg=self.bg_color, fg=self.accent_color,
                                   relief=tk.RIDGE, borderwidth=3)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Player name
        tk.Label(self.left_frame, text="Player Name:", bg=self.bg_color, 
                fg=self.fg_color, font=("Arial", 14)).pack(pady=(15, 8))
        self.name_entry = tk.Entry(self.left_frame, font=("Arial", 14), width=22)
        self.name_entry.pack(pady=8)
        
        # DNF Prediction
        tk.Label(self.left_frame, text="DNF Prediction (0-20):", bg=self.bg_color,
                fg=self.fg_color, font=("Arial", 14)).pack(pady=(15, 8))
        self.dnf_spin = tk.Spinbox(self.left_frame, from_=0, to=20, 
                                   font=("Arial", 14), width=20)
        self.dnf_spin.pack(pady=8)
        
        # Team Prediction
        tk.Label(self.left_frame, text="Team with Most Points:", bg=self.bg_color,
                fg=self.fg_color, font=("Arial", 14)).pack(pady=(15, 8))
        self.team_combo = ttk.Combobox(self.left_frame, font=("Arial", 14), 
                                       width=20, state="readonly",
                                       values=self.teams)
        self.team_combo.pack(pady=8)
        
        # Assigned Drivers
        tk.Label(self.left_frame, text="Assigned Drivers:", bg=self.bg_color,
                fg=self.fg_color, font=("Arial", 14)).pack(pady=(15, 8))
        self.drivers_label = tk.Label(self.left_frame, text="Random Assignment",
                                     bg=self.bg_color, fg="#888", 
                                     font=("Arial", 12, "italic"),
                                     wraplength=240)
        self.drivers_label.pack(pady=8)
        
        # Add Player Button
        self.add_btn = tk.Button(self.left_frame, text="Add Player", command=self.add_player,
                 bg=self.accent_color, fg="white", font=("Arial", 14, "bold"),
                 relief=tk.FLAT, padx=30, pady=12)
        self.add_btn.pack(pady=25)
        
        # Right side - Players Grid
        right_frame = tk.LabelFrame(main_frame, text="Players", 
                                    font=("Arial", 16, "bold"),
                                    bg=self.bg_color, fg=self.accent_color,
                                    relief=tk.RIDGE, borderwidth=3)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollable players grid
        canvas = tk.Canvas(right_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.players_frame = tk.Frame(canvas, bg=self.bg_color)
        
        self.players_frame.bind("<Configure>", 
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.players_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def update_category_leaderboard(self):
        """Update the visual category leaderboard - SHOWS ALL PLAYERS"""
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()
        
        if self.phase not in ["race", "finished"]:
            return
        
        dnf_rankings = sorted(self.players, 
                             key=lambda p: abs(p.dnf_prediction - self.actual_dnf_count))
        
        places_rankings = sorted(self.players, 
                                key=lambda p: p.places_gained_score if p.places_gained_score else 0, 
                                reverse=True)
        
        if self.winning_team and self.team_points:
            def team_closeness(player):
                return self.team_points.get(player.team_prediction, 0)
            
            team_rankings = sorted(self.players, key=team_closeness, reverse=True)
        else:
            team_rankings = self.players.copy()
        
        categories = [
            ("DNF Predictions", dnf_rankings),
            ("Places Gained", places_rankings),
            ("Team Predictions", team_rankings)
        ]
        
        for i, (category_name, rankings) in enumerate(categories):
            row_frame = tk.Frame(self.leaderboard_frame, bg="#2d2d44", 
                                relief=tk.RAISED, borderwidth=2)
            row_frame.pack(fill=tk.X, padx=12, pady=6)
            
            tk.Label(row_frame, text=category_name, 
                    font=("Arial", 13, "bold"),
                    bg="#2d2d44", 
                    fg=self.accent_color, width=18, anchor="w").pack(side=tk.LEFT, padx=8)
            
            # Show ALL players
            for j, player in enumerate(rankings):
                if j == 0:
                    bg_color = self.gold_color
                    fg_color = "#000"
                    position_text = "1st"
                elif j == 1:
                    bg_color = self.silver_color
                    fg_color = "#000"
                    position_text = "2nd"
                elif j == 2:
                    bg_color = self.bronze_color
                    fg_color = "#000"
                    position_text = "3rd"
                else:
                    bg_color = "#3d3d5c"
                    fg_color = self.fg_color
                    position_text = f"{j+1}th"
                
                if category_name.startswith("DNF"):
                    score_text = f"{player.dnf_prediction} (off by {abs(player.dnf_prediction - self.actual_dnf_count)})"
                elif category_name.startswith("Places"):
                    score_text = f"+{player.places_gained_score}" if player.places_gained_score >= 0 else f"{player.places_gained_score}"
                else:
                    if self.team_points:
                        pred_points = self.team_points.get(player.team_prediction, 0)
                        score_text = f"{pred_points}pts"
                    else:
                        score_text = player.team_prediction[:8]
                
                tile = tk.Frame(row_frame, bg=bg_color, relief=tk.RAISED, borderwidth=2)
                tile.pack(side=tk.LEFT, padx=4, pady=4)
                
                tk.Label(tile, text=f"{position_text}: {player.name}", 
                        font=("Arial", 12, "bold"),
                        bg=bg_color, fg=fg_color).pack(padx=10, pady=3)
                tk.Label(tile, text=score_text, 
                        font=("Arial", 12), bg=bg_color, fg=fg_color).pack(padx=10, pady=(0, 3))
    
    def add_player(self):
        if self.phase != "betting":
            messagebox.showwarning("Bets Locked", "Bets are already locked!")
            return
            
        if len(self.players) >= 10:
            messagebox.showwarning("Limit Reached", "Maximum 10 players allowed!")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Invalid Input", "Please enter player name!")
            return
        
        dnf = int(self.dnf_spin.get())
        team = self.team_combo.get()
        
        if not team:
            messagebox.showwarning("Invalid Input", "Please select a team!")
            return
        
        used_drivers = [d for p in self.players for d in p.assigned_drivers]
        available = [d for d in self.all_drivers if d not in used_drivers]
        
        if len(available) < 2:
            messagebox.showwarning("Not Enough Drivers", 
                "Not enough unique drivers available!")
            return
        
        assigned = random.sample(available, 2)
        player = Player(name, dnf, team, assigned)
        self.players.append(player)
        
        self.update_players_display()
        
        self.name_entry.delete(0, tk.END)
        self.dnf_spin.delete(0, tk.END)
        self.dnf_spin.insert(0, "0")
        self.team_combo.set('')
        
    def update_players_display(self):
        """Display players in 3-column grid"""
        for widget in self.players_frame.winfo_children():
            widget.destroy()
        
        # Create grid: 3 columns, up to 4 rows
        for i, player in enumerate(self.players):
            row = i // 3
            col = i % 3
            
            player_card = tk.Frame(self.players_frame, bg="#2d2d44", 
                                  relief=tk.RAISED, borderwidth=2, width=420, height=180)
            player_card.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")
            
            # Make columns expand equally
            self.players_frame.grid_columnconfigure(col, weight=1, minsize=420)
            
            header = tk.Frame(player_card, bg="#2d2d44")
            header.pack(fill=tk.X, padx=15, pady=8)
            
            tk.Label(header, text=f"#{i+1} {player.name}", 
                    font=("Arial", 15, "bold"),
                    bg="#2d2d44", 
                    fg=self.accent_color).pack(side=tk.LEFT)
            
            if self.phase == "betting":
                tk.Button(header, text="X", command=lambda idx=i: self.remove_player(idx),
                         bg="#ff4444", fg="white", font=("Arial", 12, "bold"),
                         relief=tk.FLAT, padx=8, pady=4).pack(side=tk.RIGHT)
            
            details = tk.Frame(player_card, bg="#2d2d44")
            details.pack(fill=tk.X, padx=15, pady=(0, 8))
            
            tk.Label(details, text=f"DNF Prediction: {player.dnf_prediction}",
                    font=("Arial", 13), bg="#2d2d44", fg=self.fg_color).pack(anchor=tk.W, pady=2)
            tk.Label(details, text=f"Team Prediction: {player.team_prediction}",
                    font=("Arial", 13), bg="#2d2d44", fg=self.fg_color, 
                    wraplength=380).pack(anchor=tk.W, pady=2)
            
            driver_text = ""
            for driver in player.assigned_drivers:
                if driver in self.dnf_drivers:
                    driver_text += f"[DNF] {driver}, "
                else:
                    driver_text += f"{driver}, "
            driver_text = driver_text.rstrip(", ")
            
            tk.Label(details, text=f"Drivers: {driver_text}",
                    font=("Arial", 12, "italic"), bg="#2d2d44", fg="#aaa", 
                    wraplength=380).pack(anchor=tk.W, pady=2)
            
            if self.phase in ["race", "finished"] and player.categories_won is not None:
                scores = tk.Frame(player_card, bg="#2d2d44")
                scores.pack(fill=tk.X, padx=15, pady=(3, 8))
                
                tk.Label(scores, text=f"DNF: {player.dnf_score} | Team: {player.team_score}",
                        font=("Arial", 12), bg="#2d2d44", 
                        fg=self.fg_color).pack(anchor=tk.W, pady=1)
                tk.Label(scores, text=f"Places Gained: {player.places_gained_score}",
                        font=("Arial", 12), bg="#2d2d44", 
                        fg=self.fg_color).pack(anchor=tk.W, pady=1)
                
                categories_text = f"Categories Won: {player.categories_won}"
                tk.Label(scores, text=categories_text,
                        font=("Arial", 13, "bold"),
                        bg="#2d2d44", 
                        fg=self.success_color).pack(anchor=tk.W, pady=(3, 0))
    
    def remove_player(self, idx):
        if self.phase != "betting":
            return
        del self.players[idx]
        self.update_players_display()
    
    def randomize_all_drivers(self):
        if self.phase != "betting":
            messagebox.showwarning("Bets Locked", "Bets are already locked!")
            return
            
        if not self.players:
            messagebox.showinfo("No Players", "Add some players first!")
            return
        
        if len(self.all_drivers) < len(self.players) * 2:
            messagebox.showwarning("Not Enough Drivers", "Not enough drivers!")
            return
        
        shuffled = self.all_drivers.copy()
        random.shuffle(shuffled)
        
        for i, player in enumerate(self.players):
            player.assigned_drivers = shuffled[i*2:(i*2)+2]
        
        self.update_players_display()
        messagebox.showinfo("Success", "All drivers randomized!")
    
    def clear_all(self):
        if self.phase != "betting":
            messagebox.showwarning("Bets Locked", "Cannot clear after bets are locked!")
            return
            
        if messagebox.askyesno("Confirm", "Clear all players?"):
            self.players = []
            self.update_players_display()
    
    def lock_bets_and_start_race(self):
        """Lock bets and fetch starting grid"""
        if not self.players:
            messagebox.showwarning("No Players", "Add some players first!")
            return
        
        if not messagebox.askyesno("Lock Bets", 
            "Lock all bets and fetch starting grid?\nThis will take ~15 seconds."):
            return
        
        self.phase_label.config(text="Fetching starting grid from f1-dash.com...")
        self.root.update()
        
        def fetch_grid():
            try:
                self.starting_grid, _, _ = self.scrape_live_positions(detect_dnf=False)
                self.save_backup_csv()
                
                self.phase = "race"
                self.phase_label.config(text="RACE IN PROGRESS - Use Refresh Button", 
                                       fg="#FFA500")
                self.refresh_label.config(text=f"Refreshes: {self.refresh_count} | DNFs: {self.actual_dnf_count}")
                
                self.leaderboard_frame.pack(pady=10, padx=30, fill=tk.X, after=self.button_frame)
                
                self.add_btn.config(state=tk.DISABLED)
                self.name_entry.config(state=tk.DISABLED)
                self.dnf_spin.config(state=tk.DISABLED)
                self.team_combo.config(state=tk.DISABLED)
                self.randomize_btn.config(state=tk.DISABLED)
                self.clear_btn.config(state=tk.DISABLED)
                self.lock_btn.config(state=tk.DISABLED)
                
                # Add new buttons to existing button_frame at top
                self.refresh_race_btn = tk.Button(self.button_frame, text="Refresh Positions", 
                         command=self.refresh_positions,
                         bg="#FFA500", fg="white",
                         font=("Arial", 14, "bold"), relief=tk.FLAT,
                         padx=30, pady=14)
                self.refresh_race_btn.pack(side=tk.LEFT, padx=8)
                
                self.finish_race_btn = tk.Button(self.button_frame, text="Finish Race", 
                         command=self.finish_race,
                         bg=self.accent_color, fg="white",
                         font=("Arial", 14, "bold"), relief=tk.FLAT,
                         padx=30, pady=14)
                self.finish_race_btn.pack(side=tk.LEFT, padx=8)
                
                self.actual_dnf_count = 0
                self.dnf_drivers = set()
                self.team_points = {}
                self.winning_team = None
                for player in self.players:
                    player.places_gained_score = 0
                    player.dnf_score = 0
                    player.team_score = 0
                    player.categories_won = 0
                
                self.update_category_leaderboard()
                
                messagebox.showinfo("Success", 
                    f"Starting grid saved!\n{len(self.starting_grid)} drivers found.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch starting grid: {e}")
                self.phase = "betting"
                self.phase_label.config(text="PHASE 1: Placing Bets")
        
        thread = threading.Thread(target=fetch_grid)
        thread.daemon = True
        thread.start()
    
    def refresh_positions(self):
        """Refresh current positions"""
        self.refresh_label.config(text="Refreshing positions...")
        self.root.update()
        
        def fetch_and_update():
            try:
                self.current_positions, self.dnf_drivers, self.team_points = self.scrape_live_positions(detect_dnf=True)
                self.actual_dnf_count = len(self.dnf_drivers)
                
                if self.team_points:
                    self.winning_team = max(self.team_points.items(), key=lambda x: x[1])[0]
                    winning_points = self.team_points[self.winning_team]
                    self.team_label.config(text=f"Leading Team: {self.winning_team} ({winning_points} pts)")
                
                self.refresh_count += 1
                self.calculate_current_standings()
                self.save_backup_csv()
                
                self.refresh_label.config(text=f"Refreshes: {self.refresh_count} | Last: {datetime.now().strftime('%H:%M:%S')} | DNFs: {self.actual_dnf_count}")
                self.update_players_display()
                self.update_category_leaderboard()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to refresh: {e}")
        
        thread = threading.Thread(target=fetch_and_update)
        thread.daemon = True
        thread.start()
    
    def finish_race(self):
        """Finish race"""
        if not messagebox.askyesno("Finish Race", "Finalize race results?"):
            return
        
        self.refresh_label.config(text="Fetching final positions...")
        self.root.update()
        
        def finalize():
            try:
                self.current_positions, self.dnf_drivers, self.team_points = self.scrape_live_positions(detect_dnf=True)
                self.actual_dnf_count = len(self.dnf_drivers)
                
                if self.team_points:
                    self.winning_team = max(self.team_points.items(), key=lambda x: x[1])[0]
                    winning_points = self.team_points[self.winning_team]
                    self.team_label.config(text=f"Winning Team: {self.winning_team} ({winning_points} pts)")
                
                self.calculate_final_results()
                self.save_backup_csv()
                
                self.phase = "finished"
                self.phase_label.config(text="RACE FINISHED", fg="#4CAF50")
                self.refresh_label.config(text=f"Final results saved | DNFs: {self.actual_dnf_count}")
                
                self.refresh_race_btn.config(state=tk.DISABLED)
                self.finish_race_btn.config(state=tk.DISABLED)
                
                self.update_players_display()
                self.update_category_leaderboard()
                self.show_final_results()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to finalize: {e}")
        
        thread = threading.Thread(target=finalize)
        thread.daemon = True
        thread.start()
    
    def calculate_current_standings(self):
        if not self.starting_grid or not self.current_positions:
            return
        
        for player in self.players:
            total_places_gained = 0
            for driver_name in player.assigned_drivers:
                if driver_name not in self.dnf_drivers:
                    if driver_name in self.starting_grid and driver_name in self.current_positions:
                        start_pos = self.starting_grid[driver_name]
                        current_pos = self.current_positions[driver_name]
                        places_gained = start_pos - current_pos
                        total_places_gained += places_gained
            
            player.places_gained_score = total_places_gained
            
            exact_dnf_players = [p for p in self.players if p.dnf_prediction == self.actual_dnf_count]
            if exact_dnf_players:
                player.dnf_score = 1 if player.dnf_prediction == self.actual_dnf_count else 0
            else:
                min_diff = min(abs(p.dnf_prediction - self.actual_dnf_count) for p in self.players)
                player.dnf_score = 1 if abs(player.dnf_prediction - self.actual_dnf_count) == min_diff else 0
            
            if self.winning_team and self.team_points:
                winning_points = self.team_points[self.winning_team]
                predicted_points = self.team_points.get(player.team_prediction, 0)
                
                all_diffs = [(p, abs(self.team_points.get(p.team_prediction, 0) - winning_points)) for p in self.players]
                min_team_diff = min(diff for _, diff in all_diffs)
                
                player_diff = abs(predicted_points - winning_points)
                player.team_score = 1 if player_diff == min_team_diff else 0
    
    def calculate_final_results(self):
        if not self.current_positions:
            return
        
        for player in self.players:
            exact_dnf_players = [p for p in self.players if p.dnf_prediction == self.actual_dnf_count]
            if exact_dnf_players:
                player.dnf_score = 1 if player.dnf_prediction == self.actual_dnf_count else 0
            else:
                min_diff = min(abs(p.dnf_prediction - self.actual_dnf_count) for p in self.players)
                player.dnf_score = 1 if abs(player.dnf_prediction - self.actual_dnf_count) == min_diff else 0
            
            if self.winning_team and self.team_points:
                winning_points = self.team_points[self.winning_team]
                predicted_points = self.team_points.get(player.team_prediction, 0)
                
                all_diffs = [(p, abs(self.team_points.get(p.team_prediction, 0) - winning_points)) for p in self.players]
                min_team_diff = min(diff for _, diff in all_diffs)
                
                player_diff = abs(predicted_points - winning_points)
                player.team_score = 1 if player_diff == min_team_diff else 0
            
            total_places_gained = 0
            for driver_name in player.assigned_drivers:
                if driver_name not in self.dnf_drivers:
                    if driver_name in self.starting_grid and driver_name in self.current_positions:
                        start_pos = self.starting_grid[driver_name]
                        final_pos = self.current_positions[driver_name]
                        places_gained = start_pos - final_pos
                        total_places_gained += places_gained
            player.places_gained_score = total_places_gained
        
        self.category_winners = {'DNF': [], 'Team': [], 'Places Gained': []}
        
        for player in self.players:
            if player.dnf_score == 1:
                self.category_winners['DNF'].append(player.name)
        
        for player in self.players:
            if player.team_score == 1:
                self.category_winners['Team'].append(player.name)
        
        if self.players:
            max_places = max(p.places_gained_score for p in self.players)
            for player in self.players:
                if player.places_gained_score == max_places:
                    self.category_winners['Places Gained'].append(player.name)
        
        for player in self.players:
            count = 0
            if player.name in self.category_winners['DNF']:
                count += 1
            if player.name in self.category_winners['Team']:
                count += 1
            if player.name in self.category_winners['Places Gained']:
                count += 1
            player.categories_won = count
        
        self.players.sort(key=lambda p: p.categories_won, reverse=True)
    
    def show_final_results(self):
        result_msg = "FINAL RACE RESULTS - SAO PAULO GP 2025\n\n"
        
        if self.team_points:
            result_msg += "TEAM STANDINGS:\n"
            sorted_teams = sorted(self.team_points.items(), key=lambda x: x[1], reverse=True)
            for i, (team, points) in enumerate(sorted_teams[:3], 1):
                medal = ["1st", "2nd", "3rd"][i-1]
                result_msg += f"{medal} - {team}: {points} pts\n"
            result_msg += "\n"
        
        result_msg += f"Total DNFs: {self.actual_dnf_count}\n"
        if self.dnf_drivers:
            result_msg += f"DNF'd Drivers: {', '.join(sorted(self.dnf_drivers))}\n\n"
        else:
            result_msg += "DNF'd Drivers: None\n\n"
        
        result_msg += "CATEGORY WINNERS:\n\n"
        
        for category, winners in self.category_winners.items():
            if winners:
                if len(winners) == 1:
                    result_msg += f"{category}: {winners[0]}\n"
                else:
                    result_msg += f"{category}: {', '.join(winners)} (TIE)\n"
            else:
                result_msg += f"{category}: No winner\n"
        
        result_msg += f"\nOVERALL WINNER(S):\n"
        top_categories = self.players[0].categories_won
        overall_winners = [p.name for p in self.players if p.categories_won == top_categories]
        
        if len(overall_winners) == 1:
            result_msg += f"{overall_winners[0]} with {top_categories} categor{'y' if top_categories == 1 else 'ies'} won!"
        else:
            result_msg += f"{', '.join(overall_winners)} (TIE) with {top_categories} categor{'y' if top_categories == 1 else 'ies'} won each!"
        
        messagebox.showinfo("Final Results", result_msg)
    
    def save_backup_csv(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"f1_game_backup_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            writer.writerow(['Phase', self.phase])
            writer.writerow(['Refresh Count', self.refresh_count])
            writer.writerow(['DNF Count', self.actual_dnf_count])
            writer.writerow(['Winning Team', self.winning_team if self.winning_team else ''])
            writer.writerow(['Timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            
            if self.team_points:
                writer.writerow(['Team Standings'])
                writer.writerow(['Team', 'Points'])
                for team, points in sorted(self.team_points.items(), key=lambda x: x[1], reverse=True):
                    writer.writerow([team, points])
                writer.writerow([])
            
            if self.dnf_drivers:
                writer.writerow(['DNF Drivers'])
                for driver in sorted(self.dnf_drivers):
                    writer.writerow([driver])
                writer.writerow([])
            
            writer.writerow(['Player', 'DNF Pred', 'Team Pred', 'Driver 1', 'Driver 2', 
                           'DNF Score', 'Team Score', 'Places Gained', 'Categories Won'])
            
            for player in self.players:
                writer.writerow([
                    player.name,
                    player.dnf_prediction,
                    player.team_prediction,
                    player.assigned_drivers[0] if len(player.assigned_drivers) > 0 else '',
                    player.assigned_drivers[1] if len(player.assigned_drivers) > 1 else '',
                    player.dnf_score if player.dnf_score is not None else '',
                    player.team_score if player.team_score is not None else '',
                    player.places_gained_score if player.places_gained_score is not None else '',
                    player.categories_won if player.categories_won is not None else ''
                ])
            
            writer.writerow([])
            
            if self.starting_grid:
                writer.writerow(['Starting Grid'])
                writer.writerow(['Driver', 'Position'])
                for driver, pos in sorted(self.starting_grid.items(), key=lambda x: x[1]):
                    writer.writerow([driver, pos])
            
            writer.writerow([])
            
            if self.current_positions:
                writer.writerow(['Current Positions'])
                writer.writerow(['Driver', 'Position'])
                for driver, pos in sorted(self.current_positions.items(), key=lambda x: x[1]):
                    writer.writerow([driver, pos])


if __name__ == "__main__":
    root = tk.Tk()
    app = F1PredictionGame(root)
    root.mainloop()
