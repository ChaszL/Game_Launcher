import os
from steam_api import enrich_game_data # Import your enrichment function

class GameScanner:
    @staticmethod
    def get_games(folder_name="games"):
        path = os.path.join(os.path.dirname(__file__), folder_name)
        
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
        
        # This calls your steam_api logic to add 'hero' and 'cover' URLs
        return enrich_game_data(games)