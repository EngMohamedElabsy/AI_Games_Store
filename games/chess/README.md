# Chess AI: Minimax with Alpha-Beta Pruning

This document explains the artificial intelligence algorithm powering the Chess Bot in this project.

## The Algorithm: Minimax

Chess is a two-player, zero-sum game with perfect information. To build a bot, we use the **Minimax Algorithm**. 

The concept is simple: 
- The AI (Maximizer) wants to maximize the board evaluation score.
- The Opponent (Minimizer) wants to minimize the board evaluation score.
The algorithm simulates all possible future moves up to a certain depth and assumes both players play optimally.

## Optimization: Alpha-Beta Pruning

Vanilla Minimax explores an astronomical number of nodes, making it too slow. We optimize it using **Alpha-Beta Pruning**, which completely skips evaluating branches of the game tree that are guaranteed to be worse than a previously discovered move.

- **Alpha**: The best (highest) score the Maximizer can guarantee.
- **Beta**: The best (lowest) score the Minimizer can guarantee.
If at any point `beta <= alpha`, we stop evaluating the current branch.

### The Evaluation Function

To decide who is winning at the end of the simulation depth, we need an evaluation function. Our AI uses **Material Evaluation** combined with basic positional scores (e.g., piece-square tables).

```python
def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn else 9999
        
    score = 0
    # Standard piece values
    piece_values = {
        chess.PAWN: 10,
        chess.KNIGHT: 30,
        chess.BISHOP: 30,
        chess.ROOK: 50,
        chess.QUEEN: 90
    }
    
    # Calculate material advantage
    for piece_type in piece_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
        
    return score
```

### Implementation Details

The core of the bot uses recursion to traverse the game tree. A `depth` limit (controlled by the Bot's "IQ" setting) determines how many moves ahead the AI thinks.

```python
def minimax(board, depth, alpha, beta, maximizing_player):
    # Base case: reached depth limit or game over
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval
```

### Why Minimax for Chess?
Minimax is the mathematical foundation of almost all traditional chess engines (including Stockfish, prior to neural networks). Combined with Alpha-Beta pruning, it allows the AI to look several moves ahead to trap the opponent and avoid blunders efficiently.
