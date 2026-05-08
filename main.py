import customtkinter as ctk
from games.n_queens.view import NQueensView
from games.n_puzzle.view import NPuzzleView
from games.chess.view import ChessView

class AIGamesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Games Collection")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Fullscreen & Layout state ---
        self.is_fullscreen = False
        self.sidebar_hidden = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        
        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AI Games\nCollection", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_n_queens = ctk.CTkButton(self.sidebar_frame, text="N-Queens", command=self.show_n_queens)
        self.btn_n_queens.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_n_puzzle = ctk.CTkButton(self.sidebar_frame, text="N-Puzzle", command=self.show_n_puzzle)
        self.btn_n_puzzle.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_chess = ctk.CTkButton(self.sidebar_frame, text="Chess", command=self.show_chess)
        self.btn_chess.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_hide_sidebar = ctk.CTkButton(self.sidebar_frame, text="Hide Sidebar", fg_color="#7F8C8D", hover_color="#95A5A6", command=self.toggle_sidebar)
        self.btn_hide_sidebar.grid(row=4, column=0, padx=20, pady=10, sticky="s")
        
        # --- Main Content Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Dictionary to store views
        self.views = {}
        
        # Initialize views
        self.init_views()
        
        # Show default view
        self.show_n_queens()
        
        # Overlay button to show sidebar when hidden
        self.btn_show_sidebar = ctk.CTkButton(self, text="☰", width=40, height=40, font=("Arial", 20), command=self.toggle_sidebar, fg_color="#2C3E50")
        self.btn_show_sidebar.place(x=10, y=10)
        self.btn_show_sidebar.place_forget() # Initially hidden

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)

    def toggle_sidebar(self):
        if self.sidebar_hidden:
            # Show sidebar
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            self.btn_show_sidebar.place_forget()
            self.sidebar_hidden = False
        else:
            # Hide sidebar
            self.sidebar_frame.grid_forget()
            self.main_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
            self.btn_show_sidebar.place(x=10, y=10)
            self.btn_show_sidebar.lift()
            self.sidebar_hidden = True

    def init_views(self):
        self.views['n_queens'] = NQueensView(self.main_frame, self)
        self.views['n_puzzle'] = NPuzzleView(self.main_frame, self)
        self.views['chess'] = ChessView(self.main_frame, self)

    def hide_all_views(self):
        for view in self.views.values():
            view.pack_forget()

    def show_n_queens(self):
        self.hide_all_views()
        self.views['n_queens'].pack(fill="both", expand=True)

    def show_n_puzzle(self):
        self.hide_all_views()
        self.views['n_puzzle'].pack(fill="both", expand=True)

    def show_chess(self):
        self.hide_all_views()
        self.views['chess'].pack(fill="both", expand=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = AIGamesApp()
    app.mainloop()
