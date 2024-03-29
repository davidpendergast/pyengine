import pygame

import src.utils.util as util
import src.engine.sounds as sounds
import src.engine.window as window
import src.engine.inputs as inputs
import src.engine.keybinds as keybinds

import src.engine.renderengine as renderengine
import src.engine.spritesheets as spritesheets
import src.engine.globaltimer as globaltimer
import configs


_INSTANCE = None


def create_instance(game):
    global _INSTANCE
    if _INSTANCE is not None:
        raise ValueError("a game loop has already been created")
    else:
        _INSTANCE = _GameLoop(game)
        return _INSTANCE


class _GameLoop:

    def __init__(self, game):
        self._game = game
        self._clock = pygame.time.Clock()
        self._requested_fullscreen_toggle_this_tick = False
        self._slo_mo_timer = 0

        print("INFO: pygame version: " + pygame.version.ver)
        print("INFO: initializing sounds...")
        pygame.mixer.pre_init(44100, -16, 1, 2048)

        pygame.mixer.init()
        pygame.init()

        if configs.runtime_icon_path is not None:
            window_icon = pygame.image.load(util.resource_path(configs.runtime_icon_path))
            window_icon.set_colorkey((255, 0, 0))
        else:
            window_icon = None

        print("INFO: creating window...")
        window.create_instance(window_size=configs.default_window_size,
                               min_size=configs.minimum_window_size,
                               opengl_mode=not configs.start_in_compat_mode)
        window.get_instance().set_caption(configs.name_of_game)
        window.get_instance().set_icon(window_icon)
        window.get_instance().show()

        glsl_version_to_use = None
        if window.get_instance().is_opengl_mode():
            # make sure we can actually support OpenGL
            glsl_version_to_use = renderengine.check_system_glsl_version(or_else_throw=False)
            if glsl_version_to_use is None:
                window.get_instance().set_opengl_mode(False)

        print("INFO: creating render engine...")
        render_eng = renderengine.create_instance(glsl_version_to_use)
        render_eng.init(*configs.default_window_size)
        render_eng.set_min_size(*configs.minimum_window_size)

        inputs.create_instance()
        keybinds.create_instance()

        sprite_atlas = spritesheets.create_instance()

        for sheet in self._game.get_sheets():
            sprite_atlas.add_sheet(sheet)

        atlas_surface = sprite_atlas.create_atlas_surface()

        # uncomment for fun
        # import src.utils.artutils as artutils
        # artutils.rainbowfill(atlas_surface)

        # uncomment to save out the full texture atlas
        # pygame.image.save(atlas_surface, "texture_atlas.png")

        render_eng.set_texture_atlas(atlas_surface)

        for layer in self._game.get_layers():
            renderengine.get_instance().add_layer(layer)

        px_scale = window.calc_pixel_scale(window.get_instance().get_display_size())
        render_eng.set_pixel_scale(px_scale)

        self._game.initialize()

        if configs.is_dev:
            keybinds.get_instance().set_global_action(pygame.K_F1, "toggle profiling", lambda: self._toggle_profiling())

        if configs.allow_fullscreen:
            keybinds.get_instance().set_global_action(pygame.K_F4, "fullscreen",
                                                      lambda: self._request_fullscreen_toggle())

    def _toggle_profiling(self):
        # used to help find performance bottlenecks
        import src.utils.profiling as profiling
        profiling.get_instance().toggle()

    def _request_fullscreen_toggle(self):
        self._requested_fullscreen_toggle_this_tick = True

    def run(self):
        running = True

        ignore_resize_events_next_tick = False

        while running:
            # processing user input events
            all_resize_events = []

            input_state = inputs.get_instance()
            input_state.pre_update()

            for py_event in pygame.event.get():
                if py_event.type == pygame.QUIT:
                    running = False
                    continue
                elif py_event.type == pygame.KEYDOWN:
                    input_state.set_key(py_event.key, True, ascii_val=py_event.unicode)
                    keybinds.get_instance().do_global_action_if_necessary(py_event.key)

                elif py_event.type == pygame.KEYUP:
                    input_state.set_key(py_event.key, False)

                elif py_event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    scr_pos = window.get_instance().window_to_screen_pos(py_event.pos)
                    game_pos = util.round_vec(util.mult(scr_pos, 1 / renderengine.get_instance().get_pixel_scale()))
                    input_state.set_mouse_pos(game_pos)

                    if py_event.type == pygame.MOUSEBUTTONDOWN:
                        input_state.set_mouse_down(True, button=py_event.button)
                    elif py_event.type == pygame.MOUSEBUTTONUP:
                        input_state.set_mouse_down(False, button=py_event.button)

                elif py_event.type == pygame.VIDEORESIZE:
                    all_resize_events.append(py_event)

                if not pygame.mouse.get_focused():
                    input_state.set_mouse_pos(None)

            ignore_resize_events_this_tick = ignore_resize_events_next_tick
            ignore_resize_events_next_tick = False

            if self._requested_fullscreen_toggle_this_tick:
                # TODO I have no idea if this **** is still necessary in pygame 2+
                win = window.get_instance()
                win.set_fullscreen(not win.is_fullscreen())

                new_size = win.get_display_size()
                new_pixel_scale = window.calc_pixel_scale(new_size)
                if new_pixel_scale != renderengine.get_instance().get_pixel_scale():
                    renderengine.get_instance().set_pixel_scale(new_pixel_scale)
                renderengine.get_instance().resize(new_size[0], new_size[1], px_scale=new_pixel_scale)

                # when it goes from fullscreen to windowed mode, pygame sends a VIDEORESIZE event
                # on the next frame that claims the window has been resized to the maximum resolution.
                # this is annoying so we ignore it. we want the window to remain the same size it was
                # before the fullscreen happened.
                ignore_resize_events_next_tick = True

            self._requested_fullscreen_toggle_this_tick = False

            if not ignore_resize_events_this_tick and len(all_resize_events) > 0:
                last_resize_event = all_resize_events[-1]
                window.get_instance().set_window_size(last_resize_event.w, last_resize_event.h)

                display_w, display_h = window.get_instance().get_display_size()
                new_pixel_scale = window.calc_pixel_scale((last_resize_event.w, last_resize_event.h))

                renderengine.get_instance().resize(display_w, display_h, px_scale=new_pixel_scale)

            input_state.update()
            sounds.update()

            # updates the actual game state
            still_running = self._game.update()

            if still_running is False:
                running = False

            # draws the actual game state
            for spr in self._game.all_sprites():
                if spr is not None:
                    renderengine.get_instance().update(spr)

            renderengine.get_instance().set_clear_color(self._game.get_clear_color())
            renderengine.get_instance().render_layers()

            pygame.display.flip()

            slo_mo_mode = configs.is_dev and input_state.is_held(pygame.K_TAB)
            target_fps = configs.target_fps if not slo_mo_mode else configs.target_fps // 4

            dt = self._wait_until_next_frame(target_fps)

            globaltimer.set_dt(dt, target_dt=1000 / target_fps)
            globaltimer.inc_tick_count()

            if globaltimer.get_show_fps():
                if globaltimer.tick_count() % 20 == 0:
                    window.get_instance().set_caption_info("FPS", "{:.1f}".format(globaltimer.get_fps()))
            elif globaltimer.tick_count() % configs.target_fps == 0:
                if globaltimer.get_fps() < 0.9 * configs.target_fps and configs.is_dev and not slo_mo_mode:
                    print("WARN: fps drop: {} ({} sprites)".format(round(globaltimer.get_fps() * 10) / 10.0,
                                                                   renderengine.get_instance().count_sprites()))
            if slo_mo_mode:
                self._slo_mo_timer += 1
            elif self._slo_mo_timer > 0:
                # useful for timing things in the game
                print("INFO: slow-mo mode ended after {} tick(s)".format(self._slo_mo_timer))
                self._slo_mo_timer = 0

        self._game.cleanup()

        print("INFO: quitting game")
        pygame.quit()

    def _wait_until_next_frame(self, target_fps) -> int:
        if configs.precise_fps:
            return self._clock.tick_busy_loop(target_fps)
        else:
            return self._clock.tick(target_fps)






