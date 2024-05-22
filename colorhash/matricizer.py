import abc
from typing import Sequence


Matrix = Sequence[Sequence[int]]


class Matricizer(metaclass=abc.ABCMeta):
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    @abc.abstractmethod
    def hash_to_matrix(self, data: bytes) -> Matrix:
        """
        Convert a hash to a matrix of given width and height.
        """


class NibbleMatricizer(Matricizer):
    def hash_to_matrix(self, data: bytes) -> Matrix:
        """
        Convert a set of bytes to a list of rows of nibbles.
        """

        nibbles = []
        for b in data:
            top = (b & 0xF0) >> 4
            bottom = b & 0x0F
            nibbles += [top, bottom]

        if len(nibbles) != self.w * self.h:
            raise ValueError(
                f"input data length ({len(nibbles)}) must match matrix dimensions ({self.w}x{self.h} = {self.w * self.h})"
            )

        cols = []
        row = []
        for b in nibbles:
            row += [b]
            if len(row) == self.w:
                cols += [row]
                row = []

        return cols
