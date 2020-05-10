
import os.path

name_of_game = "Demo Game"
version = "1.0.0"

default_window_size = (800, 600)  # size of window when the game starts.
minimum_window_size = (320, 120)  # if the window is smaller than this, it will begin cropping the picture.

optimal_window_size = (640, 240)
optimal_pixel_scale = 2  # how many screen pixels each "game pixel" will take up at the optimal window size.

auto_resize_pixel_scale = True  # whether to automatically update the pixel scale as the window grows and shrinks.
minimum_auto_pixel_scale = 1

target_fps = 60
precise_fps = False  # if enabled, will hog the CPU to ensure the frame rate is correct

is_dev = os.path.exists(".gitignore")  # elegant but yikes

