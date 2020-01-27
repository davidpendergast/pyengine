# pyengine

Note: This has bugs, it's not well documented, and it's not very pleasant to use!

This was originally the core "engine" of [Skeletris](https://github.com/davidpendergast/skeletris), built on top of pygame, and I've extracted it here as a standalone resource. 

It sidesteps most of pygame's rendering API to interface directly with PyOpenGL instead. This means you can't use pygame-y stuff like pygame.draw, pygame.font, and direct surface manipulation / blitting to put stuff onto the screen. Instead, you basically load or create a massive spritesheet that contains all the sprites you'll ever need, bind it to the GPU, and work solely with those for the entire game. Then you set up "sprite layers", fill them with "sprite objects" (AKA sub-rectangles of the original sheet), and then each frame the game renders each layer (potentially containing hundreds of sprites) to the screen with a single draw call. In exchange for flexibily, you get speed. That's the idea anyways.

Some key features:
 - Quick and easy OpenGL setup, that supports on-the-fly pixel scale adjustment (renderengine.py).
 - A layer-based sprite rendering system (renderengine.py, layers.py, sprites.py).
 - Easier window creation, resizing, and fullscreen management (window.py).
 - Some helpful methods involving music & sounds (music.py + sounds.py). 
 - A more convenient way to handle keyboard + mouse inputs (inputs.py).
 
And there's a demo scene to help illustrate the setup (gameloop.py). 

This is what it should look like:

![demo](demo_scene.gif)
