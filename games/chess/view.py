import customtkinter as ctk
import chess
import threading
import sys
import os
from PIL import Image, ImageTk

from .ai_player import get_ai_move

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ui_utils import show_congratulations
from sound_utils import play_move_sound

class ChessView(ctk.CTkFrame):
    def __init__(self, master, app_root):
        super().__init__(master, corner_radius=10)
        self.app_root = app_root
        
        self.board = chess.Board()
        self.mode = "Human vs Bot"
        self.bot_diff = "Medium"
        self.selected_square = None
        self.is_ai_thinking = False
        self.game_id = 0
        self.redo_stack = []
        
        self.images = {}
        self.small_images = {}
        self.cached_size = 0
        
        self.setup_ui()
        self.load_small_images()
        self.update_all()

    def setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Top Controls
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.control_frame, text="Mode:", font=("Arial", 14)).grid(row=0, column=0, padx=(50, 5))
        self.mode_var = ctk.StringVar(value=self.mode)
        self.mode_menu = ctk.CTkOptionMenu(self.control_frame, variable=self.mode_var, width=150,
                                         values=["Human vs Human", "Human vs Bot", "Bot vs Human", "Human vs AI", "AI vs Human"],
                                         command=self.change_mode)
        self.mode_menu.grid(row=0, column=1, padx=5)
        
        self.diff_lbl = ctk.CTkLabel(self.control_frame, text="Bot IQ:", font=("Arial", 14))
        self.diff_lbl.grid(row=0, column=2, padx=(20, 5))
        
        self.bot_iq_entry = ctk.CTkEntry(self.control_frame, width=60)
        self.bot_iq_entry.insert(0, "800")
        self.bot_iq_entry.grid(row=0, column=3, padx=5)
        self.bot_iq_entry.bind("<Return>", self.confirm_iq)
        
        self.reset_btn = ctk.CTkButton(self.control_frame, text="New Game", width=100, command=self.reset_game)
        self.reset_btn.grid(row=0, column=4, padx=20)
        
        self.undo_btn = ctk.CTkButton(self.control_frame, text="< Undo", width=60, command=self.undo_move)
        self.undo_btn.grid(row=0, column=5, padx=5)
        
        self.redo_btn = ctk.CTkButton(self.control_frame, text="Redo >", width=60, command=self.redo_move)
        self.redo_btn.grid(row=0, column=6, padx=5)
        
        self.status_label = ctk.CTkLabel(self.control_frame, text="White's Turn", font=("Arial", 16, "bold"))
        self.status_label.grid(row=0, column=7, padx=20)

        # Main layout
        self.canvas_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.canvas_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.center_wrapper = ctk.CTkFrame(self.canvas_container, fg_color="transparent")
        self.center_wrapper.pack(expand=True, pady=20)
        
        self.top_captured = ctk.CTkFrame(self.center_wrapper, fg_color="transparent", height=45)
        self.top_captured.pack(fill="x", pady=(0, 5))
        
        self.board_iq_frame = ctk.CTkFrame(self.center_wrapper, fg_color="transparent")
        self.board_iq_frame.pack()
        
        self.board_size = 500
        self.canvas_frame = ctk.CTkFrame(self.board_iq_frame, fg_color="#2b2b2b", width=self.board_size, height=self.board_size)
        self.canvas_frame.pack(side="left")
        self.canvas_frame.pack_propagate(False)
        self.canvas_frame.grid_propagate(False)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # IQ Progress Bar
        self.iq_bar = ctk.CTkProgressBar(self.board_iq_frame, orientation="vertical", width=15, height=self.board_size, progress_color="#F1C40F")
        self.iq_bar.pack(side="left", padx=(10, 0))
        self.iq_bar.set(0.5)
        
        self.bottom_captured = ctk.CTkFrame(self.center_wrapper, fg_color="transparent", height=45)
        self.bottom_captured.pack(fill="x", pady=(5, 0))
        
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        self.app_root.bind("<Control-MouseWheel>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-plus>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-minus>", self.on_zoom, add="+")
        self.app_root.bind("<KeyPress-equal>", self.on_zoom, add="+")
        self.app_root.bind("<F11>", self.auto_fit_zoom, add="+")

    def auto_fit_zoom(self, event=None):
        if not self.winfo_ismapped(): return
        
        optimal_size = self.app_root.winfo_height() - 150
        self.board_size = max(300, min(1500, optimal_size))
        
        self.canvas_frame.configure(width=self.board_size, height=self.board_size)
        self.canvas.configure(width=self.board_size, height=self.board_size)
        self.iq_bar.configure(height=self.board_size)
        self.draw_board()

    def confirm_iq(self, event=None):
        self.bot_iq_entry.configure(fg_color="#3498DB")
        self.after(300, lambda: self.bot_iq_entry.configure(fg_color=["#F9F9FA", "#343638"]))

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
        self.canvas.configure(width=self.board_size, height=self.board_size)
        self.iq_bar.configure(height=self.board_size)
        self.draw_board()

    def change_mode(self, new_mode):
        self.mode = new_mode
        if "AI" in self.mode or "Human vs Human" == self.mode:
            self.diff_lbl.grid_remove()
            self.bot_iq_entry.grid_remove()
        else:
            self.diff_lbl.grid()
            self.bot_iq_entry.grid()
        self.reset_game()

    def reset_game(self):
        self.game_id += 1
        self.board.reset()
        self.redo_stack = []
        self.selected_square = None
        self.is_ai_thinking = False
        self.update_all()
        self.check_ai_turn()

    def undo_move(self):
        if self.is_ai_thinking: return
        if len(self.board.move_stack) > 0:
            self.redo_stack.append(self.board.pop())
            self.update_all()

    def redo_move(self):
        if self.is_ai_thinking: return
        if self.redo_stack:
            self.board.push(self.redo_stack.pop())
            self.update_all()

    def update_all(self):
        self.update_status()
        self.update_iq()
        self.update_captured()
        self.draw_board()

    def update_status(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            self.status_label.configure(text=f"Checkmate! {winner} Wins!")
            
            is_ai_win = False
            if self.mode in ["Human vs Bot", "Human vs AI"] and winner == "Black": is_ai_win = True
            elif self.mode in ["Bot vs Human", "AI vs Human"] and winner == "White": is_ai_win = True
            
            show_congratulations(self.app_root, f"Checkmate! {winner} Wins! 🎉👑🏆", callback=self.reset_game, is_ai=is_ai_win)
        elif self.board.is_game_over():
            self.status_label.configure(text="Draw!")
        elif self.board.is_check():
            turn = "White" if self.board.turn else "Black"
            self.status_label.configure(text=f"{turn} is in Check!")
        else:
            turn = "White" if self.board.turn else "Black"
            self.status_label.configure(text=f"{turn}'s Turn")

    def update_iq(self):
        score = 0
        for sq in chess.SQUARES:
            piece = self.board.piece_at(sq)
            if piece:
                val = 0
                if piece.piece_type == chess.PAWN: val = 1
                elif piece.piece_type == chess.KNIGHT: val = 3
                elif piece.piece_type == chess.BISHOP: val = 3
                elif piece.piece_type == chess.ROOK: val = 5
                elif piece.piece_type == chess.QUEEN: val = 9
                
                if piece.color == chess.WHITE: score += val
                else: score -= val
                
        # Clamp score between -20 and +20, convert to 0.0-1.0
        score = max(-20, min(20, score))
        progress = 0.5 + (score / 40.0)
        self.iq_bar.set(progress)

    def update_captured(self):
        for w in self.top_captured.winfo_children(): w.destroy()
        for w in self.bottom_captured.winfo_children(): w.destroy()
        
        starting = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
        current_w = {pt: len(self.board.pieces(pt, chess.WHITE)) for pt in starting}
        current_b = {pt: len(self.board.pieces(pt, chess.BLACK)) for pt in starting}
        
        captured_w = [] # White pieces captured by Black (Black's trophies)
        for pt, count in starting.items():
            for _ in range(count - current_w[pt]): captured_w.append((pt, chess.WHITE))
            
        captured_b = [] # Black pieces captured by White (White's trophies)
        for pt, count in starting.items():
            for _ in range(count - current_b[pt]): captured_b.append((pt, chess.BLACK))
            
        flip_board = False
        if self.mode in ["Bot vs Human", "AI vs Human"]: flip_board = True
        elif self.mode == "Human vs Human": flip_board = not self.board.turn
        
        if flip_board:
            top_list = captured_b
            bot_list = captured_w
        else:
            top_list = captured_w
            bot_list = captured_b
            
        self._render_captured(self.top_captured, top_list)
        self._render_captured(self.bottom_captured, bot_list)

    def _render_captured(self, frame, pieces):
        # Sort pieces by value
        piece_order = {chess.QUEEN: 0, chess.ROOK: 1, chess.BISHOP: 2, chess.KNIGHT: 3, chess.PAWN: 4}
        pieces.sort(key=lambda p: piece_order[p[0]])
        
        for pt, color in pieces:
            img = self.small_images.get((pt, color))
            if img:
                lbl = ctk.CTkLabel(frame, text="", image=img)
                lbl.pack(side="right", padx=2)

    def get_cell_size(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return 0, 0, 0
        size = min(w, h)
        cell_size = int(size / 8)
        offset_x = (w - (cell_size * 8)) / 2
        offset_y = (h - (cell_size * 8)) / 2
        return cell_size, offset_x, offset_y

    def load_small_images(self):
        pieces = {
            chess.PAWN: ('wP', 'bP'), chess.KNIGHT: ('wN', 'bN'),
            chess.BISHOP: ('wB', 'bB'), chess.ROOK: ('wR', 'bR'),
            chess.QUEEN: ('wQ', 'bQ'), chess.KING: ('wK', 'bK')
        }
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        assets_dir = os.path.join(base_dir, "assets", "chess_pieces")
        
        for pt, (w_name, b_name) in pieces.items():
            for color, name in [(chess.WHITE, w_name), (chess.BLACK, b_name)]:
                path = os.path.join(assets_dir, f"{name}.png")
                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA")
                    self.small_images[(pt, color)] = ctk.CTkImage(light_image=img, dark_image=img, size=(35, 35))

    def load_images(self, size):
        if size == self.cached_size and self.images:
            return
        self.cached_size = size
        self.images.clear()
        
        pieces = {
            chess.PAWN: ('wP', 'bP'), chess.KNIGHT: ('wN', 'bN'),
            chess.BISHOP: ('wB', 'bB'), chess.ROOK: ('wR', 'bR'),
            chess.QUEEN: ('wQ', 'bQ'), chess.KING: ('wK', 'bK')
        }
        
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        assets_dir = os.path.join(base_dir, "assets", "chess_pieces")
        
        for pt, (w_name, b_name) in pieces.items():
            for color, name in [(chess.WHITE, w_name), (chess.BLACK, b_name)]:
                path = os.path.join(assets_dir, f"{name}.png")
                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA").resize((int(size*0.9), int(size*0.9)), Image.Resampling.LANCZOS)
                    self.images[(pt, color)] = ImageTk.PhotoImage(img)

    def draw_board(self, skip_square=None):
        self.canvas.delete("all")
        cell_size, offset_x, offset_y = self.get_cell_size()
        if cell_size == 0:
            return
            
        self.load_images(cell_size)
            
        legal_moves = [m.to_square for m in self.board.legal_moves if m.from_square == self.selected_square] if self.selected_square is not None else []
            
        flip_board = False
        if self.mode in ["Bot vs Human", "AI vs Human"]: flip_board = True
        elif self.mode == "Human vs Human": flip_board = not self.board.turn
        
        last_move_squares = []
        if len(self.board.move_stack) > 0:
            last_move = self.board.peek()
            last_move_squares = [last_move.from_square, last_move.to_square]
            
        for display_rank in range(8):
            for display_file in range(8):
                chess_rank = display_rank if flip_board else 7 - display_rank
                chess_file = 7 - display_file if flip_board else display_file
                
                sq = chess.square(chess_file, chess_rank)
                x1 = offset_x + display_file * cell_size
                y1 = offset_y + display_rank * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                is_light = (display_rank + display_file) % 2 == 0
                
                if self.selected_square == sq:
                    color = "#f6f669"
                elif sq in legal_moves:
                    color = "#E67E22" if is_light else "#D35400"
                elif sq in last_move_squares:
                    color = "#f6f669" if is_light else "#baca44"
                else:
                    color = "#ebecd0" if is_light else "#739552"
                    
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                piece = self.board.piece_at(sq)
                if piece and sq != skip_square:
                    img = self.images.get((piece.piece_type, piece.color))
                    if img:
                        self.canvas.create_image(x1 + cell_size/2, y2, image=img, anchor="s")
                
                if display_file == 0:
                    text_color = "#739552" if is_light else "#ebecd0"
                    self.canvas.create_text(x1 + 3, y1 + 3, text=str(chess_rank + 1), fill=text_color, font=("Helvetica", max(10, int(cell_size*0.18)), "bold"), anchor="nw")
                
                if display_rank == 7:
                    text_color = "#739552" if is_light else "#ebecd0"
                    file_letter = chr(ord('a') + chess_file)
                    self.canvas.create_text(x2 - 3, y2 - 3, text=file_letter, fill=text_color, font=("Helvetica", max(10, int(cell_size*0.18)), "bold"), anchor="se")

    def on_canvas_resize(self, event):
        self.draw_board()

    def on_canvas_click(self, event):
        if self.is_ai_thinking or self.board.is_game_over():
            return
            
        is_white_turn = self.board.turn
        if self.mode in ["Human vs Bot", "Human vs AI"] and not is_white_turn: return
        if self.mode in ["Bot vs Human", "AI vs Human"] and is_white_turn: return
            
        cell_size, offset_x, offset_y = self.get_cell_size()
        if cell_size == 0:
            return
            
        display_file = int((event.x - offset_x) // cell_size)
        display_rank = int((event.y - offset_y) // cell_size)
        
        if 0 <= display_file < 8 and 0 <= display_rank < 8:
            flip_board = False
            if self.mode in ["Bot vs Human", "AI vs Human"]: flip_board = True
            elif self.mode == "Human vs Human": flip_board = not self.board.turn
                
            chess_rank = display_rank if flip_board else 7 - display_rank
            chess_file = 7 - display_file if flip_board else display_file
            
            sq = chess.square(chess_file, chess_rank)
            piece = self.board.piece_at(sq)
            
            if self.selected_square is None:
                if piece and piece.color == self.board.turn:
                    self.selected_square = sq
                    self.draw_board()
            else:
                move = chess.Move(self.selected_square, sq)
                if piece := self.board.piece_at(self.selected_square):
                    if piece.piece_type == chess.PAWN:
                        if (piece.color == chess.WHITE and chess.square_rank(sq) == 7) or \
                           (piece.color == chess.BLACK and chess.square_rank(sq) == 0):
                            move = chess.Move(self.selected_square, sq, promotion=chess.QUEEN)
                
                if move in self.board.legal_moves:
                    self.selected_square = None
                    self.redo_stack = [] # New move clears redo stack
                    self.animate_move(move, lambda: self._finish_human_move(move))
                else:
                    if piece and piece.color == self.board.turn:
                        self.selected_square = sq
                    else:
                        self.selected_square = None
                    self.draw_board()

    def _finish_human_move(self, move):
        self.board.push(move)
        play_move_sound()
        self.update_all()
        self.check_ai_turn()

    def animate_move(self, move, callback):
        cell_size, offset_x, offset_y = self.get_cell_size()
        if cell_size == 0:
            callback()
            return
            
        self.draw_board(skip_square=move.from_square)
        
        flip_board = False
        if self.mode in ["Bot vs Human", "AI vs Human"]: flip_board = True
        elif self.mode == "Human vs Human": 
            # During animation of human vs human, the board is oriented for the player who just moved
            # However self.board.turn has NOT been updated yet!
            flip_board = not self.board.turn
        
        start_rank = chess.square_rank(move.from_square)
        start_file = chess.square_file(move.from_square)
        end_rank = chess.square_rank(move.to_square)
        end_file = chess.square_file(move.to_square)
        
        start_display_rank = start_rank if flip_board else 7 - start_rank
        start_display_file = 7 - start_file if flip_board else start_file
        end_display_rank = end_rank if flip_board else 7 - end_rank
        end_display_file = 7 - end_file if flip_board else end_file
        
        start_x = offset_x + start_display_file * cell_size + cell_size/2
        start_y = offset_y + start_display_rank * cell_size + cell_size/2
        target_x = offset_x + end_display_file * cell_size + cell_size/2
        target_y = offset_y + end_display_rank * cell_size + cell_size/2
        
        piece = self.board.piece_at(move.from_square)
        img = self.images.get((piece.piece_type, piece.color))
        if not img:
            callback()
            return
            
        anim_piece = self.canvas.create_image(start_x, start_y + cell_size/2, image=img, anchor="s")
        
        steps = 10
        dx = (target_x - start_x) / steps
        dy = (target_y - start_y) / steps
        
        def step_anim(step):
            if step < steps:
                self.canvas.move(anim_piece, dx, dy)
                self.after(15, step_anim, step + 1)
            else:
                self.canvas.delete(anim_piece)
                callback()
                
        step_anim(1)

    def check_ai_turn(self):
        if self.board.is_game_over(): return
        
        is_white_turn = self.board.turn
        should_ai_move = False
        
        if self.mode in ["Human vs Bot", "Human vs AI"] and not is_white_turn: should_ai_move = True
        elif self.mode in ["Bot vs Human", "AI vs Human"] and is_white_turn: should_ai_move = True
        
        if should_ai_move:
            self.is_ai_thinking = True
            self.status_label.configure(text="AI is thinking...")
            threading.Thread(target=self.make_ai_move, args=(self.game_id,)).start()

    def make_ai_move(self, current_game_id):
        try:
            iq = int(self.bot_iq_entry.get())
        except ValueError:
            iq = 800
            
        if "AI" in self.mode:
            diff = "Extremely Hard"
        else:
            if iq < 500: diff = "Easy"
            elif iq < 1000: diff = "Medium"
            elif iq < 1500: diff = "Hard"
            else: diff = "Extremely Hard"
            
        board_copy = self.board.copy()
        move = get_ai_move(board_copy, diff)
        
        if move and current_game_id == self.game_id:
            self.after(100, self.animate_move, move, lambda: self._finish_ai_move(move, current_game_id))

    def _finish_ai_move(self, move, current_game_id):
        if current_game_id != self.game_id: return
        self.board.push(move)
        play_move_sound()
        self.is_ai_thinking = False
        self.update_all()
        self.check_ai_turn()
