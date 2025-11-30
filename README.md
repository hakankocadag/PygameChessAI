# ♟️ Discrete Structures‑Based Chess AI (Pygame)

## 📌 Note about this Repository

This specific repository is a **refined, consolidated showcase version** of the final project code.  

The original, collaborative codebase—featuring multiple Python modules, separate commits by all team members, and the full development history—is hosted in the primary repository maintained by the team leader, **Sude Kaya**.  

This version has been formatted for **ease of individual running and modification**, making it simpler to explore the chess AI, experiment with move validation, or adapt it for personal learning projects.

## 📄 License / Usage Notice

This repository is a **showcase of the team project** developed by the chess AI team at Erciyes University, led by **Sude Kaya**.  

It is provided for **educational purposes only**. No part of the code should be copied, redistributed, or used for other projects without the **consent of the project team**.  

All credit for the original project and contributions goes to the entire team.

---

This repository contains a complete, single‑file implementation of a fully functional chess game with a graphical interface and an AI opponent. Developed as a course project at Erciyes University, this project showcases how fundamental concepts from **Discrete Structures** can be practically applied in programming.

The project brings together several important ideas from computer science:

* **Matrices (2D Arrays):** Using an 8×8 matrix to represent the chessboard and manage piece positions.  
* **Game Trees & Recursion:** The AI opponent relies on the **Negamax algorithm** (with alpha‑beta pruning) to search move trees and choose optimal moves.  
* **Finite State Machine (FSM):** Underlies the game loop to handle player interactions: selecting pieces, moving them, turn switching.  
* **Boolean Logic & Set Theory:** Used heavily in move validation and check/checkmate detection, encoding chess rules in logical and set‑based form.

---

## 📚 Table of Contents

- [Technical Core & Implementation](#-technical-core--implementation)  
- [My Contribution — Move Validation](#-my-contribution--move-validation)  
- [Team & Roles](#-team--roles)  
- [Setup & Running the Game](#-setup--running-the-game)  
- [What You Get / Features](#-what-you-get--features)  
- [Credits & License](#-credits--license)

---

## 🛠️ Technical Core & Implementation

### Game Engine & AI  
* **Language & GUI:** Written entirely in **Python**, using **Pygame** for rendering and user interaction.  
* **AI:** The computer player executes the **Negamax algorithm** with **Alpha-Beta Pruning** to efficiently evaluate the game tree and select strong moves.  
* **Board Representation:** The chessboard is stored as an 8×8 matrix, which simplifies tracking piece positions, movement, captures, and state updates.

---

## ✅ My Contribution — Move Validation (Hakan Kocadağ)  
As the **Move Validation Specialist**, I designed and implemented the core system that ensures all chess moves follow the official geometric and logical rules:

* **Per‑piece Validation:** Separate functions handle move logic for each type of piece (Pawn, Rook, Knight, Bishop, Queen, King).  
* **Path Clearance:** For sliding pieces (Rook, Bishop, Queen), I implemented an `is_path_clear` check to ensure they cannot jump over other pieces.  
* **Rule Enforcement:** The validation logic rigorously follows the rules derived from discrete mathematics, covering movement, captures, check/checkmate conditions, and special moves as needed.

---

## 👥 Team & Roles  

The project was developed by a team of students under the guidance of **Asst. Prof. Fatih Sarıkoç**. Each member handled a specific responsibility to bring the project together:

| Team Member | Responsibility | Role |
|-------------|----------------|------|
| **Sude Kaya** | AI Chess Opponent (Negamax, evaluation, alpha-beta pruning) & Project Management | AI Developer / Team Leader |  
| **Hakan Kocadağ** (me) | Move validation, piece geometry, path clearance | Move Validation Specialist |  
| **Zehra Yavuzer** | Check / Checkmate logic, king safety detection | Checkmate Logic Specialist |  
| **Shafiqullah Qaweem** | Board representation, game state tracking (turn, pieces, history) | Game State Developer |  
| **Mugahed Lahmar** | Main game loop & FSM for player input and turns | Game Loop / FSM Developer |  
| **Tarık Ömer Tatlı** | Graphical User Interface (GUI) implementation using Pygame | GUI Developer |  

---

## ⚙️ Setup & Running the Game  

### Requirements  
* Python 3.x  
* Pygame library  

### How to Run  

```bash
git clone https://github.com/hakankocadag/PygameChessAI  
cd PygameChessAI  

pip install pygame  

python ChessAI.py
