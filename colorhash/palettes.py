"Base color palette definitions."
from typing import Sequence

from .color import Color, HSLColor


HSLRange = range | float | int | list[float | int]
Palette = Sequence[Color]


def quantize(r: range, steps: int = 16) -> list[float]:
    """
    Given a range and a number of steps, create a list of numbers starting and ending in the range
    (inclusive) with that number of steps.

    :param r: the range to quantize.
    :param steps: the number of steps to use.
    :returns: a list of the quantized range.
    """
    dist = abs(r.stop - r.start)
    return [r.start + (i * dist / (steps - 1)) for i in range(steps)]


def hsl_palette(hue: HSLRange, sat: HSLRange, light: HSLRange) -> list[HSLColor]:
    """
    Utility method to create 16 colors using HSL.

    :param hue: the hue, or range of hues, to use for this palette.
    :param sat: the saturation, or range of saturations, to use for this palette.
    :param light: the light value, or range of light values, to use for this palette.
    """

    if isinstance(hue, (float, int)):
        hue = [hue] * 16
    elif isinstance(hue, range):
        hue = quantize(hue)
    assert len(hue) == 16, "hue values must be a list of 16 elements"

    if isinstance(sat, (float, int)):
        sat = [sat] * 16
    elif isinstance(sat, range):
        sat = quantize(sat)
    assert len(sat) == 16, "saturation values must be a list of 16 elements"

    if isinstance(light, (float, int)):
        light = [light] * 16
    elif isinstance(light, range):
        light = quantize(light)
    assert len(light) == 16, "light values must be a list of 16 elements"

    return [HSLColor(h, s, l) for h, s, l in zip(hue, sat, light)]


GRADIENT_PALETTES = {
    # Interesting thing with human perception.
    # Between red and yellow, we can perceive "orange". We have a name for it and see it as a
    # distinct color. However, between yellow and green, we see a sickly green; between green and
    # cyan, a seafoam green; between cyan and blue, a lighter blue.
    #
    # Beside these, I think that between blue and magenta gives a color you could safely call
    # "purple", and between magenta and red, you get a color you could safely call "pink". It seems
    # that reds are more distinct to the human eye.
    #
    # For this reason, I have decided to pick these palettes as the "defaults", with a "dark" and
    # "light" variant of each (lightness 0-50%, and 50-100% respectively), with an additional
    # fully-saturated "rainbow" palette with all of the colors:
    #
    # red, orange, yellow, green, cyan, blue, purple, magenta, pink, gray, rainbow
    #
    # Also disabling yellow-light, that one just gives me a headache. It's hard to look at.
    #
    "red-light": hsl_palette(0, 100, range(50, 100)),
    "red-dark": hsl_palette(0, 100, range(0, 50)),
    #
    "orange-light": hsl_palette(30, 100, range(50, 100)),
    "orange-dark": hsl_palette(30, 100, range(0, 50)),
    #
    # "yellow-light": hsl_palette(60, 100, range(50, 100)),
    "yellow-dark": hsl_palette(60, 100, range(0, 50)),
    #
    # "lime-light": hsl_palette(90, 100, range(50, 100)),
    # "lime-dark": hsl_palette(90, 100, range(0, 50)),
    #
    "green-light": hsl_palette(120, 100, range(50, 100)),
    "green-dark": hsl_palette(120, 100, range(0, 50)),
    #
    # "seafoam-light": hsl_palette(150, 100, range(50, 100)),
    # "seafoam-dark": hsl_palette(150, 100, range(0, 50)),
    #
    "cyan-light": hsl_palette(180, 100, range(50, 100)),
    "cyan-dark": hsl_palette(180, 100, range(0, 50)),
    #
    # "teal-light": hsl_palette(210, 100, range(50, 100)),
    # "teal-dark": hsl_palette(210, 100, range(0, 50)),
    #
    "blue-light": hsl_palette(240, 100, range(50, 100)),
    "blue-dark": hsl_palette(240, 100, range(0, 50)),
    #
    "purple-light": hsl_palette(270, 100, range(50, 100)),
    "purple-dark": hsl_palette(270, 100, range(0, 50)),
    #
    "magenta-light": hsl_palette(300, 100, range(50, 100)),
    "magenta-dark": hsl_palette(300, 100, range(0, 50)),
    #
    "pink-light": hsl_palette(330, 100, range(50, 100)),
    "pink-dark": hsl_palette(330, 100, range(0, 50)),
    #
    "gray-light": hsl_palette(0, 0, range(50, 100)),
    "gray-dark": hsl_palette(0, 0, range(0, 50)),
}


MULTICOLOR_PALETTES = {
    "rainbow": hsl_palette(range(0, 360), 100, 50),
    "rainbow-reverse": list(reversed(hsl_palette(range(0, 360), 100, 50))),
}

DEFAULT_PALETTES = {
    **GRADIENT_PALETTES,
    **MULTICOLOR_PALETTES,
}


PALETTES = {**DEFAULT_PALETTES}
