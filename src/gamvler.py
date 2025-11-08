import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import random
from dataclasses import dataclass
from typing import List, Optional
import json


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
        self.root.title("F1 Race Prediction Game")
        self.root.geometry("950x750")

        self.players = []
        self.all_drivers = [
            "Max Verstappen", "Liam Lawson", "Lewis Hamilton", "George Russell",
            "Charles Leclerc", "Carlos Sainz", "Lando Norris", "Oscar Piastri",
            "Fernando Alonso", "Lance Stroll", "Esteban Ocon", "Pierre Gasly",
            "Alexander Albon", "Gabriel Bortoleto", "Isack Hadjar", "Oliver Bearman",
            "Kimi Antonelli", "Nico Hulkenberg", "Yuki Tsunoda", "Franco Colapinto"
        ]
        self.teams = [
            "Red Bull Racing", "Mercedes", "Ferrari", "McLaren",
            "Aston Martin", "Alpine", "Williams", "Kick Sauber",
            "Haas", "Racing Bulls"
        ]

        self.phase = "betting"  # "betting" or "results"
        self.results_data = None
        self.category_winners = {}  # Track winners for each category

        # Color scheme
        self.bg_color = "#1a1a2e"
        self.fg_color = "#eee"
        self.accent_color = "#e94560"
        self.button_color = "#16213e"
        self.success_color = "#4CAF50"

        self.root.configure(bg=self.bg_color)

        self.create_widgets()

    def create_widgets(self):
        # Title
        self.title_label = tk.Label(self.root, text=" F1 PREDICTION GAME - PLACE BETS", 
                        font=("Arial", 22, "bold"),
                        bg=self.bg_color, fg=self.accent_color)
        self.title_label.pack(pady=20)

        # Phase indicator
        self.phase_label = tk.Label(self.root, text=" PHASE 1: Placing Bets", 
                                   font=("Arial", 12, "bold"),
                                   bg=self.bg_color, fg=self.success_color)
        self.phase_label.pack(pady=5)

        # Main container with two columns
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Left side - Player Entry
        self.left_frame = tk.LabelFrame(main_frame, text="Add Player", 
                                   font=("Arial", 12, "bold"),
                                   bg=self.bg_color, fg=self.accent_color,
                                   relief=tk.RIDGE, borderwidth=2)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Player name
        tk.Label(self.left_frame, text="Player Name:", bg=self.bg_color, 
                fg=self.fg_color, font=("Arial", 10)).pack(pady=(10, 5))
        self.name_entry = tk.Entry(self.left_frame, font=("Arial", 11), width=25)
        self.name_entry.pack(pady=5)

        # DNF Prediction
        tk.Label(self.left_frame, text="DNF Prediction (0-20):", bg=self.bg_color,
                fg=self.fg_color, font=("Arial", 10)).pack(pady=(10, 5))
        self.dnf_spin = tk.Spinbox(self.left_frame, from_=0, to=20, 
                                   font=("Arial", 11), width=23)
        self.dnf_spin.pack(pady=5)

        # Team Prediction
        tk.Label(self.left_frame, text="Team with Most Points:", bg=self.bg_color,
                fg=self.fg_color, font=("Arial", 10)).pack(pady=(10, 5))
        self.team_combo = ttk.Combobox(self.left_frame, font=("Arial", 11), 
                                       width=23, state="readonly",
                                       values=self.teams)
        self.team_combo.pack(pady=5)

        # Assigned Drivers (auto-assigned)
        tk.Label(self.left_frame, text="Assigned Drivers (auto):", bg=self.bg_color,
                fg=self.fg_color, font=("Arial", 10)).pack(pady=(10, 5))
        self.drivers_label = tk.Label(self.left_frame, text="Will be assigned randomly",
                                     bg=self.bg_color, fg="#888", 
                                     font=("Arial", 9, "italic"),
                                     wraplength=250)
        self.drivers_label.pack(pady=5)

        # Add Player Button
        self.add_btn = tk.Button(self.left_frame, text="+ Add Player", command=self.add_player,
                 bg=self.accent_color, fg="white", font=("Arial", 11, "bold"),
                 relief=tk.FLAT, padx=20, pady=8)
        self.add_btn.pack(pady=20)

        # Right side - Players List
        right_frame = tk.LabelFrame(main_frame, text="Players", 
                                    font=("Arial", 12, "bold"),
                                    bg=self.bg_color, fg=self.accent_color,
                                    relief=tk.RIDGE, borderwidth=2)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollable players list
        canvas = tk.Canvas(right_frame, bg=self.bg_color, 
                          highlightthickness=0)
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", 
                                command=canvas.yview)
        self.players_frame = tk.Frame(canvas, bg=self.bg_color)

        self.players_frame.bind("<Configure>", 
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.players_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Bottom buttons
        self.button_frame = tk.Frame(self.root, bg=self.bg_color)
        self.button_frame.pack(pady=20)

        self.randomize_btn = tk.Button(self.button_frame, text="Randomize All Drivers", 
                 command=self.randomize_all_drivers,
                 bg=self.button_color, fg=self.fg_color,
                 font=("Arial", 10, "bold"), relief=tk.FLAT,
                 padx=15, pady=8)
        self.randomize_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(self.button_frame, text="Clear All", 
                 command=self.clear_all,
                 bg=self.button_color, fg=self.fg_color,
                 font=("Arial", 10, "bold"), relief=tk.FLAT,
                 padx=15, pady=8)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.lock_btn = tk.Button(self.button_frame, text="Lock Bets & Upload Results", 
                 command=self.lock_bets,
                 bg=self.success_color, fg="white",
                 font=("Arial", 11, "bold"), relief=tk.FLAT,
                 padx=20, pady=10)
        self.lock_btn.pack(side=tk.LEFT, padx=5)

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

        # Check if enough drivers available
        used_drivers = [d for p in self.players for d in p.assigned_drivers]
        available = [d for d in self.all_drivers if d not in used_drivers]

        if len(available) < 2:
            messagebox.showwarning("Not Enough Drivers", 
                "Not enough unique drivers available for assignment!")
            return

        # Randomly assign 2 drivers
        assigned = random.sample(available, 2)

        player = Player(name, dnf, team, assigned)
        self.players.append(player)

        self.update_players_display()

        # Clear inputs
        self.name_entry.delete(0, tk.END)
        self.dnf_spin.delete(0, tk.END)
        self.dnf_spin.insert(0, "0")
        self.team_combo.set('')

    def update_players_display(self):
        # Clear existing widgets
        for widget in self.players_frame.winfo_children():
            widget.destroy()

        # Display each player
        for i, player in enumerate(self.players):
            player_card = tk.Frame(self.players_frame, bg="#2d2d44", 
                                  relief=tk.RAISED, borderwidth=1)
            player_card.pack(fill=tk.X, padx=5, pady=5)

            # Player header
            header = tk.Frame(player_card, bg="#2d2d44")
            header.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(header, text=f"#{i+1} {player.name}", 
                    font=("Arial", 11, "bold"), bg="#2d2d44", 
                    fg=self.accent_color).pack(side=tk.LEFT)

            if self.phase == "betting":
                tk.Button(header, text="❌", command=lambda idx=i: self.remove_player(idx),
                         bg="#ff4444", fg="white", font=("Arial", 8, "bold"),
                         relief=tk.FLAT, padx=5, pady=2).pack(side=tk.RIGHT)

            # Player details
            details = tk.Frame(player_card, bg="#2d2d44")
            details.pack(fill=tk.X, padx=10, pady=(0, 5))

            tk.Label(details, text=f"DNFs: {player.dnf_prediction} | Team: {player.team_prediction}",
                    font=("Arial", 9), bg="#2d2d44", fg=self.fg_color).pack(anchor=tk.W)

            tk.Label(details, text=f"Drivers: {', '.join(player.assigned_drivers)}",
                    font=("Arial", 9, "italic"), bg="#2d2d44", 
                    fg="#aaa").pack(anchor=tk.W)

            # Show scores if in results phase
            if self.phase == "results" and player.categories_won is not None:
                scores = tk.Frame(player_card, bg="#2d2d44")
                scores.pack(fill=tk.X, padx=10, pady=(5, 5))

                score_text = f"DNF Score: {player.dnf_score} | Team Score: {player.team_score} | Places Gained: {player.places_gained_score}"
                tk.Label(scores, text=score_text,
                        font=("Arial", 9), bg="#2d2d44", 
                        fg=self.fg_color).pack(anchor=tk.W)

                # Display categories won
                categories_text = f"🏆 Categories Won: {player.categories_won}"
                tk.Label(scores, text=categories_text,
                        font=("Arial", 10, "bold"), bg="#2d2d44", 
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
            messagebox.showwarning("Not Enough Drivers",
                "Not enough drivers for all players!")
            return

        # Shuffle all drivers
        shuffled = self.all_drivers.copy()
        random.shuffle(shuffled)

        # Assign 2 to each player
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

    def lock_bets(self):
        if not self.players:
            messagebox.showwarning("No Players", "Add some players first!")
            return

        if messagebox.askyesno("Lock Bets", 
            "Lock all bets and proceed to upload results?\nYou won't be able to add/edit players after this!"):
            self.phase = "results"
            self.update_ui_for_results_phase()

    def update_ui_for_results_phase(self):
        # Update title and phase indicator
        self.title_label.config(text=" F1 PREDICTION GAME - UPLOAD RESULTS")
        self.phase_label.config(text="PHASE 2: Upload Race Results", fg="#FFA500")

        # Disable betting controls
        self.add_btn.config(state=tk.DISABLED)
        self.name_entry.config(state=tk.DISABLED)
        self.dnf_spin.config(state=tk.DISABLED)
        self.team_combo.config(state=tk.DISABLED)
        self.randomize_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.lock_btn.config(state=tk.DISABLED)

        # Add CSV upload button
        self.upload_btn = tk.Button(self.button_frame, text="Upload Results CSV", 
                 command=self.upload_results,
                 bg=self.accent_color, fg="white",
                 font=("Arial", 11, "bold"), relief=tk.FLAT,
                 padx=20, pady=10)
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        self.update_players_display()

    def upload_results(self):
        filename = filedialog.askopenfilename(
            title="Select Results CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                if not rows:
                    messagebox.showerror("Error", "CSV file is empty!")
                    return

                # Parse results
                self.results_data = {}
                actual_dnf_count = 0
                team_points = {}

                for row in rows:
                    # Get driver name
                    driver = (row.get('Driver') or row.get('driver') or 
                             row.get('Name') or row.get('name', '')).strip()

                    # Get team
                    team = (row.get('Team') or row.get('team') or 
                           row.get('Constructor') or row.get('constructor', '')).strip()

                    # Get positions
                    start_pos = row.get('StartPosition') or row.get('start_position') or row.get('Grid')
                    finish_pos = row.get('FinishPosition') or row.get('finish_position') or row.get('Position')

                    # Get points
                    points = row.get('Points') or row.get('points') or '0'

                    # Check DNF
                    status = (row.get('Status') or row.get('status') or '').lower()
                    is_dnf = 'dnf' in status or 'retired' in status or finish_pos in ['DNF', 'DNS', 'DSQ', '']

                    if is_dnf:
                        actual_dnf_count += 1

                    # Calculate places gained
                    places_gained = 0
                    if start_pos and finish_pos and not is_dnf:
                        try:
                            places_gained = int(start_pos) - int(finish_pos)
                        except:
                            pass

                    # Track team points
                    if team:
                        team_points[team] = team_points.get(team, 0) + float(points or 0)

                    self.results_data[driver] = {
                        'team': team,
                        'places_gained': places_gained,
                        'is_dnf': is_dnf,
                        'points': float(points or 0)
                    }

                # Find team with most points
                winning_team = max(team_points.items(), key=lambda x: x[1])[0] if team_points else None

                # Calculate scores for each player
                for player in self.players:
                    # DNF score (1 point for exact match, 0 otherwise)
                    player.dnf_score = 1 if player.dnf_prediction == actual_dnf_count else 0

                    # Team score (1 point if correct)
                    player.team_score = 1 if player.team_prediction == winning_team else 0

                    # Places gained score (can be negative)
                    total_places_gained = 0
                    for driver in player.assigned_drivers:
                        if driver in self.results_data:
                            total_places_gained += self.results_data[driver]['places_gained']
                    player.places_gained_score = total_places_gained

                # Determine category winners
                self.category_winners = {
                    'DNF': [],
                    'Team': [],
                    'Places Gained': []
                }

                # DNF category - exact match first, then closest if no exact match
                exact_dnf_players = [p for p in self.players if p.dnf_score == 1]

                if exact_dnf_players:
                    # Award to all who got exact match
                    for player in exact_dnf_players:
                        self.category_winners['DNF'].append(player.name)
                else:
                    # No exact match - find closest prediction(s)
                    min_difference = min(abs(p.dnf_prediction - actual_dnf_count) for p in self.players)
                    for player in self.players:
                        if abs(player.dnf_prediction - actual_dnf_count) == min_difference:
                            self.category_winners['DNF'].append(player.name)

                # Team category - all players who got it right
                for player in self.players:
                    if player.team_score == 1:
                        self.category_winners['Team'].append(player.name)

                # Places Gained category - highest score(s)
                if self.players:
                    max_places = max(p.places_gained_score for p in self.players)
                    for player in self.players:
                        if player.places_gained_score == max_places:
                            self.category_winners['Places Gained'].append(player.name)

                # Count categories won for each player
                for player in self.players:
                    count = 0
                    if player.name in self.category_winners['DNF']:
                        count += 1
                    if player.name in self.category_winners['Team']:
                        count += 1
                    if player.name in self.category_winners['Places Gained']:
                        count += 1
                    player.categories_won = count

                # Sort players by categories won
                self.players.sort(key=lambda p: p.categories_won, reverse=True)

                self.update_players_display()

                # Build results message
                result_msg = "🏁 RACE RESULTS CALCULATED!\n\n"
                result_msg += f"Actual DNFs: {actual_dnf_count}\n"
                result_msg += f"Winning Team: {winning_team}\n\n"
                result_msg += "📊 CATEGORY WINNERS:\n\n"

                for category, winners in self.category_winners.items():
                    if winners:
                        if len(winners) == 1:
                            result_msg += f"🏆 {category}: {winners[0]}\n"
                        else:
                            result_msg += f"🏆 {category}: {', '.join(winners)} (TIE)\n"
                    else:
                        result_msg += f"🏆 {category}: No winner\n"

                result_msg += f"\n🎉 OVERALL WINNER(S):\n"
                top_categories = self.players[0].categories_won
                overall_winners = [p.name for p in self.players if p.categories_won == top_categories]

                if len(overall_winners) == 1:
                    result_msg += f"{overall_winners[0]} with {top_categories} categor{'y' if top_categories == 1 else 'ies'} won!"
                else:
                    result_msg += f"{', '.join(overall_winners)} (TIE) with {top_categories} categor{'y' if top_categories == 1 else 'ies'} won each!"

                messagebox.showinfo("Results Calculated!", result_msg)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process results: {str(e)}")

    def save_game(self):
        if not self.players:
            messagebox.showinfo("No Data", "No players to save!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            data = {
                "phase": self.phase,
                "players": [
                    {
                        "name": p.name,
                        "dnf_prediction": p.dnf_prediction,
                        "team_prediction": p.team_prediction,
                        "assigned_drivers": p.assigned_drivers,
                        "dnf_score": p.dnf_score,
                        "team_score": p.team_score,
                        "places_gained_score": p.places_gained_score,
                        "categories_won": p.categories_won
                    }
                    for p in self.players
                ]
            }

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            messagebox.showinfo("Success", f"Game saved to {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = F1PredictionGame(root)
    root.mainloop()
    # print end    
