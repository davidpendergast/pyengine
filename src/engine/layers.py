from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

import src.engine.sprites as sprites
import src.utils.util as util


def assert_int(val):
    if not isinstance(val, int):
        raise ValueError("value is not an int: {}".format(val))


class _Layer:

    def __init__(self, layer_id, sprite_type, layer_depth, sort_sprites=True, use_color=True):
        """
            layer_id: The string identifier for this layer.
            sprite_type: The kinds of sprites this layer accepts.
            layer_depth: The depth of this layer, in relation to other layers in the engine.
            sort_sprites: Whether the sprites in this layer should be sorted by their depth.
            use_color: Whether this layer should use the color information in its sprites.
        """
        self._layer_id = layer_id
        self._sprite_type = sprite_type
        self._layer_depth = layer_depth

        self._sort_sprites = sort_sprites
        self._use_color = use_color

        self._offset = (0, 0)

    def get_layer_id(self):
        return self._layer_id

    def set_offset(self, x, y):
        self._offset = (x, y)

    def get_offset(self):
        return self._offset

    def is_sorted(self):
        return self._sort_sprites

    def is_color(self):
        return self._use_color

    def get_sprite_type(self):
        return self._sprite_type

    def get_layer_depth(self):
        return self._layer_depth

    def is_dirty(self):
        raise NotImplementedError()

    def get_num_sprites(self):
        raise NotImplementedError()

    def update(self, sprite_id):
        raise NotImplementedError()

    def remove(self, sprite_id):
        raise NotImplementedError()

    def rebuild(self, sprite_lookup):
        raise NotImplementedError()

    def render(self, engine):
        raise NotImplementedError()

    def __contains__(self, sprite_id):
        raise NotImplementedError()

    def __len__(self):
        return self.get_num_sprites()


class ImageLayer(_Layer):
    """
        Layer for ImageSprites.
    """

    def __init__(self, layer_id, layer_depth, sort_sprites=True, use_color=True):
        _Layer.__init__(self, layer_id, sprites.SpriteTypes.IMAGE, layer_depth,
                        sort_sprites=sort_sprites, use_color=use_color)

        self.images = []  # ordered list of image ids
        self._image_set = set()

        # these are the pointers the layer passes to gl
        self.vertices = numpy.array([], dtype=float)
        self.tex_coords = numpy.array([], dtype=float)
        self.indices = numpy.array([], dtype=float)
        self.colors = numpy.array([], dtype=float) if use_color else None

        self._dirty_sprites = []
        self._to_remove = []
        self._to_add = []

    def update(self, sprite_id):
        assert_int(sprite_id)
        if sprite_id in self._image_set:
            self._dirty_sprites.append(sprite_id)
        else:
            self._image_set.add(sprite_id)
            self._to_add.append(sprite_id)

    def remove(self, sprite_id):
        assert_int(sprite_id)
        if sprite_id in self._image_set:
            self._image_set.remove(sprite_id)
            self._to_remove.append(sprite_id)

    def is_dirty(self):
        return len(self._dirty_sprites) + len(self._to_add) + len(self._to_remove) > 0

    def rebuild(self, sprite_lookup):
        if len(self._to_remove) > 0:
            for sprite_id in self._to_remove:
                if sprite_id in self._image_set:
                    self._image_set.remove(sprite_id)

            util.Utils.remove_all_from_list_in_place(self.images, self._to_remove)
            util.Utils.remove_all_from_list_in_place(self._to_add, self._to_remove)
            self._to_remove.clear()

        if len(self._to_add) > 0:
            self.images.extend(self._to_add)
            self._to_add.clear()

        self._dirty_sprites.clear()

        if self.is_sorted():
            self.images.sort(key=lambda x: -sprite_lookup[x].depth())

        n_sprites = len(self.images)

        # need refcheck to be false or else Pycharm's debugger can cause this to fail (due to holding a ref)
        self.vertices.resize(8 * n_sprites, refcheck=False)
        self.tex_coords.resize(8 * n_sprites, refcheck=False)
        self.indices.resize(6 * n_sprites, refcheck=False)
        if self.is_color():
            self.colors.resize(4 * 3 * n_sprites, refcheck=False)

        for i in range(0, n_sprites):
            sprite = sprite_lookup[self.images[i]]
            sprite.add_urself(
                i,
                self.vertices,
                self.tex_coords,
                self.colors,
                self.indices)

    def render(self, engine):
        # split up like this to make it easier to find performance bottlenecks
        self._set_client_states(True, engine)
        self._pass_attributes(engine)
        self._draw_elements()
        self._set_client_states(False, engine)

    def _set_client_states(self, enable, engine):
        engine.set_vertices_enabled(enable)
        engine.set_texture_coords_enabled(enable)
        if self.is_color():
            engine.set_colors_enabled(enable)

    def _pass_attributes(self, engine):
        engine.set_vertices(self.vertices)
        engine.set_texture_coords(self.tex_coords)
        if self.is_color():
            engine.set_colors(self.colors)

    def _draw_elements(self):
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, self.indices)

    def __contains__(self, uid):
        return uid in self._image_set

    def num_sprites(self):
        return len(self.images)


