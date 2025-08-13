import tkinter as tk
from tkinter import messagebox
import math
import random
import threading
from typing import Optional, List, Tuple

class FourInARowCreative:
    def __init__(self, master):
        self.master = master
        self.setup_window()
        self.initialize_game_state()
        self.create_ui()
        self.reset_game()

    def setup_window(self):
        """Configure the main window with focus on game board."""
        self.master.title("Four in a Row - Pro v0.4.8")
        self.master.geometry("800x600")
        self.master.resizable(False, False)
        
        # Modern dark background
        self.master.config(bg="#0F172A")
        
        # Center the window
        x = (self.master.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.master.winfo_screenheight() // 2) - (600 // 2)
        self.master.geometry(f"800x600+{x}+{y}")

    def initialize_game_state(self):
        """Initialize all game state variables."""
        # Board dimensions and sizing (fit within 800x600 alongside sidebar)
        self.cols = 7
        self.rows = 6
        self.cell_size = 70  # 7 * 70 = 490px width, 6 * 70 = 420px height
        self.board_width = self.cols * self.cell_size
        self.board_height = self.rows * self.cell_size
        # Radii for slots/pieces derived from cell size
        self.slot_radius = int(self.cell_size * 0.40)
        self.piece_outer_radius = int(self.cell_size * 0.38)
        self.piece_mid_radius = int(self.cell_size * 0.30)
        self.piece_inner_radius = int(self.cell_size * 0.20)
        self.preview_radius = int(self.cell_size * 0.35)

        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = "red"
        self.game_mode = "ai"
        self.difficulty = "hard"
        self.move_history = []
        self.scores = {"red": 0, "yellow": 0}
        self.game_active = True
        self.paused = False
        self.animation_in_progress = False
        # Track pending AI timer to allow cancellation
        self.pending_ai_after_id = None

    def create_ui(self):
        """Create UI with game board as main focus."""
        # Create compact header
        self.create_compact_header()
        
        # Main container with horizontal layout
        main_container = tk.Frame(self.master, bg="#0F172A")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left sidebar for controls and info
        self.create_sidebar(main_container)
        
        # Central game board (main focus)
        self.create_main_game_area(main_container)

    def create_compact_header(self):
        """Create minimal header."""
        header = tk.Frame(self.master, bg="#0F172A", height=60)
        header.pack(fill="x", pady=(10, 5))
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text="Four in a Row - Pro v0.4.8",
            font=("Arial", 16, "bold"),
            fg="#64748B",
            bg="#0F172A"
        )
        title_label.pack(pady=15)

    def create_sidebar(self, parent):
        """Create compact sidebar with all controls."""
        sidebar = tk.Frame(parent, bg="#1E293B", width=180)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)
        
        # Scores section (compact)
        self.create_compact_scores(sidebar)
        
        # Game controls (compact)
        self.create_compact_controls(sidebar)
        
        # Game options (compact)
        self.create_compact_options(sidebar)
        
        # Status area (compact)
        self.create_compact_status(sidebar)

    def create_compact_scores(self, parent):
        """Create compact score display."""
        score_frame = tk.Frame(parent, bg="#1E293B")
        score_frame.pack(fill="x", padx=10, pady=15)
        
        # Title
        tk.Label(score_frame, text="SCORES", font=("Arial", 10, "bold"),
                fg="#94A3B8", bg="#1E293B").pack()
        
        # Player 1 score
        p1_frame = tk.Frame(score_frame, bg="#DC2626", height=40)
        p1_frame.pack(fill="x", pady=(10, 5))
        p1_frame.pack_propagate(False)
        
        tk.Label(p1_frame, text="🔴 P1", font=("Arial", 9, "bold"),
                fg="#FEF2F2", bg="#DC2626").pack(side="left", padx=8, pady=10)
        
        self.player1_score_label = tk.Label(p1_frame, text="0", font=("Arial", 18, "bold"),
                                          fg="#FEF2F2", bg="#DC2626")
        self.player1_score_label.pack(side="right", padx=8, pady=5)
        
        # Player 2 score
        p2_frame = tk.Frame(score_frame, bg="#EAB308", height=40)
        p2_frame.pack(fill="x", pady=5)
        p2_frame.pack_propagate(False)
        
        tk.Label(p2_frame, text="🟡 P2", font=("Arial", 9, "bold"),
                fg="#FFFBEB", bg="#EAB308").pack(side="left", padx=8, pady=10)
        
        self.player2_score_label = tk.Label(p2_frame, text="0", font=("Arial", 18, "bold"),
                                          fg="#FFFBEB", bg="#EAB308")
        self.player2_score_label.pack(side="right", padx=8, pady=5)

    def create_compact_controls(self, parent):
        """Create compact control buttons."""
        controls_frame = tk.Frame(parent, bg="#1E293B")
        controls_frame.pack(fill="x", padx=10, pady=15)
        
        tk.Label(controls_frame, text="CONTROLS", font=("Arial", 10, "bold"),
                fg="#94A3B8", bg="#1E293B").pack()
        
        button_style = {
            "font": ("Arial", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "pady": 8,
            "width": 15
        }
        
        # New Game
        self.new_game_btn = tk.Button(
            controls_frame, text="🎮 New Game", command=self.reset_game,
            bg="#3B82F6", fg="#F8FAFC", activebackground="#2563EB", **button_style
        )
        self.new_game_btn.pack(fill="x", pady=(8, 3))
        
        # Undo
        self.undo_btn = tk.Button(
            controls_frame, text="↶ Undo", command=self.undo_move,
            bg="#6B7280", fg="#F8FAFC", activebackground="#4B5563", **button_style
        )
        self.undo_btn.pack(fill="x", pady=3)
        
        # Pause
        self.pause_btn = tk.Button(
            controls_frame, text="⏸ Pause", command=self.toggle_pause,
            bg="#8B5CF6", fg="#F8FAFC", activebackground="#7C3AED", **button_style
        )
        self.pause_btn.pack(fill="x", pady=3)

    def create_compact_options(self, parent):
        """Create compact game options."""
        options_frame = tk.Frame(parent, bg="#1E293B")
        options_frame.pack(fill="x", padx=10, pady=15)
        
        tk.Label(options_frame, text="OPTIONS", font=("Arial", 10, "bold"),
                fg="#94A3B8", bg="#1E293B").pack()
        
        # Mode
        tk.Label(options_frame, text="Mode", font=("Arial", 8),
                fg="#CBD5E1", bg="#1E293B").pack(anchor="w", pady=(8, 2))
        
        self.game_mode_var = tk.StringVar(value="ai")
        mode_menu = tk.OptionMenu(options_frame, self.game_mode_var,
                                 "ai", "2player", command=self.set_game_mode)
        self.style_compact_menu(mode_menu)
        mode_menu.pack(fill="x")
        
        # Difficulty
        tk.Label(options_frame, text="Difficulty", font=("Arial", 8),
                fg="#CBD5E1", bg="#1E293B").pack(anchor="w", pady=(8, 2))
        
        self.difficulty_var = tk.StringVar(value="hard")
        diff_menu = tk.OptionMenu(options_frame, self.difficulty_var,
                                 "easy", "medium", "hard", command=self.set_difficulty)
        self.style_compact_menu(diff_menu)
        diff_menu.pack(fill="x")

    def style_compact_menu(self, menu):
        """Style compact option menus."""
        menu.config(
            bg="#374151", fg="#F8FAFC", font=("Arial", 9),
            relief="flat", bd=0, highlightthickness=0,
            activebackground="#4B5563", cursor="hand2"
        )
        menu["menu"].config(
            bg="#374151", fg="#F8FAFC", font=("Arial", 9),
            activebackground="#4B5563"
        )

    def create_compact_status(self, parent):
        """Create compact status area."""
        status_frame = tk.Frame(parent, bg="#1E293B")
        status_frame.pack(fill="x", side="bottom", padx=10, pady=15)
        
        tk.Label(status_frame, text="STATUS", font=("Arial", 10, "bold"),
                fg="#94A3B8", bg="#1E293B").pack()
        
        self.status_label = tk.Label(
            status_frame, text="", font=("Arial", 10, "bold"),
            fg="#F8FAFC", bg="#1E293B", wraplength=150
        )
        self.status_label.pack(pady=(5, 0))
        
        # Paused indicator
        self.paused_label = tk.Label(
            status_frame, text="⏸ PAUSED", font=("Arial", 9, "bold"),
            fg="#F59E0B", bg="#1E293B"
        )

    def create_main_game_area(self, parent):
        """Create the main game board area - THE FOCUS."""
        game_area = tk.Frame(parent, bg="#0F172A")
        game_area.pack(side="right", fill="both", expand=True)
        
        # Center the board vertically and horizontally
        board_container = tk.Frame(game_area, bg="#0F172A")
        board_container.pack(expand=True)
        
        # Board title (minimal)
        board_title = tk.Label(
            board_container, text="GAME BOARD",
            font=("Arial", 14, "bold"), fg="#94A3B8", bg="#0F172A"
        )
        board_title.pack(pady=(0, 15))
        
        # The main game canvas - LARGE and CLEAR
        canvas_frame = tk.Frame(board_container, bg="#1E293B", relief="raised", bd=4)
        canvas_frame.pack()
        
        # Sized from board dimensions
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.board_width,
            height=self.board_height,
            bg="#0F172A",
            highlightthickness=3,
            highlightcolor="#3B82F6"
        )
        self.canvas.pack(padx=15, pady=15)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.handle_hover)
        self.canvas.bind("<Leave>", self.clear_hover)

    def draw_board(self):
        """Draw large, clear game board."""
        self.canvas.delete("all")
        
        # Draw board background
        self.canvas.create_rectangle(
            0, 0, self.board_width, self.board_height,
            fill="#1E293B", outline="#3B82F6", width=4
        )
        
        # Draw column separators for clarity
        for col in range(1, self.cols):
            x = col * self.cell_size
            self.canvas.create_line(
                x, 0, x, self.board_height,
                fill="#374151", width=2
            )
        
        # Draw row separators for clarity
        for row in range(1, self.rows):
            y = row * self.cell_size
            self.canvas.create_line(
                0, y, self.board_width, y,
                fill="#374151", width=2
            )
        
        # Draw slots and pieces
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                
                # Draw large, clear slot
                self.canvas.create_oval(
                    x - self.slot_radius, y - self.slot_radius, x + self.slot_radius, y + self.slot_radius,
                    fill="#0F172A", outline="#64748B", width=3
                )
                
                # Draw piece if exists
                piece = self.board[row][col]
                if piece:
                    self.draw_large_piece(x, y, piece)

    def draw_large_piece(self, x: int, y: int, color: str):
        """Draw large, beautiful game pieces."""
        if color == "red":
            # Large red piece with multiple gradients (scaled)
            self.canvas.create_oval(
                x - self.piece_outer_radius, y - self.piece_outer_radius, x + self.piece_outer_radius, y + self.piece_outer_radius,
                fill="#DC2626", outline="#B91C1C", width=4
            )
            self.canvas.create_oval(
                x - self.piece_mid_radius, y - self.piece_mid_radius, x + self.piece_mid_radius, y + self.piece_mid_radius,
                fill="#EF4444", outline="", width=0
            )
            self.canvas.create_oval(
                x - self.piece_inner_radius, y - self.piece_inner_radius, x + self.piece_inner_radius, y + self.piece_inner_radius,
                fill="#F87171", outline="", width=0
            )
            # Large shine effect
            self.canvas.create_oval(
                x - int(self.piece_inner_radius * 0.75), y - self.piece_inner_radius, x - int(self.piece_inner_radius * 0.25), y - int(self.piece_inner_radius * 0.1), 
                fill="#FCA5A5", outline="", width=0
            )
        else:  # yellow
            # Large yellow piece with multiple gradients (scaled)
            self.canvas.create_oval(
                x - self.piece_outer_radius, y - self.piece_outer_radius, x + self.piece_outer_radius, y + self.piece_outer_radius,
                fill="#EAB308", outline="#CA8A04", width=4
            )
            self.canvas.create_oval(
                x - self.piece_mid_radius, y - self.piece_mid_radius, x + self.piece_mid_radius, y + self.piece_mid_radius,
                fill="#FDE047", outline="", width=0
            )
            self.canvas.create_oval(
                x - self.piece_inner_radius, y - self.piece_inner_radius, x + self.piece_inner_radius, y + self.piece_inner_radius,
                fill="#FEF08A", outline="", width=0
            )
            # Large shine effect
            self.canvas.create_oval(
                x - int(self.piece_inner_radius * 0.75), y - self.piece_inner_radius, x - int(self.piece_inner_radius * 0.25), y - int(self.piece_inner_radius * 0.1),
                fill="#FEF3C7", outline="", width=0
            )

    def handle_click(self, event):
        """Handle clicks on the large board."""
        if not self.game_active or self.paused or self.animation_in_progress:
            return
        
        col = event.x // self.cell_size
        if 0 <= col < self.cols:
            self.make_move(int(col))

    def handle_hover(self, event):
        """Enhanced hover effects for large board."""
        if not self.game_active or self.paused or self.animation_in_progress:
            return
        
        col = event.x // self.cell_size
        if 0 <= col < self.cols:
            self.canvas.delete("hover")
            col = int(col)
            # Highlight entire column
            self.canvas.create_rectangle(
                col * self.cell_size + 2, 2, (col + 1) * self.cell_size - 2, self.board_height - 2,
                fill="#3B82F6", stipple="gray12", tags="hover"
            )
            
            # Show preview piece at top
            x = col * self.cell_size + self.cell_size // 2
            y = self.cell_size // 2
            color = "#DC2626" if self.current_player == "red" else "#EAB308"
            self.canvas.create_oval(
                x - self.preview_radius, y - self.preview_radius, x + self.preview_radius, y + self.preview_radius,
                fill=color, outline="#F8FAFC", width=2, tags="hover"
            )

    def clear_hover(self, event):
        """Clear hover effects."""
        self.canvas.delete("hover")

    def make_move(self, col: int):
        """Make a move with enhanced animation."""
        if not (0 <= col < self.cols) or self.animation_in_progress:
            return
        
        row = self.get_lowest_empty_row(col)
        if row == -1:
            messagebox.showwarning("Invalid Move", "Column is full!")
            return
        
        self.animation_in_progress = True
        self.board[row][col] = self.current_player
        self.move_history.append((row, col, self.current_player))
        
        # Clear hover effects
        self.canvas.delete("hover")
        
        # Enhanced animation for large board
        self.animate_large_piece_drop(row, col, self.current_player)

    def animate_large_piece_drop(self, target_row: int, target_col: int, player: str):
        """Enhanced animation for large pieces."""
        x = target_col * self.cell_size + self.cell_size // 2
        start_y = -self.piece_outer_radius
        end_y = target_row * self.cell_size + self.cell_size // 2
        current_y = start_y
        velocity = 0
        gravity = max(2, int(self.cell_size / 35))
        
        # Colors
        piece_color = "#DC2626" if player == "red" else "#EAB308"
        outline_color = "#B91C1C" if player == "red" else "#CA8A04"
        r = self.piece_outer_radius
        
        # Create large animated piece
        piece_id = self.canvas.create_oval(
            x - r, current_y - r, x + r, current_y + r,
            fill=piece_color, outline=outline_color, width=4
        )
        
        def drop_step():
            nonlocal current_y, velocity
            
            if current_y < end_y:
                velocity += gravity
                current_y += velocity
                
                if current_y >= end_y:
                    current_y = end_y
                    # Bounce effect for scaled pieces
                    bounce_threshold = max(6, int(self.cell_size / 12))
                    if velocity > bounce_threshold:
                        velocity = -int(velocity * 0.4)
                        current_y = end_y + velocity
                    else:
                        velocity = 0
                
                self.canvas.coords(
                    piece_id,
                    x - r, current_y - r, x + r, current_y + r
                )
                
                if current_y != end_y or velocity != 0:
                    self.master.after(25, drop_step)
                else:
                    self.canvas.delete(piece_id)
                    self.draw_board()
                    self.animation_in_progress = False
                    self.post_move_logic(target_row, target_col)
            else:
                self.canvas.delete(piece_id)
                self.draw_board()
                self.animation_in_progress = False
                self.post_move_logic(target_row, target_col)
        
        drop_step()

    def post_move_logic(self, row: int, col: int):
        """Handle post-move logic."""
        if self.check_win(row, col):
            self.scores[self.current_player] += 1
            self.update_scores()
            winner = "Player 1" if self.current_player == "red" else "Player 2"
            self.update_status(f"🎉 {winner} Wins!")
            self.game_active = False
            # Ensure no pending AI move fires after game end
            self.cancel_pending_ai()
            self.show_game_end_modal(f"{winner} Wins!")
            return
        
        if self.check_draw():
            self.update_status("🤝 Draw!")
            self.game_active = False
            self.cancel_pending_ai()
            self.show_game_end_modal("It's a Draw!")
            return
        
        # Switch players
        self.current_player = "yellow" if self.current_player == "red" else "red"
        player_name = "Player 1" if self.current_player == "red" else "Player 2"
        self.update_status(f"🎯 {player_name}'s Turn")
        
        # AI move
        if self.game_mode == "ai" and self.current_player == "yellow":
            self.cancel_pending_ai()
            self.pending_ai_after_id = self.master.after(1200, self.make_ai_move)

    def get_lowest_empty_row(self, col: int) -> int:
        """Get lowest empty row."""
        for r in range(self.rows - 1, -1, -1):
            if self.board[r][col] is None:
                return r
        return -1

    def check_win(self, row: int, col: int) -> bool:
        """Check for win condition."""
        player = self.board[row][col]
        
        # Check all directions
        directions = [
            [(0, 1), (0, -1)],    # Horizontal
            [(1, 0), (-1, 0)],    # Vertical
            [(1, 1), (-1, -1)],   # Diagonal /
            [(1, -1), (-1, 1)]    # Diagonal \
        ]
        
        for direction_pair in directions:
            count = 1  # Current piece
            for dr, dc in direction_pair:
                r, c = row + dr, col + dc
                while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                    count += 1
                    r, c = r + dr, c + dc
            if count >= 4:
                return True
        
        return False

    def check_draw(self) -> bool:
        """Check for draw."""
        return all(self.board[0][c] is not None for c in range(self.cols))

    def update_status(self, message: str):
        """Update status display."""
        self.status_label.config(text=message)

    def update_scores(self):
        """Update score display."""
        self.player1_score_label.config(text=str(self.scores["red"]))
        self.player2_score_label.config(text=str(self.scores["yellow"]))

    def show_game_end_modal(self, message: str):
        """Show game end dialog."""
        title = "🏆 Game Over!" if "Win" in message else "🤝 Game Over!"
        response = messagebox.askyesno(title, f"{message}\n\nPlay Again?")
        if response:
            self.reset_game()
        else:
            self.master.destroy()

    def set_game_mode(self, mode: str):
        """Set game mode."""
        self.game_mode = mode
        self.reset_game()

    def set_difficulty(self, difficulty: str):
        """Set AI difficulty."""
        self.difficulty = difficulty
        self.reset_game()

    def reset_game(self):
        """Reset game state."""
        self.cancel_pending_ai()
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = "red"
        self.move_history = []
        self.game_active = True
        self.paused = False
        self.animation_in_progress = False
        self.canvas.delete("hover")
        self.draw_board()
        self.update_status("🎯 Player 1's Turn")

    def undo_move(self):
        """Undo last move."""
        if not self.move_history or self.animation_in_progress:
            return
        
        # Cancel any pending AI action to avoid desync
        self.cancel_pending_ai()
        
        last_move = self.move_history.pop()
        row, col, player = last_move
        self.board[row][col] = None
        
        self.current_player = "red" if self.current_player == "yellow" else "yellow"
        player_name = "Player 1" if self.current_player == "red" else "Player 2"
        self.update_status(f"🎯 {player_name}'s Turn")
        
        self.game_active = True
        self.draw_board()

    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ Resume")
            self.paused_label.pack(pady=(5, 0))
            self.update_status("⏸ PAUSED")
        else:
            self.pause_btn.config(text="⏸ Pause")
            self.paused_label.pack_forget()
            player_name = "Player 1" if self.current_player == "red" else "Player 2"
            self.update_status(f"🎯 {player_name}'s Turn")

    # AI Implementation
    def make_ai_move(self):
        """Make AI move (compute in background to keep UI responsive)."""
        # Clear the pending id as it's firing now
        self.pending_ai_after_id = None
        if not self.game_active or self.paused or self.animation_in_progress or self.current_player != "yellow":
            return

        board_copy = [row[:] for row in self.board]
        depth = self.get_difficulty_depth()

        def worker():
            try:
                best_col = self.minimax(board_copy, depth, True)[0]
            except Exception:
                best_col = None

            def apply_move():
                if not self.game_active or self.paused or self.animation_in_progress or self.current_player != "yellow":
                    return
                if best_col is not None:
                    self.make_move(best_col)
            self.master.after(0, apply_move)

        threading.Thread(target=worker, daemon=True).start()

    def minimax(self, board: List[List[Optional[str]]], depth: int, maximizing_player: bool, alpha: float = -math.inf, beta: float = math.inf) -> Tuple[Optional[int], int]:
        """Minimax with alpha-beta pruning and center-first move ordering."""
        cols = len(board[0])
        valid_locations = [c for c in range(cols) if self.get_lowest_empty_row_sim(board, c) != -1]
        is_terminal = self.is_terminal_node(board)

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.check_win_sim(board, "yellow"):
                    return (None, 10_000_000_000)
                elif self.check_win_sim(board, "red"):
                    return (None, -10_000_000_000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, "yellow"))

        # Order moves: center-first
        center = cols // 2
        valid_locations.sort(key=lambda c: abs(center - c))

        if maximizing_player:
            value = -math.inf
            best_column = random.choice(valid_locations)
            for col in valid_locations:
                row_idx = self.get_lowest_empty_row_sim(board, col)
                b_copy = [r[:] for r in board]
                self.drop_piece_sim(b_copy, row_idx, col, "yellow")
                new_score = self.minimax(b_copy, depth - 1, False, alpha, beta)[1]
                if new_score > value:
                    value = new_score
                    best_column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return best_column, value
        else:
            value = math.inf
            best_column = random.choice(valid_locations)
            for col in valid_locations:
                row_idx = self.get_lowest_empty_row_sim(board, col)
                b_copy = [r[:] for r in board]
                self.drop_piece_sim(b_copy, row_idx, col, "red")
                new_score = self.minimax(b_copy, depth - 1, True, alpha, beta)[1]
                if new_score < value:
                    value = new_score
                    best_column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return best_column, value

    def score_position(self, board: List[List[Optional[str]]], player: str) -> int:
        """Score board position."""
        score = 0
        opponent = "red" if player == "yellow" else "yellow"

        rows = len(board)
        cols = len(board[0])

        # Center preference
        center_col = cols // 2
        center_array = [board[r][center_col] for r in range(rows)]
        center_count = center_array.count(player)
        score += center_count * 3

        # Horizontal windows
        for r in range(rows):
            row_array = board[r]
            for c in range(cols - 3):
                window = row_array[c:c + 4]
                score += self.evaluate_window(window, player, opponent)

        # Vertical windows
        for c in range(cols):
            col_array = [board[r][c] for r in range(rows)]
            for r in range(rows - 3):
                window = col_array[r:r + 4]
                score += self.evaluate_window(window, player, opponent)

        # Diagonal down-right
        for r in range(rows - 3):
            for c in range(cols - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)

        # Diagonal down-left
        for r in range(rows - 3):
            for c in range(3, cols):
                window = [board[r + i][c - i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)

        return score

    def evaluate_window(self, window: List[Optional[str]], player: str, opponent: str) -> int:
        """Evaluate 4-piece window."""
        score = 0
        player_count = window.count(player)
        empty_count = window.count(None)
        opponent_count = window.count(opponent)

        if player_count == 4:
            score += 100
        elif player_count == 3 and empty_count == 1:
            score += 5
        elif player_count == 2 and empty_count == 2:
            score += 2

        if opponent_count == 3 and empty_count == 1:
            score -= 4

        return score

    def is_terminal_node(self, board: List[List[Optional[str]]]) -> bool:
        """Check if terminal state."""
        return self.check_win_sim(board, "red") or self.check_win_sim(board, "yellow") or self.check_draw_sim(board)

    def check_win_sim(self, board: List[List[Optional[str]]], player: str) -> bool:
        """Check win in simulation."""
        rows = len(board)
        cols = len(board[0])
        # Horizontal
        for r in range(rows):
            for c in range(cols - 3):
                if all(board[r][col_idx] == player for col_idx in range(c, c + 4)):
                    return True
        # Vertical
        for c in range(cols):
            for r in range(rows - 3):
                if all(board[row_idx][c] == player for row_idx in range(r, r + 4)):
                    return True
        # Diagonal down-right
        for r in range(rows - 3):
            for c in range(cols - 3):
                if all(board[r + i][c + i] == player for i in range(4)):
                    return True
        # Diagonal down-left
        for r in range(rows - 3):
            for c in range(3, cols):
                if all(board[r + i][c - i] == player for i in range(4)):
                    return True
        return False

    def check_draw_sim(self, board: List[List[Optional[str]]]) -> bool:
        """Check draw in simulation."""
        cols = len(board[0])
        return all(board[0][c] is not None for c in range(cols))

    def drop_piece_sim(self, board: List[List[Optional[str]]], row: int, col: int, player: str):
        """Simulate dropping a piece on the board."""
        board[row][col] = player

    def get_lowest_empty_row_sim(self, board: List[List[Optional[str]]], col: int) -> int:
        """Get the lowest empty row in a simulated board."""
        for r in range(len(board) - 1, -1, -1):
            if board[r][col] is None:
                return r
        return -1

    def get_difficulty_depth(self) -> int:
        """Return minimax depth based on difficulty."""
        if self.difficulty == "easy":
            return 2
        elif self.difficulty == "medium":
            return 4
        else:
            return 6  # Hard

    def cancel_pending_ai(self):
        """Cancel any pending AI after callback if exists."""
        if self.pending_ai_after_id is not None:
            try:
                self.master.after_cancel(self.pending_ai_after_id)
            except Exception:
                pass
            finally:
                self.pending_ai_after_id = None


def main():
    """Main function to run the game."""
    root = tk.Tk()
    game = FourInARowCreative(root)
    root.mainloop()


if __name__ == "__main__":
    main()
