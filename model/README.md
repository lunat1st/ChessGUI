# 🧠 Chess Engines Directory

This directory serves as the designated location for UCI-compatible chess engines utilized by the application. 

To maintain a lightweight and cross-platform repository, large compiled binaries (such as `.exe` files) are **not included** in version control. 

### How to Setup the Engine:

**1. Download a UCI Engine**
We highly recommend using one of the following open-source engines:
*   **[Stockfish](https://stockfishchess.org/download/)**: The strongest traditional CPU-based engine. Recommended for most users. Download the version corresponding to your OS (e.g., Windows AVX2).
*   **[Leela Chess Zero (Lc0)](https://lczero.org/play/download/)**: A neural network-based engine (GPU recommended).

**2. Place the Executable**
Extract the downloaded archive and move the engine executable file directly into this `model/` folder. 
*   *Windows example*: `model/stockfish-windows-x86-64-avx2.exe`
*   *macOS/Linux example*: `model/stockfish`

**3. Verify Permissions (macOS/Linux only)**
Ensure the engine file has executable permissions:
```bash
chmod +x model/stockfish
```

Once the engine is placed here, the application will automatically detect and integrate it for gameplay and analysis.