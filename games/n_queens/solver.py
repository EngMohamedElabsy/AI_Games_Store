import random

class NQueensSolver:
    def __init__(self, n):
        self.n = n
        self.board = [-1] * n  # board[i] = row of queen in column i
        self.row_counts = [0] * n
        self.diag1_counts = [0] * (2 * n - 1)  # row + col
        self.diag2_counts = [0] * (2 * n - 1)  # row - col + (n - 1)

    def initialize_board(self):
        # Smart greedy initialization
        for c in range(self.n):
            min_conflicts = float('inf')
            best_rows = []
            for r in range(self.n):
                conflicts = self.row_counts[r] + self.diag1_counts[r + c] + self.diag2_counts[r - c + self.n - 1]
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_rows = [r]
                elif conflicts == min_conflicts:
                    best_rows.append(r)
            
            # Choose a random row among the best
            r = random.choice(best_rows)
            self.board[c] = r
            self.row_counts[r] += 1
            self.diag1_counts[r + c] += 1
            self.diag2_counts[r - c + self.n - 1] += 1

    def get_conflicts(self, c, r):
        # Number of conflicts if queen in col c is moved to row r
        res = self.row_counts[r] + self.diag1_counts[r + c] + self.diag2_counts[r - c + self.n - 1]
        if self.board[c] == r:
            res -= 3  # Exclude itself
        return res

    def solve(self, max_steps=100000):
        self.initialize_board()
        for step in range(max_steps):
            conflicted_cols = []
            for c in range(self.n):
                r = self.board[c]
                if self.row_counts[r] > 1 or self.diag1_counts[r + c] > 1 or self.diag2_counts[r - c + self.n - 1] > 1:
                    conflicted_cols.append(c)
            
            if not conflicted_cols:
                return True, self.board  # Solved
            
            c = random.choice(conflicted_cols)
            r_old = self.board[c]
            
            min_conflicts = float('inf')
            best_rows = []
            for r in range(self.n):
                conflicts = self.get_conflicts(c, r)
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_rows = [r]
                elif conflicts == min_conflicts:
                    best_rows.append(r)
                    
            r_new = random.choice(best_rows)
            
            if r_old != r_new:
                # Update counts
                self.row_counts[r_old] -= 1
                self.diag1_counts[r_old + c] -= 1
                self.diag2_counts[r_old - c + self.n - 1] -= 1
                
                self.board[c] = r_new
                
                self.row_counts[r_new] += 1
                self.diag1_counts[r_new + c] += 1
                self.diag2_counts[r_new - c + self.n - 1] += 1
                
        return False, self.board

def solve_n_queens(n):
    solver = NQueensSolver(n)
    success, board = solver.solve()
    # If it fails, retry once (rare for min-conflicts)
    if not success:
        solver = NQueensSolver(n)
        success, board = solver.solve()
    return board
