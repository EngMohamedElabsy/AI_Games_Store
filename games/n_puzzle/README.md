# N-Puzzle AI Solver: A* Search Algorithm

This document explains the AI algorithm used to solve the N-Puzzle game in this project.

## The Algorithm: A* Search

The N-Puzzle is solved using the **A* (A-Star) Search Algorithm**. A* is an informed search algorithm, meaning it uses a heuristic to guide its search, making it much more efficient than blind search algorithms like BFS or DFS.

### How A* Works

A* selects the path that minimizes the function:
**f(n) = g(n) + h(n)**

- **g(n)**: The exact cost to reach node `n` from the starting node (in this case, the number of moves made so far).
- **h(n)**: The estimated cost (heuristic) from node `n` to the goal node.

For A* to be optimal, the heuristic `h(n)` must be *admissible*, meaning it never overestimates the true cost to reach the goal.

### The Heuristic: Manhattan Distance

In our implementation, we use the **Manhattan Distance** heuristic. It calculates the sum of the horizontal and vertical distances of each tile from its current position to its goal position.

```python
def manhattan(state, n):
    dist = 0
    for i in range(n*n):
        val = state[i]
        if val != 0:
            target_r = (val - 1) // n
            target_c = (val - 1) % n
            curr_r = i // n
            curr_c = i % n
            dist += abs(target_r - curr_r) + abs(target_c - curr_c)
    return dist
```

### Implementation Details

The solver maintains a priority queue (min-heap) of states to explore, ordered by their `f(n)` values. It also uses a `visited` set to avoid revisiting the same board configurations and getting stuck in infinite loops.

```python
import heapq

def solve_npuzzle(board, n):
    goal = tuple(list(range(1, n*n)) + [0])
    start = tuple(board)
    
    # Priority Queue stores tuples of: (f(n), g(n), current_state, path_taken)
    pq = [(manhattan(start, n), 0, start, [])]
    visited = {start}
    
    while pq:
        f, g, state, path = heapq.heappop(pq)
        
        if state == goal:
            return path  # Solution found!
            
        # Generate valid moves and add them to the queue
        zero_idx = state.index(0)
        # ... logic to swap 0 with adjacent tiles (up, down, left, right)
        
        for move in valid_moves:
            new_state = apply_move(state, move)
            if new_state not in visited:
                visited.add(new_state)
                # Calculate new costs
                new_g = g + 1
                new_f = new_g + manhattan(new_state, n)
                heapq.heappush(pq, (new_f, new_g, new_state, path + [new_state]))
```

### Why A* for N-Puzzle?
A* is perfectly suited for the N-Puzzle because finding the absolute shortest sequence of moves is critical for an optimal solution. The Manhattan distance heuristic guarantees finding the shortest path while drastically reducing the number of states explored compared to uninformed searches.
