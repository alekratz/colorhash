import abc
from typing import Sequence


Matrix = Sequence[Sequence[int]]


class Matricizer(metaclass=abc.ABCMeta):
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    @abc.abstractmethod
    def matricize(self, data: bytes) -> Matrix:
        """
        Convert a hash to a matrix of given width and height.
        """


class NibbleMatricizer(Matricizer):
    DIMENSIONS = {
        "md5": (8, 4),
        "sha1": (8, 5),
        "sha224": (8, 7),
        "sha256": (8, 8),
        "sha384": (12, 8),
        "sha512": (16, 8),
    }
    def matricize(self, data: bytes) -> Matrix:
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


class RandomartMatricizer(Matricizer):
    def matricize(self, data: bytes) -> Matrix:
        """
        Create a matrix based on the "randomart" algorithm from ssh-keygen.
        """
        rows = [[0] * self.w for _ in range(self.h)]
        c = self.w // 2
        r = self.h // 2
        for value in data:
            for _ in range(4):
                if value & 0x1:
                    c += 1
                else:
                    c -= 1
                if value & 0x2:
                    r += 1
                else:
                    r -= 1
                c = min(max(c, 0), self.w - 1)
                r = min(max(r, 0), self.h - 1)
                # max value is 0xf
                if rows[r][c] < 0xf:
                    rows[r][c] += 1
        return rows
