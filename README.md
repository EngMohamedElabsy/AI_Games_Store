# 🎮 AI Games Store

![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

**AI Games Store** is a modern, sleek desktop application built with Python and CustomTkinter. It serves as a unified hub for classic algorithm-driven games, allowing users to play manually or watch advanced Artificial Intelligence algorithms solve complex puzzles in real-time.

## ✨ Key Features

* **Premium Modern UI:** A beautiful, responsive dark-mode interface built with CustomTkinter. Features smooth animations, scalable vector-like graphics, and glassmorphism UI elements.
* **Smart Auto-Scaling:** Fully responsive boards. Press `F11` or use keyboard shortcuts (`Ctrl + Scroll` / `+` / `-`) to auto-fit and zoom the game boards perfectly to your screen size.
* **Intelligent Win System:** 
  * 🧠 **AI Win:** Displays a robotic overlay with futuristic calculation sound effects.
  * 🏆 **Human Win:** Displays a golden trophy with triumphant fanfare.
* **Custom Meme Sounds:** Add your own `AI Win.mp3` or `Human Win.mp3` to the `assets/sounds/` folder to personalize your victories!
* **Multi-threading:** AI solvers run in the background, keeping the UI smooth and responsive during heavy algorithm calculations.

---

## 🕹️ The Games Collection

### 1. ♟️ Advanced Chess Engine
Play a complete game of chess against a friend or a customizable AI Bot!
* **Aesthetics:** Uses the modern "Neo" premium piece set (inspired by Chess.com) with precise board coordinates.
* **Game Modes:** Human vs Human, Human vs Bot, Bot vs Human, and AI vs AI.
* **Dynamic AI IQ:** Set the Bot's "IQ" level dynamically to control its difficulty and minimax search depth.
* **Captured Pieces:** Displays captured pieces cleanly on the side, auto-sorted by their exact material value.

### 2. 🧩 N-Puzzle (Sliding Tile)
The classic 8-puzzle/15-puzzle game, dynamically scalable to any grid size ($N \times N$).
* **Auto-Scramble:** Instantly generates a solvable randomized board.
* **AI Solver:** Uses advanced pathfinding algorithms (like A* Search) to find the optimal solution and animates the tiles sliding to the correct positions step-by-step.
* **Audio Feedback:** Satisfying sliding sound effects for every move.

### 3. 👑 N-Queens Problem
A classic constraint satisfaction problem where the goal is to place $N$ queens on an $N \times N$ chessboard so that no two queens threaten each other.
* **Interactive Play:** Place queens manually. The board instantly highlights "Danger Zones" in red if a queen is threatened!
* **AI Solver:** Solves the N-Queens placement instantly using backtracking/optimization algorithms.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EngMohamedElabsy/AI_Games_Store.git
   cd AI_Games_Store
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🛠️ Packaging as Standalone App (.exe)

Want to share the game as a single Windows executable? We've made it easy!

1. Make sure you have **PyInstaller** installed (`pip install pyinstaller`).
2. Simply double-click on **`build.bat`** in the root directory.
3. The script will automatically compile the code, bundle the assets (icons and sounds), and generate a single file.
4. Once finished, you will find your game inside the **`dist/`** folder as `AI_Games_Store.exe`.

---

## 🎵 Customizing Your Experience

You can customize the winning sounds even in the compiled version:
1. Create an `assets/sounds/` folder next to your `AI_Games_Store.exe`.
2. Place your custom `AI Win.mp3` or `Human Win.mp3` files inside.
3. The game will automatically prioritize your files over the built-in sounds!

---

## 👨‍💻 Developer
**Eng. Mohamed Elabsy**
[GitHub Profile](https://github.com/EngMohamedElabsy)
