import customtkinter as ctk

class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Hide title bar and borders for a "pro" look
        self.overrideredirect(True)
        
        # Center the window on the screen
        window_width = 400
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.configure(fg_color="#000000")

        # Label
        self.label = ctk.CTkLabel(
            self, 
            text="Paradise Launcher", 
            font=("Segoe UI", 32, "bold"), 
            text_color="#63cdff"
        )
        self.label.pack(expand=True, pady=(20, 0))

        self.loading_label = ctk.CTkLabel(
            self, 
            text="Loading launcher...", 
            font=("Segoe UI", 14), 
            text_color="#888888"
        )
        self.loading_label.pack(expand=True, pady=(0, 20))
        
        # Force the window to show up immediately
        self.update()