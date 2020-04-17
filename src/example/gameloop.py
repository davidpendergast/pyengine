import pygame
import math
import random

from src.utils.util import Utils
import src.engine.sounds as sounds
import src.engine.window as window
import src.engine.inputs as inputs

import src.engine.sprites as sprites
import src.engine.renderengine as renderengine
import src.engine.layers as layers
import src.engine.spritesheets as spritesheets

DEFAULT_SCREEN_SIZE = (800, 600)
MINIMUM_SCREEN_SIZE = (800, 600)


# REPLACE with real stuff, organized better
class DemoJunk:
    FLOOR_LAYER = "FLOORS"
    SHADOW_LAYER = "SHADOWS"
    WALL_LAYER = "WALLS"
    ENTITY_LAYER = "ENTITIES"
    POLYGON_LAYER = "POLYGONS"
    UI_FG_LAYER = "UI_FG"
    UI_BG_LAYER = "UI_BG"

    world_layer_ids = [ENTITY_LAYER, SHADOW_LAYER, WALL_LAYER, FLOOR_LAYER, POLYGON_LAYER]
    ui_layer_ids = [UI_BG_LAYER, UI_FG_LAYER]

    tick_count = 0
    px_scale = -1
    px_scale_options = [-1, 1, 2, 3, 4]

    @staticmethod
    def is_dev():
        return True

    camera_xy = (0, 0)
    cell_size = 32

    floor_positions = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
    floor_sprites = []

    wall_positions = [(0, 0), (1, 0), (2, 0)]
    wall_sprites = []

    entity_positions = [(0.5 * cell_size, 2.5 * cell_size), (2.5 * cell_size, 1.5 * cell_size)]
    entity_sprites = []

    shadow_sprites = []

    triangle_center = (-32, 12)
    triangle_length = 20
    triangle_angle = 0
    triangle_color = (0, 0, 0)

    triangle_sprite = None

    cube_center = (-72, 80)
    cube_length = 40
    cube_angle = 0
    cube_color = (0, 0, 0)
    cube_line_thickness = 1

    cube_line_sprites = []

    fps_text_sprite = None
    title_text_sprite = None

    text_box_rect = [0, 0, 0, 0]
    text_box_sprite = None
    text_box_text_sprite = None

    @staticmethod
    def all_sprites():
        for spr in DemoJunk.floor_sprites:
            yield spr
        for spr in DemoJunk.wall_sprites:
            yield spr
        for spr in DemoJunk.entity_sprites:
            yield spr
        for spr in DemoJunk.shadow_sprites:
            yield spr
        if DemoJunk.triangle_sprite is not None:
            yield DemoJunk.triangle_sprite
        for spr in DemoJunk.cube_line_sprites:
            yield spr

        if DemoJunk.fps_text_sprite is not None:
            yield DemoJunk.fps_text_sprite
        if DemoJunk.title_text_sprite is not None:
            yield DemoJunk.title_text_sprite

        if DemoJunk.text_box_sprite is not None:
            yield DemoJunk.text_box_sprite
        if DemoJunk.text_box_text_sprite is not None:
            yield DemoJunk.text_box_text_sprite

    class DemoSheet(spritesheets.SpriteSheet):

        def __init__(self):
            spritesheets.SpriteSheet.__init__(self, "demo_sheet", "assets/assets.png")

            self.player_models = []
            self.tv_models = []
            self.floor_model = None
            self.wall_model = None
            self.shadow_model = None

            self.border_models = []

            self.all_models = []

        def draw_to_atlas(self, atlas, sheet, start_pos=(0, 0)):
            super().draw_to_atlas(atlas, sheet, start_pos=start_pos)

            self.player_models = [sprites.ImageModel(0 + 16 * i, 0, 16, 32, offset=start_pos) for i in range(0, 2)]
            self.tv_models = [sprites.ImageModel(32 + 16 * i, 0, 16, 32, offset=start_pos) for i in range(0, 2)]
            self.floor_model = sprites.ImageModel(64, 16, 16, 16, offset=start_pos)
            self.wall_model = sprites.ImageModel(80, 16, 16, 16, offset=start_pos)
            self.shadow_model = sprites.ImageModel(64, 0, 16, 16, offset=start_pos)

            self.border_models = []
            for y in range(0, 3):
                for x in range(0, 3):
                    self.border_models.append(sprites.ImageModel(96 + x * 8, 8 + y * 8, 8, 8, offset=start_pos))

            self.all_models = [self.floor_model, self.wall_model, self.shadow_model]
            self.all_models.extend(self.player_models)
            self.all_models.extend(self.tv_models)
            self.all_models.extend(self.border_models)

    demo_sheet = DemoSheet()


