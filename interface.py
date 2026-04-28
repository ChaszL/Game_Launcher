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
        self.configure(fg_color=cfg["ui"]["background_color"])

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
        self.navbar = ctk.CTkFrame(self, height=70, fg_color=cfg["ui"]["navbar_color"], corner_radius=0)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(self.navbar, text=cfg["ui"]["title"], font=("Segoe UI", 26, "bold"), text_color=cfg["ui"]["logo_color"])
        self.logo_label.pack(side="left", padx=35)

        self.settings_btn = ctk.CTkButton(self.navbar, text="Change Theme", width=40, command=self.toggle_color_settings)
        self.settings_btn.pack(side="right", padx=20)

        self.search_entry = ctk.CTkEntry(self.navbar, placeholder_text="Search library...", width=350)
        self.search_entry.pack(side="right", padx=35)
        self.search_entry.bind("<KeyRelease>", self.filter_search)

    def toggle_color_settings(self):
        # create a small popup-style window for color settings 
        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("Theme Settings")
        self.settings_window.geometry("300x400")
        self.settings_window.lift()
        self.settings_window.after(10, self.settings_window.focus_force)

        ctk.CTkLabel(self.settings_window, text="Background Hex Color:").pack(pady=(20, 5))
        self.bg_input = ctk.CTkEntry(self.settings_window, placeholder_text="#FFFFFF")
        self.bg_input.insert(0, cfg["ui"]["background_color"])
        self.bg_input.pack(pady=5)

        ctk.CTkLabel(self.settings_window, text="Navigation Bar Hex Color:").pack(pady=(10, 0))
        self.primary_input = ctk.CTkEntry(self.settings_window, placeholder_text="#FFFFFF")
        self.primary_input.insert(0, cfg["ui"]["navbar_color"])
        self.primary_input.pack(pady=5)

        ctk.CTkLabel(self.settings_window, text="Logo Hex Color:").pack(pady=(20, 5))
        self.logo_input = ctk.CTkEntry(self.settings_window, placeholder_text="#FFFFFF")
        self.logo_input.insert(0, cfg["ui"]["logo_color"])
        self.logo_input.pack(pady=5)

        save_btn = ctk.CTkButton(self.settings_window, text="Save & Apply", command=self.save_theme)
        save_btn.pack(pady=20)

    def save_theme(self):
        # A quick helper to fix missing '#'
        def fix_hex(color):
            color = color.strip()
            if color and not color.startswith("#"):
                return f"#{color}"
            return color

        # 1. Update the in-memory config with the fixed hex codes
        new_background = fix_hex(self.bg_input.get())
        new_navbar = fix_hex(self.primary_input.get())
        new_logo = fix_hex(self.logo_input.get())

        cfg["ui"]["background_color"] = new_background
        cfg["ui"]["navbar_color"] = new_navbar
        cfg["ui"]["logo_color"] = new_logo

        # 2. Write to config.json
        try:
            with open("config.json", "w") as f:
                json.dump(cfg, f, indent=4)
            
            # 3. Visual Feedback: Update Main Window & Navbar
            self.configure(fg_color=new_background)      
            self.navbar.configure(fg_color=new_navbar)   
            self.logo_label.configure(text_color=new_logo)

            # 4. FIX: Force Scrollable Frames to match the new background
            # This removes that blue/grey tint from the game library area
            self.main_scroll.configure(fg_color=new_background)
            self.recent_scroll.configure(fg_color=new_background)

            # 5. FIX: Update Scrollbar buttons to blend into the background
            self.main_scroll.configure(
                scrollbar_button_color=new_background,
                scrollbar_button_hover_color=new_background
            )
            self.recent_scroll.configure(
                scrollbar_button_color=new_background,
                scrollbar_button_hover_color=new_background
            )
            
            # 6. Redraw the games so the hover colors on cards update too
            self.populate_games()
            self.update_recent_display()

            self.settings_window.destroy()
            print("Theme saved successfully!")
        except Exception as e:
            print(f"Error saving theme: {e}")

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
        bg_color = cfg["ui"]["background_color"]

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
                                    fg_color="transparent", hover_color=cfg["ui"]["background_color"],
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
                                fg_color="transparent", hover_color=cfg["ui"]["background_color"],
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