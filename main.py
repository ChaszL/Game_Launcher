import threading
import json
from splash import SplashScreen
from interface import AppWindow
from scanner import GameScanner

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

class LauncherController:
    def __init__(self):
        self.config = load_config()
        self.splash = SplashScreen()
        
        # Run ONLY the data scanning in the background
        threading.Thread(target=self.prepare_data, daemon=True).start()
        self.splash.mainloop()

    def prepare_data(self):
        # Scan games and fetch API assets here (The heavy lifting)
        # This keeps the Splash Screen spinning/responsive
        scanned_games = GameScanner.get_games()
        
        # Data is ready! Tell the main thread to build the UI
        self.splash.after(0, lambda: self.launch_app(scanned_games))

    def launch_app(self, games):
        self.splash.destroy()
        # Create the window on the MAIN thread
        self.app = AppWindow(games)
        self.app.mainloop()

if __name__ == "__main__":
    LauncherController()