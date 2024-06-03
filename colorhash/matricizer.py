"All things that turn a hash into a matrix."
import abc
from typing import Mapping, Sequence

from .palettes import Palette, DEFAULT_PALETTES, GRADIENT_PALETTES, MULTICOLOR_PALETTES


Matrix = Sequence[Sequence[int]]


class Matricizer(metaclass=abc.ABCMeta):
    """
    The base Matricizer class.

    A matricizer turns a collection of hash bytes into a matrix of values between 0x0 and 0xf
    (inclusive). The method by which this is done is up to the matricizer.
    """

    def __init__(self, w: int, h: int) -> None:
        """
        Create a new matricizer for the given dimensions.

        :param w: the width of the output matrix.
        :param h: the height of hte output matrix.
        """
        self.w = w
        self.h = h

    @abc.abstractmethod
    def matricize(self, data: bytes) -> Matrix:
        """
        Convert a hash to a matrix of given width and height.

        :param data: the hash data to turn into a matrix.
        :returns: the matrix converted from the hash data.
        """

    @staticmethod
    @abc.abstractmethod
    def choose_dimensions(hash: str) -> tuple[int, int]:
        """
        Choose the dimensions for this matrix based on the hash algorithm.

        :param hash: the hash algorithm being used.
        :returns: a width and height as a tuple.
        """

    def choose_palette(
        self, data: bytes, palettes: Mapping[str, Palette] | None = None
    ) -> Palette:
        """
        Choose a palette based on the give data and palettes.

        By default, this method will choose the Nth palette from the sum of the data mod the length
        of all palettes provided (using all palettes as the default).
        """
        if palettes is None:
            palettes = DEFAULT_PALETTES
        return list(palettes.values())[sum(data) % len(palettes)]


class NibbleMatricizer(Matricizer):
    """
    A matricizer that converts a hash based on all of the nibbles in the hash.

    While dimensions are not enforced by this matricizer, it is strongly recommended to use the
    dimensions provided by the `NibbleMatricizer.DIMENSIONS` member.
    """

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

        :param data: the hash data to turn into a matrix.
        :returns: the matrix converted from the hash data.
        """

        nibbles = []
        for b in data:
            top = (b & 0xF0) >> 4
            bottom = b & 0x0F
            nibbles += [top, bottom]

        if len(nibbles) != self.w * self.h:
            raise ValueError(
                f"input data length ({len(nibbles)}) must match matrix dimensions "
                f"({self.w}x{self.h} = {self.w * self.h})"
            )

        cols = []
        row = []
        for b in nibbles:
            row += [b]
            if len(row) == self.w:
                cols += [row]
                row = []

        return cols

    @staticmethod
    def choose_dimensions(hash: str) -> tuple[int, int]:
        return NibbleMatricizer.DIMENSIONS[hash]

    def choose_palette(
        self, data: bytes, palettes: Mapping[str, Palette] | None = None
    ) -> Palette:
        return super().choose_palette(data, palettes or GRADIENT_PALETTES)


class RandomartMatricizer(Matricizer):
    """
    A matricizer that converts hash data into a matrix based on the "randomart" algorithm from
    ssh-keygen.

    See: https://github.com/openssh/openssh-portable/blob/fc5dc092830de23767c6ef67baa18310a64ee533/sshkey.c#L1014
    """

    DIMENSIONS = {
        "md5": (7, 6),
        "sha1": (7, 6),
        "sha224": (8, 7),
        "sha256": (8, 7),
        "sha384": (11, 10),
        "sha512": (11, 10),
    }

    def matricize(self, data: bytes) -> Matrix:
        """
        Create a matrix based on the "randomart" algorithm from ssh-keygen.

        The algorithm is as follows:

        1. Choose the point in the middle of the matrix.
        2. Iterate through the data, two bits at a time.
        3. If the low bit is set, then move the pointer right. Otherwise, move left.
        4. If the high bit is set, then move the pointer down. Otherwise, move up.
        5. If stepping in either direction would move us outside of the matrix, then don't move in
           that direction.
        6. At the end of each step, increment the value in the matrix by one.

        :param data: the hash data to turn into a matrix.
        :returns: the matrix converted from the hash data.
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
                if rows[r][c] < 0xF:
                    rows[r][c] += 1
                value >>= 2;
        return rows

    @staticmethod
    def choose_dimensions(hash: str) -> tuple[int, int]:
        return RandomartMatricizer.DIMENSIONS[hash]

    def choose_palette(
        self, data: bytes, palettes: Mapping[str, Palette] | None = None
    ) -> Palette:
        return super().choose_palette(data, palettes or MULTICOLOR_PALETTES)
