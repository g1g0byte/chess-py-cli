import re
from dataclasses import dataclass
from typing import Optional, Self
from enum import Enum


@dataclass
class Position:
    x: int
    y: int


class Colour(Enum):
    WHITE = "white"
    BLACK = "black"


class MoveType(Enum):
    NORMAL = "normal"
    CASTLE = "castle"
    PROMOTION = "promotion"


# TODO stop pawning capturing in front and only to the sides
class Piece:
    def __init__(self, position: Position, colour: Colour) -> None:
        self.position = position
        self.colour = colour

    def valid_move(
        self, board: list[list[Optional[Self]]], move_x_pos: int, move_y_pos: int
    ) -> bool:
        if not self.can_move_to(move_x_pos, move_y_pos):
            return False

        piece: Optional[Piece] = board[move_y_pos][move_x_pos]
        if piece != None and piece.colour == self.colour:
            return False

        return True


class Pawn(Piece):
    value: int = 1
    print: str = ""
    max_move: int = 2

    def __init__(self, position: Position, colour: Colour) -> None:
        super().__init__(position, colour)
        if colour == Colour.WHITE:
            self.print = "P"
        else:
            self.print = "p"

    def can_move_to(self, move_x_pos: int, move_y_pos: int, is_capture: bool) -> bool:
        x_move_distance: int = abs(self.position.x - move_x_pos)
        y_move_distance: int = abs(self.position.y - move_y_pos)

        if is_capture:
            if x_move_distance == 1 and y_move_distance == 1:
                return True
        else:
            if x_move_distance < 1 and y_move_distance <= self.max_move:
                return True

        return False

    def valid_move(
        self, board: list[list[Optional[Piece]]], move_x_pos: int, move_y_pos: int
    ) -> bool:
        is_capture: bool = get_if_capture(
            board, Position(move_x_pos, move_y_pos), self.colour
        )
        if not self.can_move_to(move_x_pos, move_y_pos, is_capture):
            return False

        piece: Optional[Piece] = board[move_y_pos][move_x_pos]
        if piece != None and piece.colour == self.colour:
            return False

        return True


class Bishop(Piece):
    value: int = 3
    print: str = ""

    def __init__(self, position: Position, colour: Colour) -> None:
        super().__init__(position, colour)
        if colour == Colour.WHITE:
            self.print = "B"
        else:
            self.print = "b"

    def can_move_to(self: Piece, move_x_pos: int, move_y_pos: int) -> bool:
        x_direction_is_right: bool = move_x_pos - self.position.x >= 0
        y_direction_is_up: bool = move_y_pos - self.position.y >= 0
        x_move_distance: int = abs(self.position.x - move_x_pos)

        check_x_pos: int = self.position.x
        check_y_pos: int = self.position.y
        for _ in range(x_move_distance):
            if x_direction_is_right:
                check_x_pos += 1
            else:
                check_x_pos -= 1

            if y_direction_is_up:
                check_y_pos += 1
            else:
                check_y_pos -= 1

            if check_x_pos == move_x_pos and check_y_pos == move_y_pos:
                return True

        return False


class Knight(Piece):
    value: int = 3
    print: str = ""
    max_x_move: int = 2
    max_y_move: int = 2

    def __init__(self, position: Position, colour: Colour) -> None:
        super().__init__(position, colour)
        if colour == Colour.WHITE:
            self.print = "N"
        else:
            self.print = "n"

    def can_move_to(self, move_x_pos: int, move_y_pos: int) -> bool:
        x_move_distance: int = abs(self.position.x - move_x_pos)
        y_move_distance: int = abs(self.position.y - move_y_pos)

        print(x_move_distance, y_move_distance)

        if (x_move_distance == 2 and y_move_distance == 1) or (
            x_move_distance == 1 and y_move_distance == 2
        ):
            return True
        else:
            return False


