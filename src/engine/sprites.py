import pygame
import src.utils.util as util


UNIQUE_ID_CTR = 0


def gen_unique_id():
    """Note: this ain't threadsafe"""
    global UNIQUE_ID_CTR
    UNIQUE_ID_CTR += 1
    return UNIQUE_ID_CTR - 1


class SpriteTypes:
    IMAGE = "IMAGE"
    TRIANGLE = "TRIANGLE"


class _Sprite:

    def __init__(self, sprite_type, layer_id, uid=None):
        self._sprite_type = sprite_type
        self._layer_id = layer_id
        self._uid = gen_unique_id() if uid is None else uid

    def sprite_type(self):
        return self._sprite_type

    def layer_id(self):
        return self._layer_id

    def uid(self):
        return self._uid

    def __repr__(self):
        return "_Sprite({}, {}, {})".format(self.sprite_type(), self.layer_id(), self.uid())


class TriangleSprite(_Sprite):

    def __init__(self, points, layer_id, color=(1, 1, 1), depth=1, uid=None):
        _Sprite.__init__(self, SpriteTypes.TRIANGLE, layer_id, uid=uid)
        if len(points) != 3:
            raise ValueError("must have 3 points")

        # (._.)
        import src.engine.spritesheets as spritesheets
        self._model = spritesheets.get_instance().get_sheet(spritesheets.WhiteSquare.SHEET_ID).white_box

        self._points = points
        self._color = color
        self._depth = depth

    def points(self):
        return self._points

    def p1(self):
        return self._points[0]

    def p2(self):
        return self._points[1]

    def p3(self):
        return self._points[2]

    def color(self):
        return self._color

    def depth(self):
        return self._depth

    def update(self, new_points=None, new_color=None, new_depth=None):
        points = new_points if new_points is not None else self._points
        color = new_color if new_color is not None else self._color
        depth = new_depth if new_depth is not None else self._depth

        if (points == self._points and
                color == self._color and
                depth == self._depth):
            return self
        else:
            return TriangleSprite(points, self.layer_id(), color, depth, uid=self.uid())

    def add_urself(self, i, vertices, texts, colors, indices):
        p1 = self.p1()
        p2 = self.p2()
        p3 = self.p3()

        vertices[i * 6 + 0] = p1[0]
        vertices[i * 6 + 1] = p1[1]
        vertices[i * 6 + 2] = p2[0]
        vertices[i * 6 + 3] = p2[1]
        vertices[i * 6 + 4] = p3[0]
        vertices[i * 6 + 5] = p3[1]

        if colors is not None:
            rgb = self.color()
            for j in range(0, 9):
                colors[i * 9 + j] = rgb[j % 3]

        model = self._model
        if model is not None:
            for j in range(0, 3):
                texts[i * 6 + j * 2] = (model.tx1 + model.tx2) // 2
                texts[i * 6 + j * 2 + 1] = (model.ty1 + model.ty2) // 2

        indices[3 * i + 0] = 3 * i
        indices[3 * i + 1] = 3 * i + 1
        indices[3 * i + 2] = 3 * i + 2

    def __repr__(self):
        return "TriangleSprite({}, {}, {}, {}, {})".format(
             self.points(), self.layer_id(), self.color(), self.depth(), self.uid())
    

