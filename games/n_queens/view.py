import customtkinter as ctk
from PIL import Image, ImageTk
from .solver import solve_n_queens
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ui_utils import show_congratulations
from sound_utils import play_move_sound, play_error_sound

class NQueensView(ctk.CTkFrame):
    def __init__(self, master, app_root):
        super().__init__(master, corner_radius=10)
        self.app_root = app_root
        
        self.n = 4
        self.queens = [-1] * self.n # queens[col] = row
        self.danger_zones = []
        
        self.queen_image = None
        self.cached_size = 0
        
        self.setup_ui()
        self.draw_board()

    def setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, pady=10, sticky="ew")
        self.control_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(self.control_frame, text="Grid Size (N):", font=("Arial", 14)).grid(row=0, column=0, padx=(50, 10))
        
        self.n_entry = ctk.CTkEntry(self.control_frame, width=50)
        self.n_entry.insert(0, str(self.n))
        self.n_entry.grid(row=0, column=1, padx=10)
        self.n_entry.bind("<Return>", lambda e: self.update_n())
        
        self.set_btn = ctk.CTkButton(self.control_frame, text="Set N", width=80, command=self.update_n)
        self.set_btn.grid(row=0, column=2, padx=10)
        
        self.solve_btn = ctk.CTkButton(self.control_frame, text="Solve AI", width=120, fg_color="#E67E22", hover_color="#D35400", command=self.solve_ai)
        self.solve_btn.grid(row=0, column=4, padx=10)
        
        self.clear_btn = ctk.CTkButton(self.control_frame, text="Clear", width=80, fg_color="#C0392B", hover_color="#922B21", command=self.clear_board)
        self.clear_btn.grid(row=0, column=5, padx=10)

        self.canvas_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.canvas_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.center_wrapper = ctk.CTkFrame(self.canvas_container, fg_color="transparent")
        self.center_wrapper.pack(expand=True, pady=20)
        
        self.board_size = 500
        self.canvas_frame = ctk.CTkFrame(self.center_wrapper, fg_color="#2b2b2b", width=self.board_size, height=self.board_size)
        self.canvas_frame.pack()
        self.canvas_frame.pack_propagate(False)
        self.canvas_frame.grid_propagate(False)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.app_root.bind("<Control-MouseWheel>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-plus>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-minus>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-equal>", self.on_zoom, add="+")
        self.app_root.bind("<F11>", self.auto_fit_zoom, add="+")

    def auto_fit_zoom(self, event=None):
        if not self.winfo_ismapped(): return
        
        optimal_size = self.app_root.winfo_height() - 250
        self.board_size = max(300, min(1500, optimal_size))
        
        self.canvas_frame.configure(width=self.board_size, height=self.board_size)
        self.canvas.configure(width=self.board_size, height=self.board_size)
        self.draw_board()

    def on_zoom(self, event):
        if not self.winfo_ismapped(): return
        
        if hasattr(event, 'delta') and event.delta:
            if event.delta > 0: self.board_size += 50
            else: self.board_size -= 50
        elif event.keysym in ['plus', 'equal']:
            self.board_size += 50
        elif event.keysym == 'minus':
            self.board_size -= 50
            
        self.board_size = max(300, min(1500, self.board_size))
        self.canvas_frame.configure(width=self.board_size, height=self.board_size)
        self.draw_board()

    def update_n(self):
        try:
            val = int(self.n_entry.get())
            if val > 50:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", "Cannot exceed 50 due to screen size limits.")
                return
            if 4 <= val <= 50:
                self.n = val
                self.queens = [-1] * self.n
                self.danger_zones = []
                self.draw_board()
        except ValueError:
            pass

    def clear_board(self):
        self.queens = [-1] * self.n
        self.danger_zones = []
        self.draw_board()

    def on_canvas_resize(self, event):
        self.draw_board()

    def get_cell_size(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return 0, 0, 0
        size = min(w, h)
        cell_size = size / self.n
        offset_x = (w - size) / 2
        offset_y = (h - size) / 2
        return cell_size, offset_x, offset_y

    def load_queen_image(self, size):
        if size == self.cached_size and self.queen_image:
            return
        self.cached_size = size
        
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
        assets_dir = os.path.join(base_dir, "assets", "chess_pieces")
        path = os.path.join(assets_dir, "wQ.png")
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            # Golden tint
            r, g, b, a = img.split()
            r = r.point(lambda i: min(255, int(i * 1.5)))
            g = g.point(lambda i: min(255, int(i * 1.2)))
            b = b.point(lambda i: int(i * 0.3))
            img = Image.merge("RGBA", (r, g, b, a))
            
            img = img.resize((int(size*0.8), int(size*0.8)), Image.Resampling.LANCZOS)
            self.queen_image = ImageTk.PhotoImage(img)

    def draw_board(self):
        self.canvas.delete("all")
        cell_size, offset_x, offset_y = self.get_cell_size()
        if cell_size == 0:
            return
            
        self.load_queen_image(cell_size)
            
        for r in range(self.n):
            for c in range(self.n):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                color = "#eee" if (r + c) % 2 == 0 else "#666"
                if (r, c) in self.danger_zones:
                    color = "#E74C3C" if (r + c) % 2 == 0 else "#C0392B"
                    
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                if self.queens[c] == r:
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    if self.queen_image:
                        self.canvas.create_image(cx, cy, image=self.queen_image)
                    else:
                        radius = cell_size * 0.4
                        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#F1C40F", outline="#D4AC0D", width=2)
                        self.canvas.create_text(cx, cy, text="♕", font=("Arial", int(cell_size * 0.5)), fill="white")

    def on_canvas_press(self, event):
        cell_size, offset_x, offset_y = self.get_cell_size()
        if cell_size == 0:
            return
            
        c = int((event.x - offset_x) // cell_size)
        r = int((event.y - offset_y) // cell_size)
        
        if 0 <= c < self.n and 0 <= r < self.n:
            self.danger_zones = []
            
            if self.queens[c] == r:
                self.queens[c] = -1
                play_move_sound()
            else:
                valid = True
                for i in range(self.n):
                    if i != c and self.queens[i] != -1:
                        if self.queens[i] == r or abs(self.queens[i] - r) == abs(i - c):
                            valid = False
                            break
                
                if valid:
                    self.queens[c] = r
                    play_move_sound()
                else:
                    play_error_sound()
                    for i in range(self.n):
                        if self.queens[i] != -1:
                            qr = self.queens[i]
                            qc = i
                            for x in range(self.n):
                                for y in range(self.n):
                                    if x == qr or y == qc or abs(x - qr) == abs(y - qc):
                                        self.danger_zones.append((x, y))
                    self.danger_zones.append((r, c))
            
            self.draw_board()
            self.check_win()

    def on_canvas_release(self, event):
        if self.danger_zones:
            self.danger_zones = []
            self.draw_board()

    def check_win(self, is_ai=False):
        if -1 not in self.queens:
            show_congratulations(self.app_root, callback=self.clear_board, is_ai=is_ai)

    def solve_ai(self):
        self.queens = solve_n_queens(self.n)
        self.danger_zones = []
        self.draw_board()
        show_congratulations(self.app_root, callback=self.clear_board, is_ai=True)
