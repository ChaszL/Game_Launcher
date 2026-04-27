import customtkinter as ctk
from launcher import GameLauncher
from PIL import Image
import requests
from io import BytesIO
import json
import os
import sys

# This finds the folder where your .exe (or .py file) is located
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Now use application_path for your files
config_path = os.path.join(application_path, "config.json")
# Load config once at the top
with open("config.json", "r") as f:
    cfg = json.load(f)

class AppWindow(ctk.CTk):
    def __init__(self, pre_scanned_games):
        super().__init__()
        
        self.title(cfg["ui"]["title"])
        self.geometry("1400x900")
        self.after(0, lambda: self.state('zoomed')) 
        ctk.set_appearance_mode("dark")
        
        if not os.path.exists(cfg["cache_folder"]):
            os.makedirs(cfg["cache_folder"])
            
        self.all_games = pre_scanned_games
        self.filtered_games = self.all_games
        
        # UI Setup
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
        self.navbar = ctk.CTkFrame(self, height=70, fg_color=cfg["ui"]["bg_dark"], corner_radius=0)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(self.navbar, text=cfg["ui"]["title"], font=("Segoe UI", 26, "bold"), text_color=cfg["ui"]["primary_color"])
        self.logo_label.pack(side="left", padx=35)

        self.search_entry = ctk.CTkEntry(self.navbar, placeholder_text="Search library...", width=350)
        self.search_entry.pack(side="right", padx=35)
        self.search_entry.bind("<KeyRelease>", self.filter_search)

    def filter_search(self, event=None):
        query = self.search_entry.get().lower()
        self.filtered_games = [g for g in self.all_games if query in g['title'].lower()]
        self.populate_games()

    def setup_recent_section(self):
        self.recent_header = ctk.CTkLabel(
            self.main_scroll, 
            text="RECENTLY PLAYED", 
            font=("Segoe UI", 18, "bold"), 
            anchor="w"
        )
        self.recent_header.pack(fill="x", padx=35, pady=(20, 10))

        # We pull the background color from the config to match exactly
        bg_color = "#242424"  # Using primary color for scrollbar to blend in

        self.recent_scroll = ctk.CTkScrollableFrame(
            self.main_scroll, 
            orientation="horizontal", 
            height=320, 
            fg_color="transparent",
            # This makes the scrollbar handle invisible by matching the background
            scrollbar_button_color=bg_color,
            scrollbar_button_hover_color=bg_color
        )
        self.recent_scroll.pack(fill="x", padx=25)
        self.update_recent_display()

    def update_recent_display(self):
        for child in self.recent_scroll.winfo_children():
            child.destroy()

        if os.path.exists(cfg["recent_file"]):
            with open(cfg["recent_file"], "r") as f:
                recent_games = json.load(f)
            
            for game in recent_games:
                img = self.get_cached_image(game.get('title'), game.get('cover'), size=tuple(cfg["ui"]["recent_size"]))
                btn = ctk.CTkButton(self.recent_scroll, text=game['title'] if not img else "", image=img, 
                                    width=cfg["ui"]["recent_size"][0], height=cfg["ui"]["recent_size"][1],
                                    fg_color="transparent", hover_color=cfg["ui"]["card_hover"],
                                    command=lambda g=game: self.launch_and_refresh(g))
                btn.pack(side="left", padx=10)
    
    def on_mouse_wheel(self, event):
        """
        Custom scroll handler to multiply the scroll distance.
        event.delta is typically 120 or -120 on Windows.
        """
        # Get speed from config (default to 2 if not found)
        speed = cfg["ui"].get("scroll_speed", 2)
        
        # Determine direction: -1 for up/left, 1 for down/right
        direction = int(-1 * (event.delta / 120))
        
        # For the vertical main scroll
        self.main_scroll._canvas.yview_scroll(direction * speed, "units")

    def launch_and_refresh(self, game):
        GameLauncher.start(game)
        self.after(500, self.update_recent_display)

    def populate_games(self):
        for child in self.grid_container.winfo_children():
            child.destroy()

        width = self.winfo_width()
        cols = max(1, width // cfg["ui"]["grid_columns_base"]) 
        
        for i, game in enumerate(self.filtered_games):
            img = self.get_cached_image(game.get('title'), game.get('cover'), size=tuple(cfg["ui"]["cover_size"]))
            btn = ctk.CTkButton(self.grid_container, text=game['title'] if not img else "", 
                                image=img, width=cfg["ui"]["cover_size"][0], height=cfg["ui"]["cover_size"][1],
                                fg_color="transparent", hover_color=cfg["ui"]["card_hover"],
                                command=lambda g=game: self.launch_and_refresh(g))
            btn.grid(row=i // cols, column=i % cols, padx=10, pady=15)

    def get_cached_image(self, title, url, size):
        if not url: return None
        clean_name = "".join([c for c in title if c.isalnum()]).lower()
        cache_path = f"{cfg['cache_folder']}/{clean_name}.png"
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
