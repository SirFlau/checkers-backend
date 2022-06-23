import unittest

from parameterized import parameterized

from ..ValidateMove.util.validate_move import MoveValidator


class TestMoveValidator(unittest.TestCase):
    def test_basic_move(self):
        validator = MoveValidator(old_game_state="111111111111000000003333333333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="111111111111000003003303333333331")
        self.assertTrue(result)

    def test_white_move(self):
        validator = MoveValidator(old_game_state="111111111111000003003303333333331",
                                  move_requester_color="white")
        result = validator.validate_new_state(new_state="111111111011001003003303333333330")
        self.assertTrue(result)

    def test_basic_move_invalid(self):
        validator = MoveValidator(old_game_state="111111111111000000003333333333330",
                                  move_requester_color="white")
        result = validator.validate_new_state(new_state="111111111111003000003303333333331")
        self.assertFalse(result)

    def test_basic_move_invalid_not_players_turn(self):
        validator = MoveValidator(old_game_state="111111111111000000003333333333330",
                                  move_requester_color="white")
        result = validator.validate_new_state(new_state="111111111011001000003333333333331")
        self.assertFalse(result)

    def test_no_turn_switch(self):
        validator = MoveValidator(old_game_state="111111111111000000003333333333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="111111111111000003003303333333330")
        self.assertFalse(result)

    def test_king_move(self):
        validator = MoveValidator(old_game_state="111111111111000004003303333333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="111111111111000000003343333333331")
        self.assertTrue(result)

    def test_moving_opponents_piece_fails(self):
        validator = MoveValidator(old_game_state="111111111111000000003333333333331",
                                  move_requester_color="white")
        result = validator.validate_new_state(new_state="111111111111000003003303333333330")
        self.assertFalse(result)

    def test_no_overwrite(self):
        validator = MoveValidator(old_game_state="111111111111000001003333333333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="111111111111000003003303333333331")
        self.assertFalse(result)

    @parameterized.expand([
        ["000030000110000000003333333333330", "400000000110000000003333333333331", True],
        ["000030000110000000003333333333330", "300000000110000000003333333333331", False]
    ])
    def test_promote_to_black_king(self, old_game_state, new_game_state, expected_result):
        validator = MoveValidator(old_game_state=old_game_state,
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state=new_game_state)
        self.assertEqual(result, expected_result)

    @parameterized.expand([
        ["110111010001033103000330103300331", "110111010001033103000330003320330", True],
        ["110111010001033103000330103300331", "110111010001033103000330003310330", False]
    ])
    def test_promote_to_white_king(self, old_game_state, new_game_state, expected_result):
        validator = MoveValidator(old_game_state=old_game_state,
                                  move_requester_color="white")
        result = validator.validate_new_state(new_state=new_game_state)
        self.assertEqual(result, expected_result)

    @parameterized.expand([
        ["110111010001033103000330203300331", "110111010001033103000330003320330", True],
        ["110111010001033103000330103300331", "110111010001033103000330003310330", False]
    ])
    def test_white_king_to_back(self, old_game_state, new_game_state, expected_result):
        validator = MoveValidator(old_game_state=old_game_state,
                                  move_requester_color="white")
        result = validator.validate_new_state(new_state=new_game_state)
        self.assertEqual(result, expected_result)

    def test_capture_forced(self):
        validator = MoveValidator(old_game_state="111111111110000100303303333333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="111111111110000130303003333333331")
        self.assertFalse(result)

    def test_capture(self):
        validator = MoveValidator(old_game_state="111111111110000100303303333333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="111111111113000000003303333333331")
        self.assertTrue(result)

    def test_capture_becomes_king(self):
        validator = MoveValidator(old_game_state="011111011311000000003303003333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="411110011011000000003303003333331")
        self.assertTrue(result)

    def test_set_capture_continuation(self):
        validator = MoveValidator(old_game_state="400111111001001003003303000333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="0001101114010010030033030003333329")
        self.assertTrue(result)

    def test_capture_continuation(self):
        validator = MoveValidator(old_game_state="0001101114010010030033030003333329",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="004110011001001003003303000333331")
        self.assertTrue(result)

    def test_regular_move_does_not_trigger_continuous_capture_check_bug_fix(self):
        # A bug was discovered, where the check for continuing to capture when more captures are available,
        # was executed even if the original move was not a capture.
        validator = MoveValidator(old_game_state="111111011101000000303300303333331",
                                  move_requester_color="white")
        result = validator.validate_new_state(new_state="111111011001001000303300303333330")
        self.assertTrue(result)

    def test_index_out_of_bounds_bug_fix(self):
        # A bug was discovered, where the capturing into index -1 was seen as valid.
        validator = MoveValidator(old_game_state="111111110111010003003303333333330",
                                  move_requester_color="black")
        result = validator.validate_new_state(new_state="111111113111000000003303333333331")
        self.assertTrue(result)