class ImageSprite(_Sprite):

    @staticmethod
    def new_sprite(layer_id, scale=1, depth=0):
        return ImageSprite(None, 0, 0, layer_id, scale=scale, depth=depth)

    def __init__(self, model, x, y, layer_id, scale=1, depth=1, xflip=False, rotation=0, color=(1, 1, 1), ratio=(1, 1), uid=None):
        _Sprite.__init__(self, SpriteTypes.IMAGE, layer_id, uid=uid)
        self._model = model
        self._x = x
        self._y = y
        self._scale = scale
        self._depth = depth
        self._xflip = xflip
        self._rotation = rotation
        self._color = color
        self._ratio = ratio
            
    def update(self, new_model=None, new_x=None, new_y=None, new_scale=None, new_depth=None,
               new_xflip=None, new_color=None, new_rotation=None, new_ratio=None):
                
        model = self.model() if new_model is None else new_model
        x = self.x() if new_x is None else new_x
        y = self.y() if new_y is None else new_y
        scale = self.scale() if new_scale is None else new_scale
        depth = self.depth() if new_depth is None else new_depth
        xflip = self.xflip() if new_xflip is None else new_xflip
        color = self.color() if new_color is None else new_color
        rotation = self.rotation() if new_rotation is None else new_rotation
        ratio = self.ratio() if new_ratio is None else new_ratio
        
        if (model == self.model() and 
                x == self.x() and 
                y == self.y() and
                scale == self.scale() and
                depth == self.depth() and 
                xflip == self.xflip() and
                color == self.color() and
                ratio == self.ratio() and
                rotation == self.rotation()):
            return self
        else:
            res = ImageSprite(model, x, y, self.layer_id(), scale=scale, depth=depth, xflip=xflip, rotation=rotation,
                              color=color, ratio=ratio, uid=self.uid())
            return res
        
    def model(self):
        return self._model
    
    def x(self):
        return self._x
        
    def y(self):
        return self._y
        
    def width(self):
        if self.model() is None:
            return 0
        elif self.rotation() % 2 == 0:
            return self.model().width() * self.scale() * self.ratio()[0]
        else:
            return self.model().height() * self.scale() * self.ratio()[1]
        
    def height(self):
        if self.model() is None:
            return 0
        elif self.rotation() % 2 == 0:
            return self.model().height() * self.scale() * self.ratio()[1]
        else:
            return self.model().width() * self.scale() * self.ratio()[0]

    def size(self):
        return (self.width(), self.height())

    def scale(self):
        return self._scale
        
    def depth(self):
        return self._depth
        
    def xflip(self):
        return self._xflip

    def rotation(self):
        """returns: int: 0, 1, 2, or 3 representing a number of clockwise 90 degree rotations."""
        return self._rotation
        
    def color(self):
        return self._color

    def ratio(self):
        return self._ratio
        
    def add_urself(self, i, vertices, texts, colors, indices):
        """
            i: sprite's "index", which determines where in the arrays its data is written.
        """
        x = self.x()
        y = self.y()

        model = self.model()
        if model is None:
            w = 0
            h = 0
        else:
            w = model.w * self.scale() * self.ratio()[0]
            h = model.h * self.scale() * self.ratio()[1]

        if self.rotation() == 1 or self._rotation == 3:
            temp_w = w
            w = h
            h = temp_w

        vertices[i*8 + 0] = x
        vertices[i*8 + 1] = y
        vertices[i*8 + 2] = x
        vertices[i*8 + 3] = y + h
        vertices[i*8 + 4] = x + w
        vertices[i*8 + 5] = y + h
        vertices[i*8 + 6] = x + w
        vertices[i*8 + 7] = y

        if colors is not None:
            rgb = self.color()
            for j in range(0, 12):
                colors[i * 12 + j] = rgb[j % 3]

        if model is not None:
            corners = [
                model.tx1, model.ty2,
                model.tx1, model.ty1,
                model.tx2, model.ty1,
                model.tx2, model.ty2
            ]

            if self.xflip():
                corners[0] = model.tx2
                corners[2] = model.tx2
                corners[4] = model.tx1
                corners[6] = model.tx1

            for _ in range(0, self.rotation()):
                corners = corners[2:] + corners[:2]

            for j in range(0, 8):
                texts[i * 8 + j] = corners[j]

        indices[6 * i + 0] = 4 * i
        indices[6 * i + 1] = 4 * i + 1
        indices[6 * i + 2] = 4 * i + 2
        indices[6 * i + 3] = 4 * i
        indices[6 * i + 4] = 4 * i + 2
        indices[6 * i + 5] = 4 * i + 3

    def __repr__(self):
        return "ImageSprite({}, {}, {}, {}, {}, {}, {}, {}, {}. {})".format(
                self.model(), self.x(), self.y(), self.layer_id(),
                self.scale(), self.depth(), self.xflip(), self.color(), self.ratio(), self.uid())


_CURRENT_ATLAS_SIZE = None  # XXX this is a mega hack, just look away please


class ImageModel:

    def __init__(self, x, y, w, h, offset=(0, 0), texture_size=None):
        # sheet coords, origin top left corner
        self.x = x + offset[0]
        self.y = y + offset[1]
        self.w = w
        self.h = h
        self._rect = (self.x, self.y, self.w, self.h)

        tex_size = texture_size if texture_size is not None else _CURRENT_ATLAS_SIZE
        if tex_size is None:
            raise ValueError("can't construct an ImageModel without a texture size")

        # texture coords, origin bottom left corner
        self.tx1 = self.x
        self.ty1 = tex_size[1] - (self.y + self.h)
        self.tx2 = self.x + self.w
        self.ty2 = tex_size[1] - self.y
        
    def rect(self):
        return self._rect
        
    def size(self):
        return (self.w, self.h)
        
    def width(self):
        return self.w
        
    def height(self):
        return self.h
        
    def __repr__(self):
        return "ImageModel({}, {}, {}, {})".format(self.x, self.y, self.w, self.h)



