# -*- coding: utf-8 -*-
from __future__ import absolute_import

import numpy as np
import cv2
import pyglet
from pyglet import gl
from array import array
from random import random

import imgui
from imgui.integrations.pyglet import PygletRenderer

import OpenGL.GL as ogl
import datashare


sh = {}
sh['debug'] = datashare.DataShare('/tmp/debug')
sh['render'] = datashare.DataShare('render')


def rgb_to_texid(img_rgb):
    """
    Performs the actual transfer to the gpu and returns a texture_id
    """
    # inspired from https://www.programcreek.com/python/example/95539/Openogl.ogl.glPixelStorei (example 3)
    width = img_rgb.shape[1]
    height = img_rgb.shape[0]
    texture_id = ogl.glGenTextures(1)
    ogl.glPixelStorei(ogl.GL_UNPACK_ALIGNMENT, 1)
    ogl.glBindTexture(ogl.GL_TEXTURE_2D, texture_id)
    ogl.glPixelStorei(ogl.GL_UNPACK_ALIGNMENT, 1)
    ogl.glTexParameteri(ogl.GL_TEXTURE_2D, ogl.GL_TEXTURE_MAG_FILTER, ogl.GL_LINEAR)
    ogl.glTexParameteri(ogl.GL_TEXTURE_2D, ogl.GL_TEXTURE_MIN_FILTER, ogl.GL_LINEAR)
    ogl.glTexImage2D(ogl.GL_TEXTURE_2D, 0, ogl.GL_RGB, width, height, 0, ogl.GL_BGR, ogl.GL_UNSIGNED_BYTE, img_rgb)
    ogl.glBindTexture(ogl.GL_TEXTURE_2D, 0)
    return texture_id



def main():

    window = pyglet.window.Window(width=640, height=480, resizable=True)
    gl.glClearColor(1, 1, 1, 0.0)
    imgui.create_context()
    impl = PygletRenderer(window)
    io = imgui.get_io()
    io.fonts.add_font_default()

    rgb = np.random.randint(0, 255, (60,40,3))
    texture_id = rgb_to_texid(rgb)


    def update(dt):
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("commands", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Exit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()


        imgui.begin("control")
        imgui.push_style_var(imgui.STYLE_ALPHA, 0.8)

        if imgui.checkbox('learnable', True):
            if imgui.color_button("p0", 0.1, 1, 0.1, .7, 0, 10, 10):
                imgui.color_button("p1", 0.3, 1, 0.2, .7, 0, 10, 10)



        value = 42.0
        changed, value = imgui.drag_float(
            "Less precise", value, format="%.1f"
        )
        imgui.text("Changed: %s, Value: %s" % (changed, value))
        imgui.image(texture_id, 64, 64, border_color=(1, 0, 0, 1))        
        imgui.text_colored("text colored", 0.9, 0.0, 0.0)

        if imgui.button('randomize', width=100):
            print('randomize!')
        imgui.button('optimize', 100)
        imgui.button('edit', 200)

        imgui.pop_style_var(1)

        imgui.end()

    @window.event
    def on_draw():
        update(1/60.0)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()