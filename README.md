# ♟️ PyChess GUI: Advanced Desktop Chess Application

A full-featured, cross-platform desktop chess application built with Python and PyQt5. 

Developed with the domain expertise of a competitive chess player (USCF 1997), this project goes beyond a simple board representation. It features robust PGN parsing, game analysis, and seamless integration with standard UCI (Universal Chess Interface) engines like Stockfish.

## ✨ Key Features
*   **Intuitive Graphical Interface**: Built with PyQt5 for a responsive, native desktop experience.
*   **Player vs. Computer**: Play against world-class chess engines with adjustable difficulty levels.
*   **UCI Engine Integration**: Standardized communication with any UCI-compatible engine for real-time position evaluation and automated post-game analysis.
*   **PGN Management**: Import and export standard Portable Game Notation (PGN) files for game recording, sharing, and reviewing past matches.
*   **Performance Metrics**: Visualize game statistics, move accuracy, and evaluation graphs.

## 🛠️ Technology Stack
*   **Language**: Python 3
*   **GUI Framework**: PyQt5
*   **Chess Logic**: `python-chess` library
*   **Architecture**: Object-Oriented Design, MVC pattern (Model-View-Controller)

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/lunat1st/ChessGUI.git](https://github.com/lunat1st/ChessGUI.git)
cd ChessGUI
```

**2. Install dependencies**
It is recommended to use a virtual environment:
```bash
pip install -r requirements.txt
```

**3. Configure the Chess Engine**
To use the AI opponent and analysis features, you must provide a UCI-compatible engine. Pre-compiled engines are **not** bundled with this repository. 
👉 **Please refer to `model/README.md` for download links and setup instructions.**

**4. Run the application**
```bash
python main.py
```

## 📸 Screenshots
*(Note: Replace these placeholder links with actual screenshots of your GUI)*
*   [Gameplay Interface](./assets/screenshot1.png)
*   [Post-game Analysis Dashboard](./assets/screenshot2.png)