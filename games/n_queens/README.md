# N-Queens AI Solver: Min-Conflicts Algorithm

This document explains the AI algorithm used to solve the N-Queens problem in this project.

## The Algorithm: Min-Conflicts (Local Search)

The N-Queens problem is a classic Constraint Satisfaction Problem (CSP). While it can be solved using backtracking, backtracking becomes extremely slow for large values of N (e.g., N=50). 

To solve it instantly even for very large grid sizes, we use the **Min-Conflicts Algorithm**, which is a local search algorithm.

### How Min-Conflicts Works

Instead of placing queens one by one and backtracking upon failure, Min-Conflicts starts with a complete but potentially invalid board (all queens placed). It then iteratively improves the board by moving queens to positions that reduce the total number of conflicts.

1. **Initialization**: Place one queen in each column randomly.
2. **Conflict Evaluation**: Count how many other queens are attacking each position (same row, or same diagonals).
3. **Iterative Repair**: Pick a queen that is currently in conflict, and move it to the row in its column that has the *minimum number of conflicts*.
4. **Repeat** until no queens are attacking each other.

### The Conflict Evaluation Logic

To rapidly evaluate conflicts without scanning the whole board, we maintain arrays that count the number of queens in every row and diagonal.

```python
def get_conflicts(self, c, r):
    # c: column, r: row
    # Calculate conflicts using O(1) lookups in our tracking arrays
    res = self.row_counts[r] + self.diag1_counts[r + c] + self.diag2_counts[r - c + self.n - 1]
    
    # Exclude the queen itself if it's already in this position
    if self.board[c] == r:
        res -= 3
    return res
```

### Implementation Details

The algorithm continuously loops, picking a random conflicted column and moving the queen to the best possible row.

```python
import random

def solve(self, max_steps=100000):
    self.initialize_board()
    
    for step in range(max_steps):
        # 1. Find all columns that have a conflicted queen
        conflicted_cols = self.get_conflicted_columns()
        
        # 2. If no conflicts, we won!
        if not conflicted_cols:
            return True, self.board
        
        # 3. Pick a random conflicted column
        c = random.choice(conflicted_cols)
        
        # 4. Find the row with the absolute minimum conflicts
        min_conflicts = float('inf')
        best_rows = []
        for r in range(self.n):
            conflicts = self.get_conflicts(c, r)
            if conflicts < min_conflicts:
                min_conflicts = conflicts
                best_rows = [r]
            elif conflicts == min_conflicts:
                best_rows.append(r)
                
        # 5. Move the queen to one of the best rows randomly (to avoid local optima)
        best_row = random.choice(best_rows)
        self.move_queen(c, best_row)
```

### Why Min-Conflicts for N-Queens?
Min-Conflicts is incredibly efficient for dense CSPs like N-Queens. While traditional backtracking struggles with N > 30, Min-Conflicts can solve N = 1,000,000 in seconds. It escapes local optima by picking random conflicting queens and randomly breaking ties among the best rows.
