import itertools as it
import numpy as np
from pc3_engine import PC3

class Viewer(PC3):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.o = dict()
        self.o['proj']  = it.cycle(['perp', 'ortho']) 
        self.o['theme'] = it.cycle(['mody', 'firepit', 'dark_to_bright', 'zone'])
        self.o['clear_color']  = it.cycle([[0.008, 0.08, 0.16], [0.5, 0.6, 1.0]]) 
        self.o['collider'] = it.cycle(['off', 'zone', 'fill'])
        self.o['xray'] = it.cycle(['off', 'seethru', 'translucent'])
        self.o['layer']  = it.cycle(['free', 'orbit']) 
        self.o['modulation']  = it.cycle(['none', 'disparity']) 
        self.o['fps']  = it.cycle([30, 1, 0]) 
        self.o['scale'] = it.cycle([0.5, 0.25, 0.125, 0.0625, 0.03, 1]) 

    def key_event(self, key, action, modifiers):
        # Key presses
        if action == self.wnd.keys.ACTION_PRESS:

            if modifiers.shift:
                if key == self.wnd.keys.SPACE:
                    self.cam.reset()

            elif  modifiers.ctrl:
                if key == self.wnd.keys.S:
                    self.cam.op['scale'] = next(self.o['scale']) 

                if key == self.wnd.keys.P:
                    self.cam.op['proj'] = next(self.o['proj']) 

                if key == self.wnd.keys.O:
                    self.cam.op['layer'] = next(self.o['layer']) 

                if key == self.wnd.keys.M:
                    self.cam.op['modulation'] = next(self.o['modulation']) 

                if key == self.wnd.keys.F:
                    self.cam.op['fps'] = next(self.o['fps'])

            else:

                if key == self.wnd.keys.S:
                    self.cam.axis_slide(['z'], [1])

                if key == self.wnd.keys.W:
                    self.cam.axis_slide(['z'], [-1])

                if key == self.wnd.keys.NUMBER_2:
                    self.cam.axis_slide(['z'], [1])

                if key == self.wnd.keys.NUMBER_5:
                    self.cam.axis_slide(['z'], [-1])

                if key == self.wnd.keys.A:
                    self.cam.axis_trans(['x'], [-1])

                if key == self.wnd.keys.D:
                    self.cam.axis_trans(['x'], [+1])

                if key == self.wnd.keys.NUMBER_1:
                    self.cam.axis_slide(['x'], [1])

                if key == self.wnd.keys.NUMBER_3:
                    self.cam.axis_slide(['x'], [-1])


                if key == self.wnd.keys.Q:
                    self.cam.axis_trans(['y'], [-1])

                if key == self.wnd.keys.E:
                    self.cam.axis_trans(['y'], [1])

                if key == self.wnd.keys.NUMBER_4:
                    self.cam.axis_slide(['y'], [-1])

                if key == self.wnd.keys.NUMBER_6:
                    self.cam.axis_slide(['y'], [1])


                if key == self.wnd.keys.NUMBER_8:
                    self.cam.view('front_top')

                if key == self.wnd.keys.V:
                    zone = self.e['zone']
                    self.op['collider_selection'] = (self.op['collider_selection'] + 1) % (len(zone) + 1)
                    print(self.op['collider_selection'], len(zone))

                if key == self.wnd.keys.T:
                    self.op['theme'] = next(self.o['theme']) 

                if key == self.wnd.keys.B:
                    self.op['clear_color'] = next(self.o['clear_color']) 

                if key == self.wnd.keys.C:
                    self.op['collider'] = next(self.o['collider']) 

                if key == self.wnd.keys.X:
                    self.op['xray'] = next(self.o['xray']) 

                if key == self.wnd.keys.I:
                    print("cam_pos: " + str(self.cam.cam_pos))
                    print("cam_tar: " + str(self.cam.cam_target))

                if key == self.wnd.keys.F:
                    # fps=inf : 1 frame then stop to fps=0 
                    self.cam.op['fps'] = np.inf 

        elif action == self.wnd.keys.ACTION_RELEASE:
            if key == self.wnd.keys.SPACE:
                self.cam.axis_slide(['x','y','z'], [0,0,0])

    #def mouse_position_event(self, x, y):
    #    print("Mouse position:", x, y)

    def mouse_drag_event(self, x, y):
        print("Mouse drag:", x, y)

    def mouse_scroll_event(self, x_offset, y_offet):
        print("mouse_scroll_event", x_offset, y_offet)

    def mouse_press_event(self, x, y, button):
        print("Mouse button {} pressed at {}, {}".format(button, x, y))
        print("Mouse states:", dir(self.wnd))

    def mouse_release_event(self, x: int, y: int, button: int):
        print("Mouse button {} released at {}, {}".format(button, x, y))
        print("Mouse states:", dir(self.wnd))

def main():
    Viewer.run()

if __name__ == '__main__':
    main()