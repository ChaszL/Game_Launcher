import os
import json
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

class GameLauncher:
    @staticmethod
    def start(game_data):
        try:
            os.startfile(game_data['path'])
            GameLauncher.update_recent(game_data)
        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def update_recent(game_data):
        r_file = config["recent_file"]
        r_limit = config["ui"]["recent_limit"]
        recent_list = []
        
        if os.path.exists(r_file):
            with open(r_file, "r") as f:
                try: recent_list = json.load(f)
                except: recent_list = []

        recent_list = [g for g in recent_list if g['path'] != game_data['path']]
        recent_list.insert(0, game_data)
        
        with open(r_file, "w") as f:
            json.dump(recent_list[:r_limit], f)