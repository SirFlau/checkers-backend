from .move import Move

FORWARD_LEFT = "forward_left"
FORWARD_RIGHT = "forward_right"
BACK_LEFT = "back_left"
BACK_RIGHT = "back_right"

DIRECTION_MAPPING = {
    "forward_left": {"correction": -4, "row_change": 1},
    "forward_right": {"correction": -3, "row_change": 1},
    "back_left": {"correction": 4, "row_change": -1},
    "back_right": {"correction": 5, "row_change": -1}
}

TURN_MAPPING = {
    "0": "black",
    "1": "white",
    "2": "blackContinuation",
    "3": "whiteContinuation"
}


class MoveValidator:
    def __init__(self, old_game_state, move_requester_color):
        self.old_game_state = old_game_state
        self.move_requester_color = move_requester_color
        self.turn_old_state = None
        self.set_turn_states()

    def find_all_valid_new_states(self):
        continuation_moves = self.find_continuation_states()
        if continuation_moves:
            return continuation_moves

        forced_captures = self.find_forced_capture_states()
        if forced_captures:
            return forced_captures

        return self.find_regular_move_states()

    def validate_new_state(self, new_state):
        if not self.validate_turn_state():
            return False
        return new_state in self.find_all_valid_new_states()

    def find_regular_move_states(self):
        moves = self.find_regular_moves()
        result = []
        for move in moves:
            result.append(self.generate_possible_new_game_state_from_move(move))
        return result

    def find_regular_moves(self):
        moves = []
        turn_piece_types = []

        if self.move_requester_color == "black":
            turn_piece_types.append(3)
            turn_piece_types.append(4)
        else:
            turn_piece_types.append(1)
            turn_piece_types.append(2)

        for i in range(32):
            piece_type = int(self.old_game_state[i])
            if piece_type not in turn_piece_types:
                continue
            possible_moves = self.find_standard_moves(i, piece_type)
            for move in possible_moves:
                moves.append(move)
        return moves

    def find_standard_moves(self, index, piece_type):
        directions = self.get_directions(piece_type)
        result = []

        for direction in directions:
            neighbour_square = self.get_index_of_neighbour(index, direction)
            if neighbour_square is None:
                continue
            if self.old_game_state[neighbour_square] == "0":
                result.append(Move(
                    piece_start_location=index,
                    piece_end_location=neighbour_square,
                    piece_type=piece_type
                ))
        return result

    def find_forced_capture_states(self):
        forced_moves = self.find_forced_moves()
        result = []
        for move in forced_moves:
            result.append(self.generate_possible_new_game_state_from_move(move))
        return result

    def find_continuation_states(self):
        result = []
        if self.turn_old_state == "blackContinuation" or self.turn_old_state == "whiteContinuation":
            forced_continuation_piece_location = int(self.old_game_state[33:])
            moves = self.find_captures(forced_continuation_piece_location,
                                       int(self.old_game_state[forced_continuation_piece_location]))
            for move in moves:
                result.append(self.generate_possible_new_game_state_from_move(move))
        return result

    def validate_turn_state(self):
        if self.turn_old_state != self.move_requester_color:
            if self.turn_old_state == "whiteContinuation":
                if self.move_requester_color == "white":
                    return True
            elif self.turn_old_state == "blackContinuation":
                if self.move_requester_color == "black":
                    return True
            return False
        return True

    def generate_possible_new_game_state_from_move(self, move):
        old_game_state = list(self.old_game_state[:33])
        old_game_state[move.piece_start_location] = "0"
        old_game_state[move.piece_end_location] = str(move.piece_type)
        if move.piece_type == 1 and self.get_row_by_index(move.piece_end_location) == 7:
            old_game_state[move.piece_end_location] = "2"
        if move.piece_type == 3 and self.get_row_by_index(move.piece_end_location) == 0:
            old_game_state[move.piece_end_location] = "4"

        if move.capture_location is not None:
            old_game_state[move.capture_location] = "0"

        if self.move_requester_color == "white":
            if self.find_captures(move.piece_end_location, move.piece_type) and move.capture_location is not None:
                old_game_state[32] = "3"
                old_game_state.append(str(move.piece_end_location))
            else:
                old_game_state[32] = "0"
        elif self.move_requester_color == "black":
            if self.find_captures(move.piece_end_location, move.piece_type) and move.capture_location is not None:
                future_captures = self.find_captures(move.piece_end_location, move.piece_type)
                old_game_state[32] = "2"
                old_game_state.append(str(move.piece_end_location))
            else:
                old_game_state[32] = "1"

        return "".join(old_game_state)

    def find_forced_moves(self):
        forced_moves = []
        turn_piece_types = []

        if self.move_requester_color == "black":
            turn_piece_types.append(3)
            turn_piece_types.append(4)
        else:
            turn_piece_types.append(1)
            turn_piece_types.append(2)

        for i in range(32):
            if i == 17:
                test_captures = self.find_captures(i, 3)
            piece_type = int(self.old_game_state[i])
            if piece_type not in turn_piece_types:
                continue
            possible_captures = self.find_captures(i, piece_type)

            for capture in possible_captures:
                forced_moves.append(capture)
        return forced_moves

    def find_captures(self, index, piece_type):
        directions = self.get_directions(piece_type)
        result = []

        for direction in directions:
            neighbour_square = self.get_index_of_neighbour(index, direction)
            if neighbour_square is None:
                continue
            if (self.old_game_state[neighbour_square] == "1" or self.old_game_state[neighbour_square] == "2") and (piece_type == 3 or piece_type == 4):
                behind_neighbour = self.get_index_of_neighbour(neighbour_square, direction)
                if behind_neighbour is None:
                    continue
                if self.old_game_state[behind_neighbour] == "0":
                    result.append(Move(piece_start_location=index,
                                       piece_end_location=behind_neighbour,
                                       capture_location=neighbour_square,
                                       piece_type=piece_type
                                       ))

            if (self.old_game_state[neighbour_square] == "3" or self.old_game_state[neighbour_square] == "4") and (piece_type == 1 or piece_type == 2):
                behind_neighbour = self.get_index_of_neighbour(neighbour_square, direction)
                if behind_neighbour is None:
                    continue
                if self.old_game_state[behind_neighbour] == "0":
                    result.append(Move(piece_start_location=index,
                                       piece_end_location=behind_neighbour,
                                       capture_location=neighbour_square,
                                       piece_type=piece_type
                                       ))
        return result

    @staticmethod
    def get_directions(piece_type):
        if piece_type == 1:
            return [BACK_LEFT, BACK_RIGHT]
        if piece_type == 2 or piece_type == 4:
            return [FORWARD_RIGHT, FORWARD_LEFT, BACK_RIGHT, BACK_LEFT]
        if piece_type == 3:
            return [FORWARD_RIGHT, FORWARD_LEFT]
        return []

    def set_turn_states(self):
        turn = TURN_MAPPING.get(self.old_game_state[32:33])
        if turn is None:
            raise ValueError("Invalid turn value")
        self.turn_old_state = turn

    def get_index_of_neighbour(self, index, direction):
        direction_info = DIRECTION_MAPPING[direction]
        row_index = self.get_row_by_index(index)
        result = index + direction_info["correction"] - row_index % 2

        result_row_index = self.get_row_by_index(result)
        if row_index - result_row_index != direction_info["row_change"]:
            return None
        if result_row_index < 0 or result_row_index > 7:
            return None
        if result < 0 or result > 31:
            return None
        return result

    @staticmethod
    def get_row_by_index(index):
        return int(index / 4)