class Rook(Piece):
    value: int = 5
    print: str = ""

    def __init__(self, position: Position, colour: Colour) -> None:
        super().__init__(position, colour)
        if colour == Colour.WHITE:
            self.print = "R"
        else:
            self.print = "r"

    def can_move_to(self: Piece, move_x_pos: int, move_y_pos: int) -> bool:
        moved_along_x: bool = abs(self.position.x - move_x_pos) > 0
        moved_along_y: bool = abs(self.position.y - move_y_pos) > 0

        # xor comparison
        if moved_along_x ^ moved_along_y:
            return True
        else:
            return False


class Queen(Piece):
    value: int = 9
    print: str = ""

    def __init__(self, position: Position, colour: Colour) -> None:
        super().__init__(position, colour)
        if colour == Colour.WHITE:
            self.print = "Q"
        else:
            self.print = "q"

    def can_move_to(self, move_x_pos: int, move_y_pos: int) -> bool:
        straight_move: bool = Rook.can_move_to(self, move_x_pos, move_y_pos)
        diagnol_move: bool = Bishop.can_move_to(self, move_x_pos, move_y_pos)

        if straight_move ^ diagnol_move:
            return True
        else:
            return False


class King(Piece):
    value: int = 0
    print: str = ""

    def __init__(self, position: Position, colour: Colour) -> None:
        super().__init__(position, colour)
        if colour == Colour.WHITE:
            self.print = "K"
        else:
            self.print = "k"

    def can_move_to(self, move_x_pos: int, move_y_pos: int) -> bool:
        x_move_distance: int = abs(self.position.x - move_x_pos)
        y_move_distance: int = abs(self.position.y - move_y_pos)

        if x_move_distance <= 1 and y_move_distance <= 1:
            return True
        else:
            return False

    def valid_move(
        self, board: list[list[Optional[Piece]]], move_x_pos: int, move_y_pos: int
    ) -> bool:
        if not self.can_move_to(move_x_pos, move_y_pos):
            return False

        piece: Optional[Piece] = board[move_y_pos][move_x_pos]
        if piece != None and piece.colour == self.colour:
            return False

        for x in range(-1, 2):
            new_x_pos: int = move_x_pos + x

            if new_x_pos < 0 or new_x_pos > 7:
                continue

            for y in range(-1, 2):
                new_y_pos: int = move_y_pos + y

                if new_y_pos < 0 or new_y_pos > 7:
                    continue
                if new_x_pos == self.position.x and new_y_pos == self.position.y:
                    continue

                square = board[move_y_pos + y][move_x_pos + x]
                if square and isinstance(square, King):
                    return False

        return True


def generate_board() -> list[list[None]]:
    board: list[list] = []
    for _ in range(8):
        rank: list[None] = []
        for _ in range(8):
            rank.append(None)
        board.append(rank)
    return board


def populate_board(board: list[list]) -> None:
    board[0][0] = Rook(Position(0, 0), Colour.WHITE)
    board[0][1] = Knight(Position(1, 0), Colour.WHITE)
    board[0][2] = Bishop(Position(2, 0), Colour.WHITE)
    board[0][3] = Queen(Position(3, 0), Colour.WHITE)
    board[0][4] = King(Position(4, 0), Colour.WHITE)
    board[0][5] = Bishop(Position(5, 0), Colour.WHITE)
    board[0][6] = Knight(Position(6, 0), Colour.WHITE)
    board[0][7] = Rook(Position(7, 0), Colour.WHITE)

    for i in range(8):
        board[1][i] = Pawn(Position(i, 1), Colour.WHITE)

    board[7][0] = Rook(Position(0, 7), Colour.BLACK)
    board[7][1] = Knight(Position(1, 7), Colour.BLACK)
    board[7][2] = Bishop(Position(2, 7), Colour.BLACK)
    board[7][3] = Queen(Position(3, 7), Colour.BLACK)
    board[7][4] = King(Position(4, 7), Colour.BLACK)
    board[7][5] = Bishop(Position(5, 7), Colour.BLACK)
    board[7][6] = Knight(Position(6, 7), Colour.BLACK)
    board[7][7] = Rook(Position(7, 7), Colour.BLACK)

    for i in range(8):
        board[6][i] = Pawn(Position(i, 6), Colour.BLACK)

    board[6][6] = Pawn(Position(6, 6), Colour.WHITE)


