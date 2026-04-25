import customtkinter as ctk
from scanner import GameScanner
from launcher import GameLauncher
from PIL import Image
import requests
from io import BytesIO
import json
import os

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Game Vault")
        self.geometry("1400x900")
        self.after(0, lambda: self.state('zoomed')) 
        ctk.set_appearance_mode("dark")
        
        if not os.path.exists("cache"):
            os.makedirs("cache")
            
        self.all_games = GameScanner.get_games()
        self.filtered_games = self.all_games
        
        self.setup_navbar()

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)

        self.setup_recent_section()

        self.grid_header = ctk.CTkLabel(self.main_scroll, text="ALL GAMES", font=("Segoe UI", 18, "bold"), anchor="w")
        self.grid_header.pack(fill="x", padx=35, pady=(30, 10))
        
        self.grid_container = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        self.populate_games()
        self.bind("<Configure>", self.on_resize)

    def setup_navbar(self):
        self.navbar = ctk.CTkFrame(self, height=70, fg_color="#111111", corner_radius=0)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(self.navbar, text="GAMEVAULT", font=("Segoe UI", 26, "bold"), text_color="#238636")
        self.logo_label.pack(side="left", padx=35)

        self.search_entry = ctk.CTkEntry(
            self.navbar, placeholder_text="Search your library...", 
            width=350, height=40, corner_radius=20, 
            fg_color="#1a1a1a", border_color="#333333"
        )
        self.search_entry.pack(side="right", padx=35)
        self.search_entry.bind("<KeyRelease>", self.filter_search)

    def filter_search(self, event=None):
        query = self.search_entry.get().lower()
        self.filtered_games = [g for g in self.all_games if query in g['title'].lower()]
        self.populate_games()

    def setup_recent_section(self):
        self.recent_header = ctk.CTkLabel(self.main_scroll, text="RECENTLY PLAYED", font=("Segoe UI", 18, "bold"), anchor="w")
        self.recent_header.pack(fill="x", padx=35, pady=(20, 10))

        # Using #242424 to hide the scrollbar without transparency errors
        bg_hex = "#242424" 

        self.recent_scroll = ctk.CTkScrollableFrame(
            self.main_scroll, 
            orientation="horizontal", 
            height=320, 
            fg_color="transparent",
            scrollbar_button_color=bg_hex,
            scrollbar_button_hover_color=bg_hex
        )
        self.recent_scroll.pack(fill="x", padx=25)
        self.update_recent_display()

    def update_recent_display(self):
        for child in self.recent_scroll.winfo_children():
            child.destroy()

        if os.path.exists("recent.json"):
            with open("recent.json", "r") as f:
                recent_games = json.load(f)[:8]
            
            for game in recent_games:
                img = self.get_cached_image(game.get('title'), game.get('cover'), size=(195, 270))
                btn = ctk.CTkButton(
                    self.recent_scroll, text=game['title'] if not img else "",
                    image=img, width=195, height=270, 
                    fg_color="transparent", 
                    hover_color="#242424", 
                    command=lambda g=game: self.launch_and_refresh(g)
                )
                btn.pack(side="left", padx=10)

    def launch_and_refresh(self, game):
        GameLauncher.start(game)
        self.after(500, self.update_recent_display)

    def populate_games(self):
        for child in self.grid_container.winfo_children():
            child.destroy()

        width = self.winfo_width()
        cols = max(1, width // 250) 
        
        for i, game in enumerate(self.filtered_games):
            img = self.get_cached_image(game.get('title'), game.get('cover'), size=(230, 345))
            btn = ctk.CTkButton(
                self.grid_container, text=game['title'] if not img else "", 
                image=img, width=230, height=345,
                fg_color="transparent", 
                hover_color="#242424", 
                command=lambda g=game: self.launch_and_refresh(g)
            )
            btn.grid(row=i // cols, column=i % cols, padx=10, pady=15)

    def get_cached_image(self, title, url, size):
        if not url: return None
        clean_name = "".join([c for c in title if c.isalnum()]).lower()
        cache_path = f"cache/{clean_name}.png"
        try:
            if os.path.exists(cache_path):
                img_data = Image.open(cache_path)
            else:
                response = requests.get(url, timeout=5)
                img_data = Image.open(BytesIO(response.content))
                img_data.save(cache_path)
            return ctk.CTkImage(light_image=img_data, dark_image=img_data, size=size)
        except:
            return None

    def on_resize(self, event):
        if event.widget == self:
            self.populate_games()

if __name__ == "__main__":
    app = AppWindow()
    app.mainloop()