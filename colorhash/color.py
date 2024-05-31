import abc
import colorsys
import dataclasses


class Color(metaclass=abc.ABCMeta):
    """
    An abstract color class.

    This can be used to convert any color format into another color format.
    """

    @abc.abstractmethod
    def to_html_color(self) -> str:
        """
        Convert this color to an HTML color.

        This may produce unexpected results if you are expecting an RGB color. If you are expecting
        RGB, then you should use `color.to_rgb().to_html_color()` instead.
        """

    @abc.abstractmethod
    def to_rgb(self) -> "RGBColor":
        "Convert this color into an RGB color."

    @abc.abstractmethod
    def to_hsl(self) -> "HSLColor":
        "Convert this color into an HSL color."


@dataclasses.dataclass
class RGBColor(Color):
    """
    An RGB color. Colors are expected to be a floating point value from [0.0-255.0).
    """
    r: float
    g: float
    b: float

    def to_html_color(self) -> str:
        r, g, b = round(self.r), round(self.g), round(self.b)
        return f"#{r:02x}{g:02x}{b:02x}"

    def to_rgb(self) -> "RGBColor":
        return self

    def to_hsl(self) -> "HSLColor":
        r = self.r / 255.0
        g = self.g / 255.0
        b = self.b / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return HSLColor(h * 360.0, s * 100.0, l * 100.0)


@dataclasses.dataclass
class HSLColor(Color):
    h: float
    s: float
    l: float

    def to_html_color(self) -> str:
        return f"hsl({self.h:.02f},{self.s:.02f}%,{self.l:.02f}%)"

    def to_rgb(self) -> "RGBColor":
        h = self.h / 360.0
        s = self.s / 100.0
        l = self.l / 100.0
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return RGBColor(r * 255.0, g * 255.0, b * 255.0)


    def to_hsl(self) -> "HSLColor":
        return self