def init(name_of_game):
    print("INFO: pygame version: " + pygame.version.ver)
    print("INFO: initializing sounds...")
    pygame.mixer.pre_init(44100, -16, 1, 2048)

    pygame.mixer.init()
    pygame.init()

    window_icon = pygame.image.load(Utils.resource_path("assets/icon.png"))
    pygame.display.set_icon(window_icon)

    window.create_instance(window_size=DEFAULT_SCREEN_SIZE, min_size=MINIMUM_SCREEN_SIZE)
    window.get_instance().set_caption(name_of_game)
    window.get_instance().show()

    render_eng = renderengine.create_instance()
    render_eng.init(*DEFAULT_SCREEN_SIZE)
    render_eng.set_min_size(*MINIMUM_SCREEN_SIZE)

    # REPLACE with a call to a function that builds the real assets surface
    sprite_atlas = spritesheets.create_instance()
    sprite_atlas.add_sheet(DemoJunk.demo_sheet)

    atlas_surface = sprite_atlas.create_atlas_surface()

    # uncomment to save out the full texture atlas
    # pygame.image.save(atlas_surface, "texture_atlas.png")

    texture_data = pygame.image.tostring(atlas_surface, "RGBA", 1)
    width = atlas_surface.get_width()
    height = atlas_surface.get_height()
    render_eng.set_texture(texture_data, width, height)

    # REPLACE with whatever layers you need
    COLOR = True
    SORTS = True
    render_eng.add_layer(layers.ImageLayer(DemoJunk.FLOOR_LAYER, 0, False, COLOR))
    render_eng.add_layer(layers.ImageLayer(DemoJunk.SHADOW_LAYER, 5, False, COLOR))
    render_eng.add_layer(layers.ImageLayer(DemoJunk.WALL_LAYER, 10, False, COLOR))
    render_eng.add_layer(layers.PolygonLayer(DemoJunk.POLYGON_LAYER, 12, SORTS))
    render_eng.add_layer(layers.ImageLayer(DemoJunk.ENTITY_LAYER, 15, SORTS, COLOR))

    render_eng.add_layer(layers.ImageLayer(DemoJunk.UI_FG_LAYER, 20, SORTS, COLOR))
    render_eng.add_layer(layers.ImageLayer(DemoJunk.UI_BG_LAYER, 19, SORTS, COLOR))

    inputs.create_instance()

    px_scale = _calc_pixel_scale(DEFAULT_SCREEN_SIZE)
    render_eng.set_pixel_scale(px_scale)

    DemoJunk.px_scale = px_scale


def _calc_pixel_scale(screen_size, px_scale_opt=-1, max_scale=4):
    global DEFAULT_SCREEN_SIZE
    default_w = DEFAULT_SCREEN_SIZE[0]
    default_h = DEFAULT_SCREEN_SIZE[1]
    default_scale = 2

    screen_w, screen_h = screen_size

    if px_scale_opt <= 0:

        # when the screen is large enough to fit this quantity of (minimal) screens at a
        # particular scaling setting, that scale is considered good enough to switch to.
        # we choose the largest (AKA most zoomed in) "good" scale.
        step_up_x_ratio = 1.0
        step_up_y_ratio = 1.0

        best = default_scale
        for i in range(default_scale + 1, max_scale + 1):
            if (default_w / default_scale * i * step_up_x_ratio <= screen_w
                    and default_h / default_scale * i * step_up_y_ratio <= screen_h):
                best = i
            else:
                break

        return best
    else:
        return int(px_scale_opt)


