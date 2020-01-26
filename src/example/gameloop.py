import pygame

from src.utils.util import Utils
import src.engine.sounds as sounds
import src.engine.window as window
import src.engine.inputs as inputs
import src.engine.img as img
import src.engine.renderengine as renderengine

DEFAULT_SCREEN_SIZE = (800, 600)
MINIMUM_SCREEN_SIZE = (800, 600)


# REPLACE with real stuff, organized better
class DemoJunk:
    FLOOR_LAYER = "FLOORS"
    SHADOW_LAYER = "SHADOWS"
    WALL_LAYER = "WALLS"
    ENTITY_LAYER = "ENTITIES"

    tick_count = 0
    px_scale = -1

    @staticmethod
    def is_dev():
        return True

    camera_xy = (0, 0)
    cell_size = 32

    player_models = [img.ImageModel(0 + 16 * i, 0, 16, 32) for i in range(0, 2)]
    tv_models = [img.ImageModel(32 + 16 * i, 0, 16, 32) for i in range(0, 2)]
    floor_model = img.ImageModel(64, 16, 16, 16)
    wall_model = img.ImageModel(80, 16, 16, 16)
    shadow_model = img.ImageModel(64, 0, 16, 16)

    all_models = [floor_model, wall_model, shadow_model]
    all_models.extend(player_models)
    all_models.extend(tv_models)

    floor_positions = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
    floor_sprites = []

    wall_positions = [(0, 0), (1, 0), (2, 0)]
    wall_sprites = []

    entity_positions = [(0.5 * cell_size, 2.5 * cell_size), (2.5 * cell_size, 1.5 * cell_size)]
    entity_sprites = []

    shadow_sprites = []

    @staticmethod
    def all_bundles():
        for bun in DemoJunk.floor_sprites:
            yield bun
        for bun in DemoJunk.wall_sprites:
            yield bun
        for bun in DemoJunk.entity_sprites:
            yield bun
        for bun in DemoJunk.shadow_sprites:
            yield bun


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
    asset_sheet = pygame.image.load(Utils.resource_path("assets/assets.png"))

    texture_data = pygame.image.tostring(asset_sheet, "RGBA", 1)
    width = asset_sheet.get_width()
    height = asset_sheet.get_height()
    render_eng.set_texture(texture_data, width, height)

    # sprites will be upside down if this isn't done... sorry
    for spr in DemoJunk.all_models:
        spr.set_sheet_size((width, height))

    # REPLACE with whatever layers you need
    COLOR = True
    SORTS = True
    render_eng.add_layer(
        DemoJunk.FLOOR_LAYER,
        "floors", 0,
        False, COLOR)
    render_eng.add_layer(
        DemoJunk.SHADOW_LAYER,
        "shadow_layer", 5,
        False, COLOR)
    render_eng.add_layer(
        DemoJunk.WALL_LAYER,
        "walls", 10,
        False, COLOR)
    render_eng.add_layer(
        DemoJunk.ENTITY_LAYER,
        "entities", 15,
        SORTS, COLOR)

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
            options = [-1, 0.5, 1, 2, 3, 4]
            if current_scale in options:
                new_scale = (options.index(current_scale) + 1) % len(options)
            else:
                print("WARN: illegal pixel scale={}, reverting to default".format(current_scale))
                new_scale = options[0]
            DemoJunk.px_scale = new_scale

            display_size = window.get_instance().get_display_size()
            new_pixel_scale = _calc_pixel_scale(display_size)
            renderengine.get_instance().set_pixel_scale(new_pixel_scale)

        renderengine.get_instance().set_clear_color((0.66, 0.66, 0.66))

        # REPLACE with real updating
        update_crappy_demo_scene()

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


