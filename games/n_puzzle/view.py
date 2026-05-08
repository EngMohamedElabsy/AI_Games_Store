import customtkinter as ctk
from .solver import solve_n_puzzle, scramble_board
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ui_utils import show_congratulations
from sound_utils import play_slide_sound

class NPuzzleView(ctk.CTkFrame):
    def __init__(self, master, app_root):
        super().__init__(master, corner_radius=10)
        self.app_root = app_root
        
        self.n = 4
        self.difficulty = "Medium"
        self.board = list(range(1, self.n*self.n)) + [0]
        self.buttons = {}
        self.is_animating = False
        
        self.setup_ui()
        self.create_grid()
        self.scramble()

    def setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, pady=10, sticky="ew")
        self.control_frame.grid_columnconfigure(5, weight=1)
        
        ctk.CTkLabel(self.control_frame, text="Grid Size (N):", font=("Arial", 14)).grid(row=0, column=0, padx=(50, 10))
        
        self.n_entry = ctk.CTkEntry(self.control_frame, width=50)
        self.n_entry.insert(0, str(self.n))
        self.n_entry.grid(row=0, column=1, padx=10)
        self.n_entry.bind("<Return>", lambda e: self.update_n())
        
        self.set_btn = ctk.CTkButton(self.control_frame, text="Set N", width=80, command=self.update_n)
        self.set_btn.grid(row=0, column=2, padx=10)

        ctk.CTkLabel(self.control_frame, text="Difficulty:", font=("Arial", 14)).grid(row=0, column=3, padx=(20, 5))
        self.diff_var = ctk.StringVar(value=self.difficulty)
        self.diff_menu = ctk.CTkOptionMenu(self.control_frame, variable=self.diff_var,
                                         values=["Easy", "Medium", "Hard", "Expert"],
                                         command=self.change_difficulty)
        self.diff_menu.grid(row=0, column=4, padx=5)
        
        self.scramble_btn = ctk.CTkButton(self.control_frame, text="Scramble", width=100, fg_color="#3498DB", hover_color="#2980B9", command=self.scramble)
        self.scramble_btn.grid(row=0, column=5, padx=10, sticky="e")
        
        self.solve_btn = ctk.CTkButton(self.control_frame, text="Solve AI", width=120, fg_color="#E67E22", hover_color="#D35400", command=self.solve_ai)
        self.solve_btn.grid(row=0, column=6, padx=10)

        self.grid_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.center_wrapper = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.center_wrapper.pack(expand=True, pady=20)
        
        self.board_size = 500
        self.grid_frame = ctk.CTkFrame(self.center_wrapper, fg_color="#2b2b2b", width=self.board_size, height=self.board_size)
        self.grid_frame.pack(side="left")
        self.grid_frame.pack_propagate(False)
        self.grid_frame.grid_propagate(False)
        
        self.iq_bar = ctk.CTkProgressBar(self.center_wrapper, orientation="vertical", width=20, height=self.board_size, progress_color="#3498DB")
        self.iq_bar.pack(side="left", padx=(15, 0))
        self.iq_bar.set(1.0)
        self.max_dist = 1
        
        self.app_root.bind("<Control-MouseWheel>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-plus>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-minus>", self.on_zoom, add="+")
        self.app_root.bind("<F11>", self.auto_fit_zoom, add="+")

    def auto_fit_zoom(self, event=None):
        if not self.winfo_ismapped(): return
        if self.is_animating: return
        
        optimal_size = self.app_root.winfo_height() - 250
        self.board_size = max(300, min(1500, optimal_size))
        self.grid_frame.configure(width=self.board_size, height=self.board_size)
        self.iq_bar.configure(height=self.board_size)
        
        self.cell_size = self.board_size / self.n
        font_size = max(10, int((self.board_size / 500) * 20 * 4/self.n))
        size = self.cell_size - 4
        
        for val, btn in self.buttons.items():
            btn.configure(width=size, height=size, font=("Arial", font_size, "bold"))
            
        self.place_all_buttons()

    def on_zoom(self, event):
        if not self.winfo_ismapped(): return
        if self.is_animating: return
        
        if hasattr(event, 'delta') and event.delta:
            if event.delta > 0: self.board_size += 50
            else: self.board_size -= 50
        elif event.keysym in ['plus', 'equal']:
            self.board_size += 50
        elif event.keysym == 'minus':
            self.board_size -= 50
            
        self.board_size = max(300, min(1500, self.board_size))
        self.grid_frame.configure(width=self.board_size, height=self.board_size)
        self.iq_bar.configure(height=self.board_size)
        
        self.cell_size = self.board_size / self.n
        font_size = max(10, int((self.board_size / 500) * 20 * 4/self.n))
        size = self.cell_size - 4
        
        for val, btn in self.buttons.items():
            btn.configure(width=size, height=size, font=("Arial", font_size, "bold"))
            
        self.place_all_buttons()

    def update_n(self):
        if self.is_animating: return
        try:
            val = int(self.n_entry.get())
            if val > 50:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", "Cannot exceed 50 due to screen size limits.")
                return
            if 3 <= val <= 50:
                self.n = val
                self.board = list(range(1, self.n*self.n)) + [0]
                self.create_grid()
                self.scramble()
        except ValueError:
            pass

    def create_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        self.cell_size = self.board_size / self.n
        
        self.buttons = {}
        font_size = max(10, int((self.board_size / 500) * 20 * 4/self.n))
        size = self.cell_size - 4
        for val in range(1, self.n * self.n):
            btn = ctk.CTkButton(self.grid_frame, text=str(val), font=("Arial", font_size, "bold"), fg_color="#1F6AA5", width=size, height=size)
            btn.configure(command=lambda v=val: self.on_tile_click(v))
            self.buttons[val] = btn
            
        self.place_all_buttons()

    def place_all_buttons(self):
        for i, val in enumerate(self.board):
            if val != 0:
                r, c = i // self.n, i % self.n
                x = c * self.cell_size + 2
                y = r * self.cell_size + 2
                self.buttons[val].place(x=x, y=y)

    def on_tile_click(self, val):
        if self.is_animating: return
        
        idx = self.board.index(val)
        zero_idx = self.board.index(0)
        r, c = idx // self.n, idx % self.n
        zr, zc = zero_idx // self.n, zero_idx % self.n
        
        if abs(r - zr) + abs(c - zc) == 1:
            self.board[zero_idx], self.board[idx] = self.board[idx], self.board[zero_idx]
            self.animate_tile(val, zr, zc, check_win=True)
            play_slide_sound()

    def animate_tile(self, val, target_r, target_c, check_win=False, fast=False, callback=None):
        self.is_animating = True
        btn = self.buttons[val]
        target_x = target_c * self.cell_size + 2
        target_y = target_r * self.cell_size + 2
        
        current_x = float(btn.place_info()['x'])
        current_y = float(btn.place_info()['y'])
        
        steps = 3 if fast else 6
        dx = (target_x - current_x) / steps
        dy = (target_y - current_y) / steps
        delay = 5 if fast else 10
        
        def step_anim(step):
            if step < steps:
                btn.place(x=current_x + dx*step, y=current_y + dy*step)
                self.after(delay, step_anim, step + 1)
            else:
                btn.place(x=target_x, y=target_y)
                self.is_animating = False
                self.update_iq()
                if check_win: self.check_win()
                if callback: callback()
                
        step_anim(1)

    def calculate_manhattan(self):
        distance = 0
        for i in range(self.n * self.n):
            val = self.board[i]
            if val != 0:
                target_r = (val - 1) // self.n
                target_c = (val - 1) % self.n
                r = i // self.n
                c = i % self.n
                distance += abs(target_r - r) + abs(target_c - c)
        return distance

    def update_iq(self):
        dist = self.calculate_manhattan()
        if not hasattr(self, 'max_dist') or self.max_dist == 0:
            self.max_dist = max(1, dist)
        progress = max(0.0, 1.0 - (dist / self.max_dist))
        self.iq_bar.set(progress)

    def change_difficulty(self, new_diff):
        self.difficulty = new_diff
        self.scramble()

    def scramble(self):
        if self.is_animating: return
        multipliers = {"Easy": 2, "Medium": 5, "Hard": 10, "Expert": 30}
        m = multipliers.get(self.difficulty, 5)
        moves = self.n * m
        self.board = scramble_board(self.n, moves)
        self.max_dist = max(1, self.calculate_manhattan())
        self.update_iq()
        self.place_all_buttons()

    def check_win(self, is_ai=False):
        goal = list(range(1, self.n*self.n)) + [0]
        if self.board == goal:
            show_congratulations(self.app_root, callback=self.scramble, is_ai=is_ai)

    def solve_ai(self):
        if self.is_animating: return
        
        self.solve_btn.configure(text="Thinking...", state="disabled")
        import threading
        threading.Thread(target=self._solve_thread, daemon=True).start()

    def _solve_thread(self):
        path = solve_n_puzzle(self.board, self.n)
        self.after(0, self._on_solve_complete, path)

    def _on_solve_complete(self, path):
        self.solve_btn.configure(text="Solve AI", state="normal")
        if not path: return
        self.animate_solution(path, 0)
        
    def animate_solution(self, path, step):
        if step < len(path):
            idx = path[step]
            zero_idx = self.board.index(0)
            val = self.board[idx]
            
            self.board[zero_idx], self.board[idx] = self.board[idx], self.board[zero_idx]
            zr, zc = zero_idx // self.n, zero_idx % self.n
            
            play_slide_sound()
            self.animate_tile(val, zr, zc, fast=True, callback=lambda: self.after(1, self.animate_solution, path, step + 1))
        else:
            self.check_win(is_ai=True)
