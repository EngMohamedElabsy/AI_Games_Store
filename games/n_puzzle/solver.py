import random
import heapq

class NPuzzleState:
    def __init__(self, board, n, g, h, parent=None, move=None):
        self.board = board
        self.n = n
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent
        self.move = move

    def __lt__(self, other):
        return self.f < other.f

def get_manhattan_distance(board, n):
    dist = 0
    for i, val in enumerate(board):
        if val == 0:
            continue
        target_r = (val - 1) // n
        target_c = (val - 1) % n
        r = i // n
        c = i % n
        dist += abs(target_r - r) + abs(target_c - c)
    return dist

def get_neighbors(state):
    neighbors = []
    zero_idx = state.board.index(0)
    r = zero_idx // state.n
    c = zero_idx % state.n
    
    moves = []
    if r > 0: moves.append((-1, 0)) # Up
    if r < state.n - 1: moves.append((1, 0)) # Down
    if c > 0: moves.append((0, -1)) # Left
    if c < state.n - 1: moves.append((0, 1)) # Right
    
    for dr, dc in moves:
        new_r, new_c = r + dr, c + dc
        new_idx = new_r * state.n + new_c
        new_board = list(state.board)
        new_board[zero_idx], new_board[new_idx] = new_board[new_idx], new_board[zero_idx]
        
        h = get_manhattan_distance(new_board, state.n)
        new_state = NPuzzleState(tuple(new_board), state.n, state.g + 1, h, state, new_idx)
        neighbors.append(new_state)
        
    return neighbors

def solve_n_puzzle(initial_board, n):
    start_state = NPuzzleState(tuple(initial_board), n, 0, get_manhattan_distance(initial_board, n))
    
    # Goal board: 1, 2, ..., n*n-1, 0
    goal_board = tuple(list(range(1, n*n)) + [0])
    
    open_set = []
    heapq.heappush(open_set, start_state)
    closed_set = set()
    
    while open_set:
        current_state = heapq.heappop(open_set)
        
        if current_state.board == goal_board:
            # Reconstruct path
            path = []
            while current_state.parent is not None:
                path.append(current_state.move)
                current_state = current_state.parent
            return path[::-1]
            
        closed_set.add(current_state.board)
        
        for neighbor in get_neighbors(current_state):
            if neighbor.board in closed_set:
                continue
            heapq.heappush(open_set, neighbor)
            
    return []

def scramble_board(n, moves=50):
    board = list(range(1, n*n)) + [0]
    for _ in range(moves):
        zero_idx = board.index(0)
        r = zero_idx // n
        c = zero_idx % n
        
        possible_moves = []
        if r > 0: possible_moves.append(zero_idx - n)
        if r < n - 1: possible_moves.append(zero_idx + n)
        if c > 0: possible_moves.append(zero_idx - 1)
        if c < n - 1: possible_moves.append(zero_idx + 1)
        
        swap_idx = random.choice(possible_moves)
        board[zero_idx], board[swap_idx] = board[swap_idx], board[zero_idx]
        
    return board
