## ♟️ Chess Engine Setup (UCI Compatible)

To keep this repository lightweight and cross-platform friendly, pre-compiled chess engines (like Stockfish or Leela Chess Zero) are **not bundled** with the source code. 

You will need to download a UCI-compatible engine of your choice and configure it locally to use the engine analysis and AI opponent features.

### Step 1: Download an Engine
We recommend using either Stockfish (traditional CPU-based) or LC0 (Neural Network-based). Both are free, open-source, and natively support the UCI protocol used by this GUI.

*   **[Stockfish (Recommended)](https://stockfishchess.org/download/)**: Highly optimized, incredibly strong, and easy to set up on any computer. Download the version that matches your operating system.
*   **[Leela Chess Zero (Lc0)](https://lczero.org/play/download/)**: A neural network-based engine. Recommended if you have a dedicated GPU for faster evaluation.

### Step 2: Installation & Configuration
1. Download and extract the engine archive to your local machine.
2. Locate the executable file (e.g., `stockfish-windows-x86-64-avx2.exe` on Windows or `stockfish` on macOS/Linux).
3. Place the executable file into the `model/Stockfish/` directory (or any preferred folder) within this project.
4. Launch the Chess GUI. 
5. *(If applicable)* Go to the GUI settings/engine configuration menu and select the path to your downloaded engine executable.

> **Note:** Ensure you have the necessary execution permissions for the engine file if you are running this on macOS or Linux (`chmod +x stockfish`).