def run():
    clock = pygame.time.Clock()
    running = True

    ignore_resize_events_next_tick = False

    while running:
        # processing user input events
        all_resize_events = []
        toggled_fullscreen = False

        input_state = inputs.get_instance()
        for py_event in pygame.event.get():
            if py_event.type == pygame.QUIT:
                running = False
                continue
            elif py_event.type == pygame.KEYDOWN:
                input_state.set_key(py_event.key, True)
            elif py_event.type == pygame.KEYUP:
                input_state.set_key(py_event.key, False)

            elif py_event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                scr_pos = window.get_instance().window_to_screen_pos(py_event.pos)
                game_pos = Utils.round(Utils.mult(scr_pos, 1 / renderengine.get_instance().get_pixel_scale()))
                input_state.set_mouse_pos(game_pos)

                if py_event.type == pygame.MOUSEBUTTONDOWN:
                    input_state.set_mouse_down(True, button=py_event.button)
                elif py_event.type == pygame.MOUSEBUTTONUP:
                    input_state.set_mouse_down(False, button=py_event.button)

            elif py_event.type == pygame.VIDEORESIZE:
                all_resize_events.append(py_event)

            if py_event.type == pygame.KEYDOWN and py_event.key == pygame.K_F4:
                toggled_fullscreen = True

            if not pygame.mouse.get_focused():
                input_state.set_mouse_pos(None)

        ignore_resize_events_this_tick = ignore_resize_events_next_tick
        ignore_resize_events_next_tick = False

        if toggled_fullscreen:
            # print("INFO {}: toggled fullscreen".format(gs.get_instance().tick_counter))
            win = window.get_instance()
            win.set_fullscreen(not win.is_fullscreen())

            new_size = win.get_display_size()
            new_pixel_scale = _calc_pixel_scale(new_size)
            if new_pixel_scale != renderengine.get_instance().get_pixel_scale():
                renderengine.get_instance().set_pixel_scale(new_pixel_scale)
            renderengine.get_instance().resize(new_size[0], new_size[1], px_scale=new_pixel_scale)

            # when it goes from fullscreen to windowed mode, pygame sends a VIDEORESIZE event
            # on the next frame that claims the window has been resized to the maximum resolution.
            # this is annoying so we ignore it. we want the window to remain the same size it was
            # before the fullscreen happened.
            ignore_resize_events_next_tick = True

        if not ignore_resize_events_this_tick and len(all_resize_events) > 0:
            last_resize_event = all_resize_events[-1]

            print("INFO: resizing to {}, {}".format(last_resize_event.w, last_resize_event.h))

            window.get_instance().set_window_size(last_resize_event.w, last_resize_event.h)

            display_w, display_h = window.get_instance().get_display_size()
            new_pixel_scale = _calc_pixel_scale((last_resize_event.w, last_resize_event.h))

            renderengine.get_instance().resize(display_w, display_h, px_scale=new_pixel_scale)

        input_state.update(DemoJunk.tick_count)
        sounds.update()

        if DemoJunk.is_dev() and input_state.was_pressed(pygame.K_F1):
            # used to help find performance bottlenecks
            import src.utils.profiling as profiling
            profiling.get_instance().toggle()

        if input_state.was_pressed(pygame.K_F5):
            current_scale = DemoJunk.px_scale
            options = DemoJunk.px_scale_options
            if current_scale in options:
                new_scale = (options.index(current_scale) + 1) % len(options)
            else:
                print("WARN: illegal pixel scale={}, reverting to default".format(current_scale))
                new_scale = options[0]
            DemoJunk.px_scale = new_scale

            display_size = window.get_instance().get_display_size()
            new_pixel_scale = _calc_pixel_scale(display_size, px_scale_opt=new_scale)
            renderengine.get_instance().set_pixel_scale(new_pixel_scale)

        renderengine.get_instance().set_clear_color((0.66, 0.66, 0.66))

        # REPLACE with real updating
        fps = clock.get_fps()
        update_crappy_demo_scene(fps)

        renderengine.get_instance().render_layers()
        pygame.display.flip()

        slo_mo_mode = DemoJunk.is_dev() and input_state.is_held(pygame.K_TAB)
        if slo_mo_mode:
            clock.tick(15)
        else:
            clock.tick(60)

        DemoJunk.tick_count += 1

        if DemoJunk.tick_count % 60 == 0:
            if clock.get_fps() < 55 and DemoJunk.is_dev() and not slo_mo_mode:
                print("WARN: fps drop: {} ({} sprites)".format(round(clock.get_fps() * 10) / 10.0,
                                                               renderengine.get_instance().count_sprites()))

    print("INFO: quitting game")
    pygame.quit()


