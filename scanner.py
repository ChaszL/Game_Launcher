import os
import json
from steam_api import enrich_game_data
import sys

# This finds the folder where your .exe (or .py file) is located
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Now use application_path for your files
config_path = os.path.join(application_path, "config.json")
with open("config.json", "r") as f:
    config = json.load(f)

class GameScanner:
    @staticmethod
    def get_games():
        folder = config["games_folder"]
        # Use application_path instead of __file__ to find the folder next to the .exe
        path = os.path.join(application_path, folder) 
        
        if not os.path.exists(path):
            os.makedirs(path)
            return []

        games = []
        for file in os.listdir(path):
            if file.endswith(".lnk") or file.endswith(".url"):
                games.append({
                    "title": os.path.splitext(file)[0],
                    "path": os.path.join(path, file)
                })
        return enrich_game_data(games)