def view_board(board: list[list[Optional[Piece]]]) -> None:
    print("   ┌───┬───┬───┬───┬───┬───┬───┬───┐")

    for i, rank in reversed(list(enumerate(board))):
        squares: list[str] = []
        for square in rank:
            if square:
                squares.append(square.print)
            else:
                squares.append(" ")

        if i != 7:
            print("   ├───┼───┼───┼───┼───┼───┼───┼───┤")
        print(
            f" {i+1} │ {squares[0]} │ {squares[1]} │ {squares[2]} │ {squares[3]} │ {squares[4]} │ {squares[5]} │ {squares[6]} │ {squares[7]} │"
        )

    print("   └───┴───┴───┴───┴───┴───┴───┴───┘")
    print("     a   b   c   d   e   f   g   h")


def update_piece_data(piece: Piece, move_position: Position) -> None:
    piece.position = Position(move_position.x, move_position.y)
    if isinstance(piece, Pawn):
        piece.max_move = 1


def char_to_piece_type(char: str) -> type[Piece]:
    char = char.upper()
    match char:
        case "Q":
            return Queen
        case "R":
            return Rook
        case "B":
            return Bishop
        case "N":
            return Knight
        case "P":
            return Pawn
        case "K":
            return King


def promote_piece(
    board: list[list[Optional[Piece]]], move: str, piece: Piece, colour: Colour
) -> None:
    PROMOTION_REGEXP = r"=[QRBNqrbn]"

    if piece.position.y != 7 and piece.colour == Colour.WHITE:
        return

    elif piece.position.y != 0 and piece.colour == Colour.BLACK:
        return

    promotion_input: Optional[re.Match] = re.search(PROMOTION_REGEXP, move)

    piece_class_type: type[Piece]
    if promotion_input != None:
        piece_class_type = char_to_piece_type(promotion_input.group(0)[1])

    else:
        while True:
            piece_type_input: str = input("promote to (Q, R, B, N): ")

            if len(piece_type_input) != 1 or piece_type_input.isdigit():
                continue

            piece_type = char_to_piece_type(piece_type_input)

            if piece_type != Pawn and piece_type != King:
                piece_class_type = piece_type
                break

    new_piece = piece_class_type(Position(piece.position.x, piece.position.y), colour)
    board[piece.position.y][piece.position.x] = new_piece


def move_piece(
    board: list[list[Optional[Piece]]], piece: Piece, move_position: Position
) -> None:
    board[piece.position.y][piece.position.x] = None
    board[move_position.y][move_position.x] = piece


def capture_piece(
    board: list[list[Optional[Piece]]], piece: Piece, move_position: Position
) -> None:
    # TODO implement score tracking (values of pieces taken)
    captured_piece: Optional[Piece] = board[move_position.y][move_position.x]
    value: int = piece.value

    move_piece(board, piece, move_position)


def get_if_capture(
    board: list[list[Optional[Piece]]], position: Position, player_colour: Colour
) -> bool:
    piece: Optional[Piece] = board[position.y][position.x]
    if piece != None and piece.colour != player_colour:
        return True
    else:
        return False


def get_piece_object(
    board: list[list[Optional[Piece]]], piece_position: Position
) -> Optional[Piece]:
    return board[piece_position.y][piece_position.x]


# TODO not accounting for piece specified by usere ex. ngf3 instead of nef3
# TODO when multiple possible pieces can take prompt user to choose which one
def get_piece_position(
    board: list[list[Optional[Piece]]],
    piece_type: type[Piece],
    move_position: Position,
    identifier: Optional[Position],
    colour: Colour,
) -> Optional[Position]:
    # for each piece on the board check if it can move to the position to move to
    for y, rank in enumerate(board):
        for x, piece in enumerate(rank):
            if piece == None:
                continue
            elif not isinstance(piece, piece_type):
                continue
            elif piece.colour != colour:
                continue

            if piece.valid_move(board, move_position.x, move_position.y):
                if identifier != None:
                    if identifier.x == x or identifier.y == y:
                        return Position(x, y)
                    else:
                        continue
                else:
                    return Position(x, y)

    return None