def update_crappy_demo_scene():
    if len(DemoJunk.entity_sprites) == 0:
        DemoJunk.entity_sprites.append(img.ImageBundle.new_bundle(DemoJunk.ENTITY_LAYER, scale=1))  # player
        DemoJunk.entity_sprites.append(img.ImageBundle.new_bundle(DemoJunk.ENTITY_LAYER, scale=1))  # tv

    if len(DemoJunk.wall_sprites) == 0:
        for pos in DemoJunk.wall_positions:
            new_bundle = img.ImageBundle(DemoJunk.wall_model,
                                         pos[0] * DemoJunk.cell_size,
                                         pos[1] * DemoJunk.cell_size,
                                         layer=DemoJunk.WALL_LAYER, scale=2)
            DemoJunk.wall_sprites.append(new_bundle)

    if len(DemoJunk.floor_sprites) == 0:
        for pos in DemoJunk.floor_positions:
            new_bundle = img.ImageBundle(DemoJunk.floor_model,
                                         pos[0] * DemoJunk.cell_size,
                                         pos[1] * DemoJunk.cell_size,
                                         layer=DemoJunk.FLOOR_LAYER, scale=2)
            DemoJunk.floor_sprites.append(new_bundle)

    if len(DemoJunk.shadow_sprites) == 0:
        for _ in DemoJunk.entity_sprites:
            DemoJunk.shadow_sprites.append(img.ImageBundle(DemoJunk.shadow_model, 0, 0, scale=1,
                                                           layer=DemoJunk.SHADOW_LAYER))

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
    new_model = DemoJunk.player_models[anim_tick % len(DemoJunk.player_models)]
    player_sprite = DemoJunk.entity_sprites[0]
    player_scale = player_sprite.scale()
    DemoJunk.entity_sprites[0] = player_sprite.update(new_model=new_model,
                                                      new_x=player_x - new_model.width() * player_scale // 2,
                                                      new_y=player_y - new_model.height() * player_scale,
                                                      new_xflip=new_xflip, new_depth=player_y)

    tv_model = DemoJunk.tv_models[(anim_tick // 2) % len(DemoJunk.tv_models)]
    tv_x = DemoJunk.entity_positions[1][0]
    tv_y = DemoJunk.entity_positions[1][1]
    tv_xflip = player_x > tv_x  # turn to face player
    tv_sprite = DemoJunk.entity_sprites[1]
    tv_scale = tv_sprite.scale()

    DemoJunk.entity_sprites[1] = tv_sprite.update(new_model=tv_model,
                                                  new_x=tv_x - tv_model.width() * tv_scale // 2,
                                                  new_y=tv_y - tv_model.height() * tv_scale,
                                                  new_xflip=tv_xflip, new_depth=tv_y)

    for i in range(0, len(DemoJunk.entity_positions)):
        xy = DemoJunk.entity_positions[i]
        shadow_sprite = DemoJunk.shadow_sprites[i]
        shadow_model = DemoJunk.shadow_model
        shadow_x = xy[0] - shadow_sprite.scale() * shadow_model.width() // 2
        shadow_y = xy[1] - shadow_sprite.scale() * shadow_model.height() // 2
        DemoJunk.shadow_sprites[i] = shadow_sprite.update(new_model=shadow_model,
                                                          new_x=shadow_x, new_y=shadow_y)

    # publishing new sprites to render engine
    for bun in DemoJunk.all_bundles():
        renderengine.get_instance().update(bun)

    # setting layer positions
    camera_x = player_x - renderengine.get_instance().get_game_size()[0] // 2
    camera_y = player_y - renderengine.get_instance().get_game_size()[1] // 2
    for layer_id in [DemoJunk.ENTITY_LAYER, DemoJunk.SHADOW_LAYER, DemoJunk.WALL_LAYER, DemoJunk.FLOOR_LAYER]:
        renderengine.get_instance().set_layer_offset(layer_id, camera_x, camera_y)

    #world = gs.get_instance().get_world()
    #if world is not None:
    #    if world_active:
    #        RenderEngine.get_instance().set_clear_color(*world.get_bg_color())

    #        world.update_all()
    #        world_view.update_all()

    #        gs.get_instance().dialog_manager().update(world)

    #        shake = gs.get_instance().get_screenshake()
    #        camera = gs.get_instance().get_actual_camera_xy()
    #        for layer_id in spriteref.WORLD_LAYERS:
    #            renderengine.get_instance().set_layer_offset(layer_id, *Utils.add(camera, shake))


    #    elif world_view is not None:
    #        world_view.cleanup_active_bundles()