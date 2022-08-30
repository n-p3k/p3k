import numpy as np
import os
import pathlib
import cv2
import os
import itertools as it
import glob
import time

from pyrr import Matrix44
import moderngl
import moderngl_window as mglw
from moderngl_window import geometry

import resource.effect.pointcloud
import resource.effect.zone 
import transform.frame as tf
from utils.m import *
from utils import path

class Dataset:
    def __init__(self, op, dataset_name='default'):
        self.name = dataset_name
        self.volume = op['render_volume']
 
    def load_point_data(self, filepath='data/depth8.png'):
        """Load depth8 image (rs cs) to opengl cordinate system"""
        depth8 = cv2.imread(filepath)[:,:,0]
        W, H, D = self.volume

        # resample to desired observed volume resolution            
        depth8 = cv2.resize(depth8, (W, H), interpolation=cv2.INTER_NEAREST)
        h, w = depth8.shape
        d = 1

        # transform x,y,z to int32, int32, float64 (needed to match frustum coord space)
        x = np.tile(np.arange(w), w).flatten()
        y = np.repeat(np.arange(h), h).flatten()
        z = depth8.flatten() * 1.0
    
        # remove z too close, adjust x,y to remove entire point
        min_z, max_z = 0, 255 
        x = x[z>min_z]
        y = y[z>min_z]
        z = z[z>min_z]

        x, y, z = tf.xyz_device_to_eye_gl(x,y,z, [w, h, max_z])
     
        # scale z as per desired volume requirements
        factor = D/max_z
        z = (z.astype(dtype=np.float64) * factor )

        pts = np.dstack([x, y, z])
        return pts, w*h, (w, h, d)

    def gen_point_data(self):
        W, H, D = self.volume
        w, h, d = W, D, 1
        num_samples = w*h
        x = (np.tile(np.arange(w), w)) 
        y = (np.repeat(np.arange(h), h))
        z = np.random.randint(0, 255, d*d) * 1.0

        x, y, z = tf.xyz_device_to_eye_gl(x,y,z) 
        coordinates = np.dstack([x, y, z*D/255])

        return coordinates, w*h, (w, h, d)


class Window(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "pc3"
    window_size = (2*640, 2*480)
    aspect_ratio = window_size[0] / window_size[1]
    resizable = True
    samples = 0

    resource_dir = os.path.normpath(os.path.join(__file__, '../data'))
    print('res dir: ', resource_dir)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)


class Camera:
    def __init__(self, op, win_size):
        self.aspect_ratio = win_size[0] / win_size[1]
        self.win = win_size
        self.volume = op['render_volume']
        self.reset()

    def reset(self):
        W, H, D = self.volume
        self.world_size = vec3(W, H, D)
        self.world_size = vec3(256, 256, 256)
        self.cam_o = vec3(128, 128, 64)
        self.cam_o = vec3(128, 128, 64)
        self.fov = 90.0
        self.cam_o = vec3(W/2, H/2, D/4)
        self.cam_pos = self.cam_o
        self.cam_target = vec3(W/2, H/2, -D/2) 
        self.cam_target = vec3(128, 128, -128)
        self.cam_up = [0, 1, 0]
        self.stepper = [0, 0, 0]
        self.speed = 1.0
        self.shift = {
            'vec' : np.array([0, 0, 0]),
            'scaler': np.array([0.03, 0.01, 0.01])
        }
        self.step_with_target = False 

        self.op = {}
        self.op['proj'] = 'ortho'
        self.op['layer'] = 'free'
        self.op['modulation'] = 'none'
        self.op['scale']= 0.25 
        self.op['fps'] = 30
        self.velocity = {
            'boost' : 3.4,
            'decay' : 0.21
        }
    
    def orbit(self, t):
        """Make camera orbit around a path."""
        angle = self.op['scale'] * (t)*np.pi/2 
        r = 230 #t #self.win[0]/8 #max(self.win[0], self.win[1]) / 2
        pos = np.array([np.cos(angle)*r,  28 , np.sin(angle)*r])
        self.cam_target = vec3(128, 128, -128) 
        self.cam_pos = pos + self.cam_target

    def view(self, viewpoint):
        print(viewpoint)
        if viewpoint == "front_top":
            self.cam_target = vec3(128, 128, -128) 
            self.cam_pos = vec3(128, 356, -128)

    def disparity_shift(self, t):
        if self.op['layer'] in  ["free"]:
            sx = (50 - np.random.randint(0, 100)) * self.shift['scaler'][0] 
            sy = (50 - np.random.randint(0, 100)) * self.shift['scaler'][1]
            sz = (50 - np.random.randint(0, 100)) * self.shift['scaler'][2] 
            self.shift['vec'] = np.array([sx, sy, sz])
        elif self.op['layer'] in ["orbit"]:
            shift = float(int(t*100) % 3 - 1)
            shift *= 1
            self.cam_pos[1] += shift
            self.cam_target[1] += shift/2
        else:
            self.shift['vec']= np.array([0,0,0])

    def step(self, t):
        """Step through motion trajectory."""
        if self.op['layer'] == "free":
            #self.speed = 2 #self.op['scale']
            for dim in range(3):
                # distance in one axis
                step = float(self.stepper[dim])
                dist = self.speed*step

                self.cam_pos[dim] += (dist)
                if self.step_with_target:
                    self.cam_target[dim] += (dist)

            # slow down at a given decay
            self.speed = max(self.speed - self.velocity['decay'], 0) 
            #self.cam_pos = self.cam_o
        elif self.op['layer'] == "orbit":
            self.orbit(t) 
        if self.op['modulation'] == "disparity":
            self.disparity_shift(t)

    def axis_slide(self, axis, deltas):
        """Slide along one or more axis."""

        # boost speed at command, as it is going to decay
        self.speed += self.velocity['boost'] 

        ax = {'z' : 2, 'y' : 1, 'x' : 0}
        self.stepper = [0,0,0]
        for a, d in zip(axis, deltas):
            self.stepper[ax[a]] = float(d)
        self.step_with_target = False 

    def axis_trans(self, axis, deltas):
        """Slide along one or more axis."""
        self.axis_slide(axis, deltas)
        self.step_with_target = True

    def update_pose(self, t):
        self.step(t)

        self.lookat = Matrix44.look_at(self.cam_pos+self.shift['vec'], self.cam_target, self.cam_up)
        if self.op['proj'] == 'perp':
            self.proj = Matrix44.perspective_projection(self.fov, self.aspect_ratio, 0.1, 5000.0)
        else: 
            a=1024*self.op['scale']
            self.proj = Matrix44.orthogonal_projection(-a, a, -a, a, -a*4, a*4) 
        return self.mvp()

    def mvp(self):
        return self.proj * self.lookat

