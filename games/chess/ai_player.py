import chess
import random

# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def evaluate_board(board):
    if board.is_checkmate():
        if board.turn:
            return -99999 # Black wins
        else:
            return 99999 # White wins
            
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
        return 0
        
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                score += val
            else:
                score -= val
                
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
        
    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
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
                break
        return min_eval

def get_best_move(board, depth):
    best_move = None
    maximizing_player = board.turn == chess.WHITE
    
    if maximizing_player:
        best_val = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            val = minimax(board, depth - 1, -float('inf'), float('inf'), False)
            board.pop()
            if val > best_val:
                best_val = val
                best_move = move
    else:
        best_val = float('inf')
        for move in board.legal_moves:
            board.push(move)
            val = minimax(board, depth - 1, -float('inf'), float('inf'), True)
            board.pop()
            if val < best_val:
                best_val = val
                best_move = move
                
    if not best_move and list(board.legal_moves):
        best_move = random.choice(list(board.legal_moves))
        
    return best_move

def get_ai_move(board, difficulty):
    if difficulty == "Easy":
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None
    elif difficulty == "Medium":
        return get_best_move(board, 2)
    elif difficulty == "Hard":
        return get_best_move(board, 3)
    elif difficulty == "Extremely Hard":
        try:
            import chess.engine
            with chess.engine.SimpleEngine.popen_uci("stockfish") as engine:
                result = engine.play(board, chess.engine.Limit(time=1.0))
                return result.move
        except Exception:
            return get_best_move(board, 4)
