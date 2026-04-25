import os
import json

class GameLauncher:
    @staticmethod
    def start(game_data):
        try:
            # Launch the file
            os.startfile(game_data['path'])
            
            # Update the recent.json list
            GameLauncher.update_recent(game_data)
        except Exception as e:
            print(f"Error launching game: {e}")

    @staticmethod
    def update_recent(game_data):
        recent_file = "recent.json"
        recent_list = []
        
        if os.path.exists(recent_file):
            with open(recent_file, "r") as f:
                try:
                    recent_list = json.load(f)
                except:
                    recent_list = []

        # Remove game if it exists to move it to the front
        recent_list = [g for g in recent_list if g['path'] != game_data['path']]
        recent_list.insert(0, game_data)
        
        # INCREASED LIMIT: Now saves the top 7 games
        with open(recent_file, "w") as f:
            json.dump(recent_list[:8], f)