class PC3(Window):
    '''
    Point Cloud 
    '''
    title = "p3rc3ption engine"
    gl_version = (3, 4)

    def load_config(self):
        cfg = { 
            "op" : 
            {
            'theme' : 'dark_to_bright', 
            'collider' : 'off',
            'collider_selection' : 0, # all zone selected
            "xray" : "off",
            "clear_color" : [.008, 0.09, 0.16],
            "render_volume" : [256, 256, 256],
            "-":"",
            }
        }
        return cfg 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.off = {'x' : 0, 'y' : 0 ,'z' : 0}
        self.time = dict.fromkeys({'render', 'render:load'}, 0)
        self.cfg = self.load_config() 
        self.op = self.cfg['op']
        self.cam = Camera(self.op, PC3.window_size)

        def get_mesh_files():
            meshpattern = os.environ.get('P3_MESHPATH', False)
            mask_pattern = os.environ.get('P3_MASKPATTERN', "*")
            meshfiles = []
            if meshpattern:
                meshfiles = glob.glob(meshpattern)

            def pass_mask(f, mask_pattern):
                if mask_pattern == '' or mask_pattern == '*':
                    return True
                return len(f.split(mask_pattern)) == 1

            def pass_single_dot(f):
                return len(f.split('.')) <= 2

            # remove files that mgl cannot handle
            flatfiles = list()
            print('\n\n\n')
            print("....................... MESH FILE ..................................")
            for f in meshfiles:
                if pass_single_dot(f) and pass_mask(f, mask_pattern):
                    parent = os.getcwd() 

                    # mgl cannot handle local file from other launch folder, need absolute path 
                    if os.path.isabs(f) is False:
                        f = os.path.join(parent, f)

                    # mgl cannot handle window abs path, turn into posix
                    mesh_file = pathlib.PurePath(f).as_posix()

                    # mgl cannot handle drive letter C:/path/
                    mesh_file = mesh_file.split(":")[-1]

                    print(" ********* {0} *********".format(mesh_file))
                    flatfiles.append(mesh_file)
            print("...................................................................")
            print('\n\n\n')

            return flatfiles

        mesh_files = get_mesh_files()

        pattern = os.environ.get('PC3_FILEPATH', False)
        if pattern is False:
            print("specify input file in PC3_FILEPATH") 
            exit(0)
        self.filepath = it.cycle(glob.glob(pattern))
        ds = Dataset(self.op)
        try:
            self.points, self.num_samples, self.dim = ds.load_point_data(next(self.filepath))
        except:
            self.points = np.array([np.array([0,0,0])]).astype(np.float64) 
            self.num_samples = 1
            W, H, D = self.op['render_volume']
            self.dim = (W, H, 1) 

        def add_effect(e, effect, effect_name, num_samples):
            theme = {'mody' : 'mody', 'firepit' : 'firepit', 'zone':'illuminated',
                'dark_to_bright' : 'dark_to_bright'}
            progasm = effect.ProgramAssembler(self.ctx, self, theme[effect_name])
            e[effect_name] = effect.Effect(progasm, num_samples)
            e[effect_name].init()

        def add_zone(e, effect, mesh_path):
            """add zone effect zone.Effect and built it from mesh_path """
            effect_name = 'zone'
            progasm = effect.ProgramAssembler(self.ctx, self, mesh_path, 'illuminated')
            e[effect_name].append(effect.Effect(progasm, 1))
            e[effect_name][-1].init()

        self.e = {'zone' : list()}
        add_effect(self.e, resource.effect.pointcloud, 'mody', self.num_samples)
        add_effect(self.e, resource.effect.pointcloud, 'firepit', self.num_samples)
        add_effect(self.e, resource.effect.pointcloud, 'dark_to_bright', self.num_samples)

        # build default collider zone
        default_zone_filepath = 'zone.obj'
        add_zone(self.e, resource.effect.zone, default_zone_filepath)

        for mesh_file in mesh_files:
            try:
                add_zone(self.e, resource.effect.zone, mesh_file)
            except Exception as e:
                print("\n\n*****************************************")
                print("  --- ERROR --- could not create Zone Effect with meshfile {0}".format(mesh_file))
                print(str(e))
                print("************ -- END OF ERROR --- ********\n\n")

    def set_blending(self):
        #self.ctx.blend_func = moderngl.ADDITIVE_BLENDING
        #self.ctx.blend_func = moderngl.PREMULTIPLIED_ALPHA
        #self.ctx.blend_func = moderngl.DEFAULT_BLENDING
        self.ctx.blend_equation = moderngl.FUNC_ADD
        self.ctx.blend_equation = moderngl.MAX

    def update_frame_data(self):
        """Update points data at each frame.

           Step through frames or change continous fps: 
           # fps = inf  : step frame
           # fps = 0    : pause
           # fps = 1    : 1 fps
           # fps = 30   : 30 fps
        """
        if self.cam.op['fps'] == np.inf:
            self.cam.op['fps'] = 0
            update_frame = True
        elif self.cam.op['fps'] != 0 and (time.time()-self.time['render:load']) > (1/self.cam.op['fps']): 
            update_frame = True
        else:
            update_frame = False

        if update_frame is True:
            try:
                filepath = next(self.filepath)
                print(filepath)
                self.points, self.num_samples, self.dim = Dataset(self.op).load_point_data(filepath)
                self.time['render:load'] = time.time()
            except:
                pass
 
    def render(self, t, frame_time):
        c0, c1, c2 = self.op['clear_color']
        self.ctx.clear(c0, c1, c2)

        self.update_frame_data()
        mvp = self.cam.update_pose(t)

        if self.op['xray'] == 'off':
            self.ctx.enable(moderngl.DEPTH_TEST)
            self.ctx.disable(moderngl.BLEND)
        else:
            self.ctx.enable(moderngl.DEPTH_TEST | moderngl.BLEND)
            self.ctx.blend_equation = moderngl.MAX

        # collision detection (theme=zone) 
        if self.op['theme'] == 'zone':
            for n, zone in enumerate(self.e['zone']):
                sel = self.op['collider_selection']
                # select all or active zone id
                if  sel == 0 or sel == (n + 1): 
                    zone.render(mvp, self.points)
                    points = zone.collider.check(self.points[0,:,:])
                    # mody, dark_to_bright, firepit
                    self.e['firepit'].render(mvp, points)
        else:
            self.e[self.op['theme']].render(mvp, self.points)

        if self.op['xray'] != 'off':
            self.ctx.enable(moderngl.DEPTH_TEST | moderngl.BLEND)
        elif self.op['xray'] == 'seethru':
            ctx.blend_equation = moderngl.FUNC_ADD
        elif self.op['xray'] == 'translucent':
            ctx.blend_equation = moderngl.MAX

        if self.op['collider'] != 'off':
            for n, zone in enumerate(self.e['zone']):
                sel = self.op['collider_selection']
                zone_id = n + 1
                # select all or just the active zone id
                if sel == 0 or sel == zone_id: 
                    zone.enable({'fill':self.op['collider']=='fill'})
                    zone.render(mvp)


        self.time['render'] = time.time()

