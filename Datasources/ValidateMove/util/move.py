from dataclasses import dataclass


@dataclass
class Move:
    piece_start_location: int
    piece_end_location: int
    piece_type: int
    capture_location: int = None
