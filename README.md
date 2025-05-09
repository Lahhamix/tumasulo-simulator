# Tumasulo Simulator

A modern, interactive web-based simulator for Tomasulo's algorithm, featuring a step-by-step visualizer, performance metrics, and a beautiful UI.  
Developed by Clara & Hadi.

---

## 🚀 Project Overview

This project implements a full-featured simulator for Tomasulo's algorithm—a classic hardware algorithm for dynamic scheduling and out-of-order execution in CPUs. The simulator models all key components: register file, reservation stations, functional units, memory, and the common data bus (CDB). It provides both a Python backend and a modern web UI for interactive exploration and visualization.

**Key Features:**
- Step-by-step simulation with visual state updates
- Full simulation run with performance metrics (cycles, IPC, etc.)
- Upload or paste your own instruction traces
- Generate random traces for demo/testing
- Modern, responsive web UI with blue/yellow theme
- Visual display of registers, reservation stations, and CDB
- Metrics and simulation report display
- Reset and replay functionality

---

## 🗂️ Project Structure

```
.
├── components/         # Core hardware components (registers, memory, reservation stations, etc.)
├── utils/              # Utility modules (metrics, parser, config)
├── tests/              # Trace generation and sample traces
│   ├── generate_random_traces.py
│   └── sample_traces/
├── simulator.py        # Main Tomasulo simulator logic
├── web_api.py          # Flask web server and UI
└── README.md           # (You are here!)
```

---

## 🖥️ Requirements

- Python 3.8+
- pip

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd tumasulo_simulator
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install flask
   ```

   *(All other dependencies are from the Python standard library.)*

---

## ▶️ Running the Simulator

1. **Start the web server:**
   ```bash
   python web_api.py
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:5000/
   ```

3. **Using the UI:**
   - **Paste or upload** a trace file (see below for format).
   - Click **Run Simulation** for a full run and metrics.
   - Click **Start Step Simulation** to step through each cycle interactively.
   - Use **Next Step** and **Reset** as needed.
   - Click **Generate Random Traces** to create demo traces in `tests/sample_traces/`.

---

## 📝 Trace File Format

Each line is a single instruction. Supported instructions:
```
ADD R1, R2, R3
SUB R4, R5, R6
MUL R1, R2, R3
DIV R1, R2, R3
LOAD R1, 8(R2)
STORE 12(R3), R4
```
- Registers: R0–R7
- Offsets: integer values

---

## 🧩 Project Details

### **Backend (simulator.py)**
- Implements all stages of Tomasulo's algorithm: Issue, Execute, Write Result
- Models register file, reservation stations, functional units, memory, and CDB
- Supports both full-run (`run()`) and step-by-step (`run_step()`) simulation
- Collects and reports performance metrics (cycles, instructions, IPC, stalls, etc.)

### **Web UI (web_api.py)**
- Flask server renders a modern HTML/CSS/JS interface
- Interactive controls for uploading traces, running, stepping, and resetting
- Visualizes registers, reservation stations, and CDB in real time
- Displays simulation metrics and reports
- Blue/yellow color theme for clarity and accessibility

### **Trace Generation (tests/generate_random_traces.py)**
- Generates random, valid instruction traces for demo/testing
- Output files are saved in `tests/sample_traces/`

---

## 🧪 Testing & Demo

- Use the **Generate Random Traces** button in the UI, or run:
  ```bash
  python tests/generate_random_traces.py
  ```
- Sample traces will appear in `tests/sample_traces/`
- You can upload these via the web UI for instant simulation

---

## 👩‍💻 Authors

**Tumasulo Simulator - Clara & Hadi**

---

## 📄 License

This project is for educational and research purposes.

---

If you have any questions or want to contribute, feel free to open an issue or pull request! 