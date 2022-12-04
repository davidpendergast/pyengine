

def _bound(v, lower, upper):
    return max(min(v, upper), lower)


def to_float(r, g, b, a=None):
    rf = _bound(r / 256, 0, 1)
    gf = _bound(g / 256, 0, 1)
    bf = _bound(b / 256, 0, 1)
    if a is not None:
        return (rf, gf, bf, _bound(a / 256, 0, 1))
    else:
        return (rf, gf, bf)


def to_floatn(color):
    return tuple(_bound(v / 255, 0, 1) for v in color)


def to_int(r, g, b, a=None):
    ri = _bound(int(r * 256), 0, 255)
    gi = _bound(int(g * 256), 0, 255)
    bi = _bound(int(b * 256), 0, 255)
    if a is not None:
        return (ri, gi, bi, _bound(int(a * 256), 0, 255))
    else:
        return (ri, gi, bi)


def to_intn(color):
    return tuple(_bound(v * 256, 0, 255) for v in color)


def darken(float_color, darkness):
    rgb = (_bound((1 - darkness) * float_color[0], 0, 1),
           _bound((1 - darkness) * float_color[1], 0, 1),
           _bound((1 - darkness) * float_color[2], 0, 1))

    if len(float_color) >= 4:
        return (rgb[0], rgb[1], rgb[2], float_color[3])
    else:
        return rgb


def lighten(float_color, lightness):
    return darken(float_color, -lightness)


def hsv_to_rgb(h, s, v):
    """
    :param h: 0 <= h < 360
    :param s: 0 <= s <= 1
    :param v: 0 <= v <= 1
    :return: (r, g, b) as floats
    """
    C = v * s
    X = C * (1 - abs((h / 60) % 2 - 1))
    m = v - C

    if h < 60:
        rgb_prime = (C, X, 0)
    elif h < 120:
        rgb_prime = (X, C, 0)
    elif h < 180:
        rgb_prime = (0, C, X)
    elif h < 240:
        rgb_prime = (0, X, C)
    elif h < 300:
        rgb_prime = (X, 0, C)
    else:
        rgb_prime = (C, 0, X)

    return (rgb_prime[0] + m, rgb_prime[1] + m, rgb_prime[2] + m)
