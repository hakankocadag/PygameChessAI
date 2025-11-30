import pygame
import textwrap
import os
import copy
import sys


# === 1. ANNOTATIONS & COORDINATE UTILITIES ===

def file_to_col(file):
    return ord(file.lower()) - ord('a')


def col_to_file(col):
    return chr(col + ord('a'))


def rank_to_row(rank):
    return 8 - int(rank)


def row_to_rank(row):
    return str(8 - row)


def format_move(start_pos, end_pos, piece):
    """Formats a move for history: 'wP e2 to e4'."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    move_str = f"{piece} {col_to_file(start_col)}{row_to_rank(start_row)} to {col_to_file(end_col)}{row_to_rank(end_row)}"
    return move_str


# === 2. KING SAFETY & PATH VALIDATION ===

def in_bounds(r, c):
    """Checks if a given row and column are within the board boundaries."""
    return 0 <= r < 8 and 0 <= c < 8


def is_path_clear(board, start, end):
    """Checks if the path between start and end (exclusive) is empty."""
    r1, c1 = start
    r2, c2 = end

    dr = (r2 - r1) // max(1, abs(r2 - r1)) if r1 != r2 else 0
    dc = (c2 - c1) // max(1, abs(c2 - c1)) if c1 != c2 else 0

    r, c = r1 + dr, c1 + dc

    while (r, c) != (r2, c2):
        if board[r][c] != '':
            return False
        r += dr
        c += dc
    return True


def find_king(board, turn):
    """Finds the (r, c) position of the King for the given color."""
    if not turn:
        return None
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == turn + 'K':
                return r, c
    return None


def check_linear_attack(board, r, c, directions, target_piece):
    """Checks for attack along a line (Rook, Bishop, Queen)."""
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            piece = board[nr][nc]
            if piece != '':
                if piece == target_piece:
                    return True
                break
            nr += dr
            nc += dc
    return False


# Dedicated attack check functions (used by is_square_attacked and check_kings_safety)
def check_king_attack(board, r, c, enemy_king):
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0: continue
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and board[nr][nc] == enemy_king:
                return True
    return False


def check_knight_attack(board, r, c, enemy_knight):
    for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and board[nr][nc] == enemy_knight:
            return True
    return False


def check_pawn_attack(board, r, c, enemy_pawn):
    direction = -1 if enemy_pawn[0] == 'b' else 1
    for dc in [-1, 1]:
        nr, nc = r + direction, c + dc
        if in_bounds(nr, nc) and board[nr][nc] == enemy_pawn:
            return True
    return False


def check_rook_attack(board, r, c, enemy_rook):
    return check_linear_attack(board, r, c, [(1, 0), (-1, 0), (0, 1), (0, -1)], enemy_rook)


def check_bishop_attack(board, r, c, enemy_bishop):
    return check_linear_attack(board, r, c, [(1, 1), (1, -1), (-1, 1), (-1, -1)], enemy_bishop)


def check_queen_attack(board, r, c, enemy_queen):
    return check_linear_attack(board, r, c, [(1, 0), (-1, 0), (0, 1), (0, -1),
                                             (1, 1), (1, -1), (-1, 1), (-1, -1)], enemy_queen)


def is_square_attacked(board, square, attacker_color):
    """
    Checks if a square is attacked by any piece of the attacker_color.
    This consolidated function uses the dedicated attack checks.
    """
    r_target, c_target = square

    # Define enemy pieces to look for
    opponent_pieces = {
        'P': attacker_color + 'P', 'N': attacker_color + 'N', 'B': attacker_color + 'B',
        'R': attacker_color + 'R', 'Q': attacker_color + 'Q', 'K': attacker_color + 'K'
    }

    # Iterate through all squares to find attacking pieces
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if not piece or piece[0] != attacker_color:
                continue

            piece_type = piece[1]
            enemy_piece_str = opponent_pieces[piece_type]

            # Temporarily replace the target square's content with the piece we're checking
            # This is crucial for *move* validation, but here we just check attack from a fixed piece.
            # We must use the piece's move logic: can the piece at (r, c) move to (r_target, c_target)?

            # Since the user's logic relies on the complex attack checks:
            if piece_type == 'P':
                # Pawn attacks are directional, so we check if the target square is a capture square
                direction = -1 if attacker_color == 'w' else 1
                if r_target == r + direction and abs(c_target - c) == 1:
                    return True
            elif piece_type == 'N':
                if abs(r_target - r) in [1, 2] and abs(c_target - c) in [1, 2] and abs(r_target - r) != abs(
                        c_target - c):
                    return True
            # For linear pieces, we use the specific attack checks which handle path clearance
            # by pretending the target square holds the piece we want to check safety for (a weak point).
            # A simpler way is to check if is_legal_move_basic(board, (r,c), (r_target, c_target), attacker_color) is True
            # For correctness, we will use the dedicated check functions which are proven to work:

            # The most accurate method for attack is to check if the attacker can move to the target:
            if is_legal_move_basic(board, (r, c), (r_target, c_target), attacker_color):
                return True

    return False


def is_king_in_check(board, king_color):
    """Checks if the king of king_color is currently in check."""
    king_pos = find_king(board, king_color)
    if king_pos is None:
        return False

    attacker_color = 'w' if king_color == 'b' else 'b'

    # The most accurate check uses the target square and the attacker's color
    return is_square_attacked(board, king_pos, attacker_color)


def check_kings_safety(board):
    """Returns 'w' or 'b' if a king is in check, otherwise None."""
    if is_king_in_check(board, 'w'):
        return 'w'
    if is_king_in_check(board, 'b'):
        return 'b'
    return None


# === 3. PIECE MOVEMENT VALIDATION (BASIC GEOMETRY) ===

def is_legal_move_pawn(board, start, end, turn):
    r1, c1 = start
    r2, c2 = end
    direction = -1 if turn == 'w' else 1
    start_row = 6 if turn == 'w' else 1
    target = board[r2][c2]

    if c1 == c2:
        if r2 - r1 == direction and target == '':
            return True
        if r1 == start_row and r2 - r1 == 2 * direction and board[r1 + direction][c1] == '' and target == '':
            return True
    elif abs(c2 - c1) == 1 and r2 - r1 == direction and target != '' and target[0] != turn:
        return True
    return False


def is_legal_move_rook(board, start, end, turn):
    r1, c1 = start
    r2, c2 = end
    if r1 != r2 and c1 != c2:
        return False
    if not is_path_clear(board, start, end):
        return False
    target = board[r2][c2]
    return target == '' or target[0] != turn


def is_legal_move_bishop(board, start, end, turn):
    r1, c1 = start
    r2, c2 = end
    if abs(r2 - r1) != abs(c2 - c1):
        return False
    if not is_path_clear(board, start, end):
        return False
    target = board[r2][c2]
    return target == '' or target[0] != turn


def is_legal_move_queen(board, start, end, turn):
    return is_legal_move_rook(board, start, end, turn) or is_legal_move_bishop(board, start, end, turn)


def is_legal_move_knight(board, start, end, turn):
    r1, c1 = start
    r2, c2 = end
    knight_moves = {
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2)
    }
    if (r2 - r1, c2 - c1) not in knight_moves:
        return False
    target = board[r2][c2]
    return target == '' or target[0] != turn


def is_legal_move_king(board, start, end, turn):
    """Checks basic King move + ensures it does NOT move into check."""
    r1, c1 = start
    r2, c2 = end

    # Basic geometric move check
    if max(abs(r2 - r1), abs(c2 - c1)) > 1:
        return False

    piece = board[r1][c1]
    captured = board[r2][c2]

    # Check if moving onto your own piece (redundant, but keeping it safe)
    if captured != '' and captured[0] == turn:
        return False

    # Simulate the move
    board[r2][c2] = piece
    board[r1][c1] = ''

    # Check if the King is safe in the new position (using the opponent's color)
    opponent_color = 'b' if turn == 'w' else 'w'
    is_safe = not is_square_attacked(board, end, opponent_color)

    # Undo the move (Crucial Fix)
    board[r1][c1] = piece
    board[r2][c2] = captured

    return is_safe


def is_legal_move_basic(board, start, end, turn):
    """
    Consolidated function to check if a move is legal based on piece rules,
    but without the safety check, EXCEPT for the King's move which must
    always include safety checks.
    """
    r1, c1 = start
    r2, c2 = end
    if not (0 <= r1 < 8 and 0 <= c1 < 8 and 0 <= r2 < 8 and 0 <= c2 < 8):
        return False
    piece = board[r1][c1]
    if not piece or piece[0] != turn:
        return False
    target = board[r2][c2]
    if target != '' and target[0] == turn:
        return False
    if r1 == r2 and c1 == c2:
        return False

    piece_type = piece[1]

    # King's move must use its specialized function that includes safety
    if piece_type == 'K':
        return is_legal_move_king(board, start, end, turn)

        # All other pieces use the geometric checks
    if piece_type == 'P':
        return is_legal_move_pawn(board, start, end, turn)
    elif piece_type == 'R':
        return is_legal_move_rook(board, start, end, turn)
    elif piece_type == 'N':
        return is_legal_move_knight(board, start, end, turn)
    elif piece_type == 'B':
        return is_legal_move_bishop(board, start, end, turn)
    elif piece_type == 'Q':
        return is_legal_move_queen(board, start, end, turn)

    return False


is_legal_move = is_legal_move_basic  # Alias used in AI functions


# === 4. GAME STATE & MOVE EXECUTION ===

def create_initial_board():
    board = [['' for _ in range(8)] for _ in range(8)]
    board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
    board[1] = ['bP'] * 8
    board[6] = ['wP'] * 8
    board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    return board


def switch_turn(turn):
    return 'b' if turn == 'w' else 'w'


def make_move(board, start, end, turn, move_history, captured_pieces):
    r1, c1 = start
    r2, c2 = end

    # 1. Basic legality check (including King safety via is_legal_move_king)
    if not is_legal_move_basic(board, start, end, turn):
        return False

    piece = board[r1][c1]
    captured = board[r2][c2]

    # 2. Temporarily make the move (if King, it's already done in is_legal_move_king,
    # but we must do it here for all other pieces)
    board[r2][c2] = piece
    board[r1][c1] = ''

    # 3. Check if this move *exposes* a check on the King
    if is_king_in_check(board, turn):
        # Undo move if it leaves king in check
        board[r1][c1] = piece
        board[r2][c2] = captured
        return False

    # 4. Finalize move
    if captured:
        opponent = 'w' if turn == 'b' else 'b'
        captured_pieces[opponent].append(captured)

    move_history.append(format_move(start, end, piece))
    return True


# === 5. AI (NEGAMAX) LOGIC ===

piece_values = {'wP': 100, 'wN': 300, 'wB': 330, 'wR': 500, 'wQ': 900, 'wK': 0,
                'bP': -100, 'bN': -300, 'bB': -330, 'bR': -500, 'bQ': -900, 'bK': 0}


def make_possible_move(board, start, end):
    """Creates a new board state after executing a move."""
    new_board = [row[:] for row in board]
    (r1, c1), (r2, c2) = start, end
    piece = new_board[r1][c1]

    new_board[r2][c2] = piece
    new_board[r1][c1] = ''

    return new_board


def all_moves(board, color):
    """Returns all legal and SAFE moves for given color (1=w, -1=b)."""
    moves = []
    piece_color = 'w' if color == 1 else 'b'

    for r1 in range(8):
        for c1 in range(8):
            piece = board[r1][c1]
            if piece and piece.startswith(piece_color):
                for r2 in range(8):
                    for c2 in range(8):
                        move = ((r1, c1), (r2, c2))

                        # Use the top-level move check (is_legal_move_basic)
                        if is_legal_move_basic(board, (r1, c1), (r2, c2), piece_color):

                            temp_board = make_possible_move(board, (r1, c1), (r2, c2))

                            # King Safety Check: The move must not leave the King in check
                            if not is_king_in_check(temp_board, piece_color):
                                moves.append(move)
    return moves


def game_over(board, color):
    """Returns True if the current player has no legal moves."""
    return not all_moves(board, color)


def piece_val_score(board_state):
    score = 0
    for row in board_state:
        for square in row:
            if square != '':
                score += piece_values.get(square, 0)
    return score


def king_safety_score(board_state, color):
    king = "wK" if color == 1 else "bK"
    score = 0
    for row in range(len(board_state)):
        for column in range(len(board_state[row])):
            if board_state[row][column] == king:
                if 3 <= row <= 6:
                    score -= 20
    return score


def evaluate(board_state, color):
    score = color * piece_val_score(board_state) + king_safety_score(board_state, color)
    return score


def negamax(board, depth, alpha, beta, color):
    if depth == 0 or game_over(board, color):
        return evaluate(board, color)

    max_score = -float('inf')
    for move in all_moves(board, color):
        next_board = make_possible_move(board, move[0], move[1])
        score = -negamax(next_board, depth - 1, -beta, -alpha, -color)

        max_score = max(max_score, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return max_score


def bot_plays(board, depth, color):
    best_score = -float('inf')
    best_move = None
    alpha = -float('inf')
    beta = float('inf')

    for move in all_moves(board, color):
        new_board = make_possible_move(board, move[0], move[1])
        score = -negamax(new_board, depth - 1, -beta, -alpha, -color)

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best_move

# === 6. PYGAME GRAPHICS & MAIN LOOP ===

def load_images(tile_size):
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    images = {}

    base_path = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
    images_dir = os.path.join(base_path, "images")
    if not os.path.isdir(images_dir):
        images_dir = os.path.join(os.getcwd(), "images")

    for piece in pieces:
        path = os.path.join(images_dir, f"{piece}.png")
        try:
            image = pygame.image.load(path)
            images[piece] = pygame.transform.scale(image, (tile_size, tile_size))
        except pygame.error:
            # Placeholder for missing images
            pass
    return images


def render_wrapped_text(lines, x, y, max_width, font, color):
    if isinstance(lines, str):
        lines = textwrap.wrap(lines, width=30)
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x, y + i * text_surface.get_height()))


def Draw_board(light_color, dark_color, meow_mode, piece_images, font):
    board_start_x = LABEL_MARGIN
    board_start_y = 10

    danger = check_kings_safety(board)
    king_in_check_pos = find_king(board, danger) if danger else None

    for row in range(8):
        for col in range(8):
            color = light_color if (row + col) % 2 == 0 else dark_color
            x = board_start_x + col * TILE_SIZE
            y = board_start_y + row * TILE_SIZE

            if king_in_check_pos == (row, col):
                pygame.draw.rect(screen, 'firebrick1', [x, y, TILE_SIZE, TILE_SIZE])
            elif (row, col) == move_start:
                pygame.draw.rect(screen, 'yellow', [x, y, TILE_SIZE, TILE_SIZE])
            else:
                pygame.draw.rect(screen, color, [x, y, TILE_SIZE, TILE_SIZE])

            pygame.draw.rect(screen, 'black', [x, y, TILE_SIZE, TILE_SIZE], 1)
            piece = board[row][col]
            if piece in piece_images:
                screen.blit(piece_images[piece], (x, y))

    pygame.draw.rect(screen, 'black', [board_start_x, board_start_y, BOARD_WIDTH, BOARD_HEIGHT], 4)

    # === Side Panel ===
    panel_x = board_start_x + BOARD_WIDTH + 20
    panel_y = board_start_y
    panel_width = WIDTH - panel_x - 20
    panel_height = BOARD_HEIGHT

    pygame.draw.rect(screen, dark_color, [panel_x - 10, panel_y, panel_width, panel_height])
    pygame.draw.rect(screen, 'black', [panel_x - 10, panel_y, panel_width, panel_height], 4)

    # Draw Restart Button
    button_width = 180
    button_height = 50
    button_x = panel_x + (panel_width - button_width) // 2
    button_y = panel_y + panel_height - button_height - 20
    global restart_rect
    restart_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if restart_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, 'darkblue', restart_rect)
    else:
        pygame.draw.rect(screen, 'lightblue', restart_rect)

    restart_text = big_font.render("Click to Restart", True, 'black')
    screen.blit(restart_text, (button_x + 10, button_y + 15))

    # Status Messages
    if danger == 'w':
        status_msg = "White king is in check!"
    elif danger == 'b':
        status_msg = "Black king is in check!"
    else:
        status_msg = "  `\\_(^-^)_/`  "

    lines = [f"Turn: {'White' if turn == 'w' else 'Black'}", status_msg, "Press C to change theme"]
    render_wrapped_text(lines, panel_x, 20, panel_width - 20, big_font, 'black')

    # Draw Move History
    font_small = pygame.font.SysFont(None, 24)
    for i, move in enumerate(move_history[-10:]):
        piece_type = move.split()[0]
        color_text = pygame.Color("white") if piece_type.startswith("w") else pygame.Color("black")
        text = font_small.render(move, True, color_text)
        screen.blit(text, (BOARD_WIDTH + 40, 100 + i * 20))

    # Draw Game Over Banner
    if game_ended:
        shadow_offset = 3
        center_x = board_start_x + BOARD_WIDTH // 2
        center_y = board_start_y + BOARD_HEIGHT // 2

        shadow = giant_font.render(winner_text, True, 'black')
        shadow_rect = shadow.get_rect(center=(center_x + shadow_offset, center_y + shadow_offset))
        screen.blit(shadow, shadow_rect)

        msg = giant_font.render(winner_text, True, 'red')
        msg_rect = msg.get_rect(center=(center_x, center_y))
        screen.blit(msg, msg_rect)

    # Draw Board Coordinates (Ranks and Files)
    font_coords = pygame.font.SysFont(None, 24)
    for col in range(8):
        letter = chr(97 + col)
        text = font_coords.render(letter, True, 'black')
        x = board_start_x + col * TILE_SIZE + TILE_SIZE // 2 - text.get_width() // 2
        y = board_start_y + TILE_SIZE * 8 + 5
        screen.blit(text, (x, y))

    for row in range(8):
        number = str(8 - row)
        text = font_coords.render(number, True, 'black')
        x = board_start_x - text.get_width() - 5
        y = board_start_y + row * TILE_SIZE + TILE_SIZE // 2 - text.get_height() // 2
        screen.blit(text, (x, y))


def has_legal_moves(board, turn):
    color = 1 if turn == 'w' else -1
    return len(all_moves(board, color)) > 0


def check_game_end(board, current_turn):
    global winner_text
    white_king_present = find_king(board, 'w') is not None
    black_king_present = find_king(board, 'b') is not None

    if not white_king_present:
        winner_text = "Black wins (King Capture)!"
        return True
    elif not black_king_present:
        winner_text = "White wins (King Capture)!"
        return True

    if not has_legal_moves(board, current_turn):
        if is_king_in_check(board, current_turn):
            winner = 'White' if current_turn == 'b' else 'Black'
            winner_text = f"Checkmate! {winner} wins!"
        else:
            winner_text = "Stalemate!"
        return True

    return False


# === Initialization ===
TILE_SIZE = 75
LABEL_MARGIN = 24
BOARD_WIDTH = TILE_SIZE * 8
BOARD_HEIGHT = TILE_SIZE * 8
WIDTH = BOARD_WIDTH + 300 + LABEL_MARGIN * 2
HEIGHT = BOARD_HEIGHT + LABEL_MARGIN * 2

pygame.init()
pygame.display.set_caption('BEST CHESS GAME EVER!')
screen = pygame.display.set_mode([WIDTH, HEIGHT])
font = pygame.font.SysFont('arial', 20)
giant_font = pygame.font.SysFont('arial', 50)
big_font = pygame.font.SysFont('arial', 20)
timer = pygame.time.Clock()
fps = 60
piece_images = load_images(TILE_SIZE)

board_themes = [
    ('burlywood', 'sienna'), ('azure', 'darkorange'), ('whitesmoke', 'crimson'),
    ('lemonchiffon', 'mediumvioletred'), ('peachpuff', 'steelblue'),
    ('lightgoldenrodyellow', 'darkcyan'), ('antiquewhite', 'teal'),
    ('seashell', 'firebrick'), ('tan', 'darkgreen'), ('wheat', 'darkslateblue'),
    ('papayawhip', 'darkolivegreen'),
]

# Game State Variables
board = create_initial_board()
turn = 'w'
game_fsm_state = "select"
move_start = None
game_ended = False
move_history = []
captured_pieces = {'w': [], 'b': []}
meow_mode = False
typed_keys = ''
meow_timer = 0
current_theme = 0
restart_rect = pygame.Rect(0, 0, 0, 0)
winner_text = ''

# AI Setup
ai_color = 'b'
human_color = 'w'
AI_DEPTH = 3

# === Main Game Loop ===
run = True
while run:
    timer.tick(fps)
    screen.fill('white')
    light_tile, dark_tile = board_themes[current_theme]
    Draw_board(light_tile, dark_tile, meow_mode, piece_images, font)

    if meow_mode:
        meow_timer += 1
        if meow_timer % 10 == 0:
            current_theme = (current_theme + 1) % len(board_themes)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if not meow_mode:
                typed_keys += event.unicode.lower()
                typed_keys = typed_keys[-4:]
                if typed_keys == 'cats':
                    meow_mode = True
            if event.key == pygame.K_c and not meow_mode:
                current_theme = (current_theme + 1) % len(board_themes)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # 1. Restart Button Click
            if restart_rect.collidepoint(x, y):
                board = create_initial_board()
                turn = 'w'
                game_fsm_state = "select"
                move_start = None
                game_ended = False
                move_history = []
                captured_pieces = {'w': [], 'b': []}
                winner_text = ''
                continue

            # 2. Board Click
            if not game_ended and turn == human_color:
                board_start_x = LABEL_MARGIN
                board_start_y = 10

                col = (x - board_start_x) // TILE_SIZE
                row = (y - board_start_y) // TILE_SIZE

                if 0 <= row < 8 and 0 <= col < 8:
                    if game_fsm_state == "select":
                        if board[row][col].startswith(turn):
                            move_start = (row, col)
                            game_fsm_state = "move"
                    elif game_fsm_state == "move":
                        move_end = (row, col)

                        if make_move(board, move_start, move_end, turn, move_history, captured_pieces):
                            if check_game_end(board, switch_turn(turn)):
                                game_ended = True
                            turn = switch_turn(turn)

                        game_fsm_state = "select"
                        move_start = None
                        move_end = None

    # === AI TURN ===
    if not game_ended and turn == ai_color:

        Draw_board(light_tile, dark_tile, meow_mode, piece_images, font)
        pygame.display.flip()

        pygame.time.delay(1000)

        color_ai_int = 1 if ai_color == 'w' else -1
        best_move = bot_plays(board, depth=AI_DEPTH, color=color_ai_int)

        if best_move:
            start, end = best_move
            if make_move(board, start, end, turn, move_history, captured_pieces):
                if check_game_end(board, switch_turn(turn)):
                    game_ended = True
                turn = switch_turn(turn)
            # No 'else' needed; AI moves should always be legal due to all_moves() filter
        else:
            # Should only happen if check_game_end missed a terminal state
            game_ended = True

    pygame.display.flip()

pygame.quit()