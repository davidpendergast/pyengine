import typing


def _bound(v, lower, upper):
    return max(min(v, upper), lower)


def to_float(r, g=0, b=0, a=None):
    """Takes a color with components 0-255 and converts it to a color with components 0-1"""
    if isinstance(r, (tuple, list)):
        return tuple(_bound(v / 255, 0, 1) for v in r)
    else:
        rf = _bound(r / 256, 0, 1)
        gf = _bound(g / 256, 0, 1)
        bf = _bound(b / 256, 0, 1)
        if a is not None:
            return (rf, gf, bf, _bound(a / 256, 0, 1))
        else:
            return (rf, gf, bf)


def to_int(r, g=0, b=0, a=None):
    """Takes a color with components 0-1 and converts it to a color with components 0-255 (rounded)"""
    if isinstance(r, tuple):
        return tuple(_bound(v * 256, 0, 255) for v in r)
    else:
        ri = _bound(int(r * 256), 0, 255)
        gi = _bound(int(g * 256), 0, 255)
        bi = _bound(int(b * 256), 0, 255)
        if a is not None:
            return (ri, gi, bi, _bound(int(a * 256), 0, 255))
        else:
            return (ri, gi, bi)


def darker(float_color, pcnt=0.2):
    rgb = (_bound((1 - pcnt) * float_color[0], 0, 1),
           _bound((1 - pcnt) * float_color[1], 0, 1),
           _bound((1 - pcnt) * float_color[2], 0, 1))

    if len(float_color) >= 4:
        return (rgb[0], rgb[1], rgb[2], float_color[3])
    else:
        return rgb


def lighter(float_color, pcnt=0.2):
    return darker(float_color, -pcnt)


def darker_int(color, pcnt=0.2):
    if pcnt < 0:
        return lighter_int(color, pcnt=-pcnt)
    res = []
    for c in color:
        res.append(max(0, min(255, int(c * (1 - pcnt)))))
    return tuple(res)


def lighter_int(color, pcnt=0.2):
    if pcnt < 0:
        return darker_int(color, pcnt=-pcnt)
    res = []
    for c in color:
        dist = 255 - c
        new_dist = int(dist) * (1 - pcnt)
        res.append(max(0, min(255, int(255 - new_dist))))
    return tuple(res)


def is_transparent(color, pcnt_thresh=0) -> bool:
    if len(color) < 4:
        return False
    else:
        return color[3] <= pcnt_thresh


def hsv_to_rgb(h, s, v) -> typing.Tuple[float, float, float]:
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