def update_crappy_demo_scene(fps_for_display):
    if len(DemoJunk.entity_sprites) == 0:
        DemoJunk.entity_sprites.append(sprites.ImageSprite.new_sprite(DemoJunk.ENTITY_LAYER, scale=1))  # player
        DemoJunk.entity_sprites.append(sprites.ImageSprite.new_sprite(DemoJunk.ENTITY_LAYER, scale=1))  # tv

    if len(DemoJunk.wall_sprites) == 0:
        for pos in DemoJunk.wall_positions:
            new_sprite = sprites.ImageSprite(DemoJunk.demo_sheet.wall_model,
                                             pos[0] * DemoJunk.cell_size,
                                             pos[1] * DemoJunk.cell_size,
                                             DemoJunk.WALL_LAYER, scale=2)
            DemoJunk.wall_sprites.append(new_sprite)

    if len(DemoJunk.floor_sprites) == 0:
        for pos in DemoJunk.floor_positions:
            new_sprite = sprites.ImageSprite(DemoJunk.demo_sheet.floor_model,
                                             pos[0] * DemoJunk.cell_size,
                                             pos[1] * DemoJunk.cell_size,
                                             DemoJunk.FLOOR_LAYER, scale=2)
            DemoJunk.floor_sprites.append(new_sprite)

    if len(DemoJunk.shadow_sprites) == 0:
        for _ in DemoJunk.entity_sprites:
            DemoJunk.shadow_sprites.append(sprites.ImageSprite(DemoJunk.demo_sheet.shadow_model, 0, 0,
                                                               DemoJunk.SHADOW_LAYER, scale=1))

    if DemoJunk.triangle_sprite is None:
        DemoJunk.triangle_sprite = sprites.TriangleSprite(DemoJunk.POLYGON_LAYER, color=(0, 0, 0))

    while len(DemoJunk.cube_line_sprites) < 12:
        DemoJunk.cube_line_sprites.append(sprites.LineSprite(DemoJunk.POLYGON_LAYER, thickness=DemoJunk.cube_line_thickness))

    anim_tick = DemoJunk.tick_count // 16

    speed = 2
    dx = 0
    new_xflip = None
    if inputs.get_instance().is_held([pygame.K_a, pygame.K_LEFT]):
        dx -= speed
        new_xflip = False
    elif inputs.get_instance().is_held([pygame.K_d, pygame.K_RIGHT]):
        dx += speed
        new_xflip = True

    dy = 0
    if inputs.get_instance().is_held([pygame.K_w, pygame.K_UP]):
        dy -= speed
    elif inputs.get_instance().is_held([pygame.K_s, pygame.K_DOWN]):
        dy += speed

    player_x = DemoJunk.entity_positions[0][0] + dx
    new_y = DemoJunk.entity_positions[0][1] + dy
    player_y = max(new_y, int(1.1 * DemoJunk.cell_size))  # collision with walls~

    DemoJunk.entity_positions[0] = (player_x, player_y)
    new_model = DemoJunk.demo_sheet.player_models[anim_tick % len(DemoJunk.demo_sheet.player_models)]
    player_sprite = DemoJunk.entity_sprites[0]
    player_scale = player_sprite.scale()
    DemoJunk.entity_sprites[0] = player_sprite.update(new_model=new_model,
                                                      new_x=player_x - new_model.width() * player_scale // 2,
                                                      new_y=player_y - new_model.height() * player_scale,
                                                      new_xflip=new_xflip, new_depth=-player_y)

    tv_model = DemoJunk.demo_sheet.tv_models[(anim_tick // 2) % len(DemoJunk.demo_sheet.tv_models)]
    tv_x = DemoJunk.entity_positions[1][0]
    tv_y = DemoJunk.entity_positions[1][1]
    tv_xflip = player_x > tv_x  # turn to face player
    tv_sprite = DemoJunk.entity_sprites[1]
    tv_scale = tv_sprite.scale()

    DemoJunk.entity_sprites[1] = tv_sprite.update(new_model=tv_model,
                                                  new_x=tv_x - tv_model.width() * tv_scale // 2,
                                                  new_y=tv_y - tv_model.height() * tv_scale,
                                                  new_xflip=tv_xflip, new_depth=-tv_y)

    for i in range(0, len(DemoJunk.entity_positions)):
        xy = DemoJunk.entity_positions[i]
        shadow_sprite = DemoJunk.shadow_sprites[i]
        shadow_model = DemoJunk.demo_sheet.shadow_model
        shadow_x = xy[0] - shadow_sprite.scale() * shadow_model.width() // 2
        shadow_y = xy[1] - shadow_sprite.scale() * shadow_model.height() // 2
        DemoJunk.shadow_sprites[i] = shadow_sprite.update(new_model=shadow_model,
                                                          new_x=shadow_x, new_y=shadow_y)

    min_rot_speed = 0.3
    max_rot_speed = 4

    if DemoJunk.triangle_sprite is not None:
        tri_center = DemoJunk.triangle_center
        tri_angle = DemoJunk.triangle_angle * 2 * 3.141529 / 360
        tri_length = DemoJunk.triangle_length

        p1 = Utils.add(tri_center, Utils.rotate((tri_length, 0), tri_angle))
        p2 = Utils.add(tri_center, Utils.rotate((tri_length, 0), tri_angle + 3.141529 * 2 / 3))
        p3 = Utils.add(tri_center, Utils.rotate((tri_length, 0), tri_angle + 3.141529 * 4 / 3))

        DemoJunk.triangle_sprite = DemoJunk.triangle_sprite.update(new_points=(p1, p2, p3))

        player_dist = Utils.dist(DemoJunk.entity_positions[0], tri_center)
        if player_dist > 100:
            rot_speed = min_rot_speed
        else:
            rot_speed = Utils.linear_interp(min_rot_speed, max_rot_speed, (100 - player_dist) / 100)

        DemoJunk.triangle_angle += rot_speed

    text_inset = 4

    title_text = "Demo Scene"
    if DemoJunk.title_text_sprite is None:
        DemoJunk.title_text_sprite = sprites.TextSprite(DemoJunk.UI_FG_LAYER, 0, text_inset, title_text)

    title_text_width = DemoJunk.title_text_sprite.get_size()[0]
    title_text_x = renderengine.get_instance().get_game_size()[0] - title_text_width - text_inset
    DemoJunk.title_text_sprite = DemoJunk.title_text_sprite.update(new_x=title_text_x)

    if DemoJunk.fps_text_sprite is None:
        DemoJunk.fps_text_sprite = sprites.TextSprite(DemoJunk.UI_FG_LAYER, text_inset, text_inset, "FPS: 0")
    fps_text = "FPS: {}".format(int(fps_for_display))
    DemoJunk.fps_text_sprite = DemoJunk.fps_text_sprite.update(new_x=text_inset, new_y=text_inset, new_text=fps_text)

    player_to_tv_dist = Utils.dist(DemoJunk.entity_positions[0], DemoJunk.entity_positions[1])
    info_text = "There's something wrong with the TV. Maybe it's better this way." if player_to_tv_dist < 32 else None
    info_text_w = 400 - 32
    info_text_h = 48
    info_text_rect = [renderengine.get_instance().get_game_size()[0] // 2 - info_text_w // 2,
                      renderengine.get_instance().get_game_size()[1] - info_text_h - 16,
                      info_text_w, info_text_h]
    if info_text is None:
        if DemoJunk.text_box_text_sprite is not None:
            renderengine.get_instance().remove(DemoJunk.text_box_text_sprite)
            DemoJunk.text_box_text_sprite = None
        if DemoJunk.text_box_sprite is not None:
            renderengine.get_instance().remove(DemoJunk.text_box_sprite)
            DemoJunk.text_box_sprite = None
    else:
        wrapped_text = "\n".join(sprites.TextSprite.wrap_text_to_fit(info_text, info_text_rect[2]))
        if DemoJunk.text_box_text_sprite is None:
            DemoJunk.text_box_text_sprite = sprites.TextSprite(DemoJunk.UI_FG_LAYER, 0, 0, wrapped_text)
        DemoJunk.text_box_text_sprite = DemoJunk.text_box_text_sprite.update(new_x=info_text_rect[0],
                                                                             new_y=info_text_rect[1],
                                                                             new_text=wrapped_text)
        if DemoJunk.text_box_sprite is None:
            DemoJunk.text_box_sprite = sprites.BorderBoxSprite(DemoJunk.UI_BG_LAYER, info_text_rect,
                                                               all_borders=DemoJunk.demo_sheet.border_models)
        DemoJunk.text_box_sprite = DemoJunk.text_box_sprite.update(new_rect=info_text_rect, new_scale=2)

    if len(DemoJunk.cube_line_sprites) == 12:
        cube_center = DemoJunk.cube_center
        cube_angle = DemoJunk.cube_angle * 2 * 3.141529 / 360
        cube_length = DemoJunk.cube_length
        cube_color = DemoJunk.cube_color

        cube_top_pts = []
        cube_btm_pts = []

        for i in range(0, 4):
            dx = cube_length / 2 * math.cos(cube_angle + i * 3.141529 / 2)
            dy = cube_length / 2 * math.sin(cube_angle + i * 3.141529 / 2) / 2  # foreshortened in the y-axis
            cube_btm_pts.append(Utils.add(cube_center, (dx, dy)))
            cube_top_pts.append(Utils.add(cube_center, (dx, dy - cube_length)))

        for i in range(0, 12):
            if i < 4:  # bottom lines
                p1 = cube_btm_pts[i % 4]
                p2 = cube_btm_pts[(i + 1) % 4]
            elif i < 8:  # top lines
                p1 = cube_top_pts[i % 4]
                p2 = cube_top_pts[(i + 1) % 4]
            else:  # bottom to top lines
                p1 = cube_btm_pts[i % 4]
                p2 = cube_top_pts[i % 4]

            DemoJunk.cube_line_sprites[i].update(new_p1=p1, new_p2=p2, new_color=cube_color)

        player_dist = Utils.dist(DemoJunk.entity_positions[0], cube_center)
        if player_dist > 100:
            rotation_speed = min_rot_speed
        else:
            rotation_speed = Utils.linear_interp(min_rot_speed, max_rot_speed, (100 - player_dist) / 100)

        DemoJunk.cube_angle += rotation_speed

    # publishing new sprites to render engine
    for spr in DemoJunk.all_sprites():
        renderengine.get_instance().update(spr)

    # setting layer positions
    camera_x = player_x - renderengine.get_instance().get_game_size()[0] // 2
    camera_y = player_y - renderengine.get_instance().get_game_size()[1] // 2
    for layer_id in DemoJunk.world_layer_ids:
        renderengine.get_instance().set_layer_offset(layer_id, camera_x, camera_y)
