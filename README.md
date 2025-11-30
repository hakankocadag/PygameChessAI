# ♟️ Discrete Structures-Based Chess AI (Pygame)

This repository contains a complete, single-file implementation of a fully functional chess game with a Graphical User Interface (GUI) and an AI opponent. It was developed as a course project at Erciyes University, demonstrating how **Discrete Structures** concepts can be applied to real-world programming problems.

The project highlights the practical use of several computer science concepts:

* **Matrices (2D Arrays):** Representing the chessboard and tracking piece positions.  
* **Game Trees & Recursion:** Implemented in the AI using the Negamax algorithm.  
* **Finite State Machines (FSM):** Managing the game loop and player interactions, including piece selection and moves.  
* **Boolean Logic & Set Theory:** Core to validating moves, detecting checks, and handling checkmate scenarios.  

---

## 🛠️ Technical Core and Implementation

### Game Engine & AI

* **Language & GUI:** The project is entirely developed in **Python** with **Pygame** providing the interactive interface.  
* **AI Algorithm:** The computer opponent uses the **Negamax algorithm** with **Alpha-Beta Pruning** to efficiently search the game tree and select optimal moves.  
* **Board Representation:** The chessboard is an 8x8 matrix, making it straightforward to update positions and manage piece movement.

### My Contribution: Move Validation (Hakan Kocadağ)

As the **Move Validation Specialist**, I focused on building a robust system to enforce the rules of chess:

* **Modular Validation:** Created separate functions for each piece type (Pawn, Rook, Knight, Bishop, Queen, King).  
* **Path Clearance:** Developed the `is_path_clear` function to ensure sliding pieces cannot move through obstacles.  
* **Rule Enforcement:** Ensured all geometric and logical rules of chess are properly implemented, demonstrating practical use of discrete mathematics principles.

---

## 👥 Team & Roles

The project was developed by a team of students under the guidance of **Asst. Prof. Fatih Sarıkoç**. Each member contributed a specific part to ensure the project’s success:

| Team Member | Core Responsibility | Role |
| :--- | :--- | :--- |
| **Sude Kaya** | AI opponent (Negamax, Evaluation, Alpha-Beta Pruning) & project management | AI Developer / Team Leader |
| **Hakan Kocadağ** | Validating chess moves, ensuring piece geometry and path clearance | Move Validation Specialist |
| **Zehra Yavuzer** | Check and checkmate logic, king safety detection | Checkmate Logic Specialist |
| **Shafiqullah Qaweem** | Board representation, game state tracking | Game State Developer |
| **Mugahed Lahmar** | Implementing the game loop using FSM for player input and turn handling | Game Loop / FSM Developer |
| **Tarık Ömer Tatlı** | Building the GUI with Pygame | GUI Developer |

---

## ⚙️ Setup & Running the Game

### Requirements

* Python 3.x  
* Pygame library  

### Instructions

1. **Clone the Repository:**
    ```bash
    git clone [YOUR_REPOSITORY_URL]
    cd [YOUR_REPOSITORY_NAME]
    ```
2. **Install Pygame:**
    ```bash
    pip install pygame
    ```
3. **Verify Images:** Make sure the `images/` folder contains all 12 chess piece images (`wK.png`, `bP.png`, etc.).  
4. **Run the Game:**
    ```bash
    python ChessAI.py
    ```
