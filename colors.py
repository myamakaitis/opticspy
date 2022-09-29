import numpy as np


def rgb2hex(rgb):
    """
    Converts from array rgb values to hex string
    :param rgb: Array of rbg values
    :return: String of hex values
    """

    if len(rgb) != 3:
        raise ValueError("RBG Array wrong size")
    elif max(rgb) > 255:
        raise ValueError("Maximum RBG value is 255")
    elif np.mean(rgb) < 1:
        rgb = [255*v for v in rgb]

    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"

def hex2rgb(hex_str):
    """
    Converts a hex number string representing color into rgb values
    :param hex_str: 7 character string with the first character being ignored
    :return: unsigned 8 bit integer array of red green and blue values
    """
    if len(hex_str) != 7:
        raise ValueError("Hex String must be 7 characters")

    r, g, b = '0x' + hex_str[1:3], '0x' + hex_str[3:5], '0x' + hex_str[5:]
    r, g, b = int(r, 0), int(g, 0), int(b, 0)

    return np.array([r, g, b], dtype = np.uint8)