def get_piece_type(move: str, move_type: MoveType) -> type[Piece]:
    FILES = ["a", "b", "c", "d", "e", "f", "g", "h"]

    if move_type == MoveType.CASTLE:
        return King
    elif move_type == MoveType.PROMOTION:
        return Pawn
    # only pawn moves dont specify the piece ex. e4, dxc6
    elif move[0] in FILES:
        return Pawn
    else:
        return char_to_piece_type[move[0]]


def get_move_type(move: str) -> MoveType:
    NORMAL_REGEXP = r"[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8]"
    PROMOTION_REGEXP = r"=[QRBNqrbn]"
    CASTLE_REGEXP = r"[Oo0](-[Oo0]){1,2}"

    if re.match(NORMAL_REGEXP, move, re.IGNORECASE) != None:
        if re.search(PROMOTION_REGEXP, move) != None:
            return MoveType.PROMOTION
        else:
            return MoveType.NORMAL

    elif re.match(CASTLE_REGEXP, move) != None:
        return MoveType.CASTLE

    else:
        raise ValueError("move type could not be inferred")


def file_to_index(file: str) -> int:
    return int(ord(file.lower()) - 97)


def get_move_position(move: str) -> Optional[Position]:
    REGEXP = r"[a-h][1-8]"

    match: Optional[re.Match] = re.search(REGEXP, move)
    if match == None:
        return None

    position: str = match.group(0)
    return Position(file_to_index(position[0]), int(position[1]) - 1)


def get_piece_identifier(move: str, move_type: str) -> Optional[Position]:
    # TODO theres definitely a better way to do this with regex
    if len(move) != 4 or len(move) != 5 or move_type != MoveType.NORMAL:
        return None

    if move[1].isdigit():
        return Position(0, int(move[1]))
    else:
        return Position(file_to_index(move[1]), 0)


def is_valid_chess_move_notation(move: str) -> bool:
    # https://8bitclassroom.com/2020/08/16/chess-in-regex/
    MOVE_REGEXP = r"[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](\=[QRBN])?"
    CASTLE_REGEXP = r"[Oo0](-[Oo0]){1,2}"
    if (
        re.match(MOVE_REGEXP, move, re.IGNORECASE) != None
        or re.match(CASTLE_REGEXP, move) != None
    ):
        return True
    else:
        return False


def get_player_move() -> str:
    while True:
        move: str = str(input("move: "))
        move = move.strip()
        if is_valid_chess_move_notation(move):
            return move
        else:
            print("invalid move")


def game():
    board: list[list[None]] = generate_board()
    populate_board(board)
    view_board(board)
    move_count: int = 0
    player_colour: Colour = Colour.WHITE
    while True:
        if move_count % 2 == 0:
            player_colour = Colour.WHITE
            print("whites turn")
        else:
            player_colour = Colour.BLACK
            print("blacks turn")

        # TODO handle all None return types here
        move: str = get_player_move()
        print(move)

        move_type: MoveType = get_move_type(move)
        print(move_type)

        piece_type: type[Piece] = get_piece_type(move, move_type)
        print(piece_type)

        move_position: Optional[Position] = get_move_position(move)
        print(move_position)

        piece_identifier: Optional[Position] = get_piece_identifier(move, move_type)
        print(piece_identifier)

        piece_position: Optional[Position] = get_piece_position(
            board, piece_type, move_position, piece_identifier, player_colour
        )
        print("piece position:", piece_position)

        piece: Optional[Piece] = get_piece_object(board, piece_position)

        is_capture: bool = get_if_capture(board, move_position, player_colour)
        print(is_capture)

        if is_capture:
            capture_piece(board, piece, move_position)
        else:
            move_piece(board, piece, move_position)

        update_piece_data(piece, move_position)

        if move_type == MoveType.PROMOTION or (
            piece_type == Pawn and move_position.y in [0, 7]
        ):
            promote_piece(board, move, piece, player_colour)

        # TODO look for check or checkmate

        view_board(board)

        move_count += 1


def main():
    game()


if __name__ == "__main__":
    main()
