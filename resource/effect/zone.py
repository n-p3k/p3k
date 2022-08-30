import numpy as np
import os
import itertools as it
import time

from pyrr import Matrix44
import moderngl
import moderngl_window as mglw
from moderngl_window import geometry

from geometry.mesh import *
from utils.path import *


class ProgramAssembler:
    def __init__(self, ctx, loader, filepath, theme="mody"):
        self.ctx = ctx
        self.mesh = None
        self.load_program(loader, theme)
        self.set_program_inputs()
        self.filepath = filepath
        self.create_vertex_data(filepath)

    def load_program(self, loader, theme):
        self.loader = loader
        self.prog = self.ctx.program(
            vertex_shader=self.load_vertex_shader(),
            fragment_shader=self.load_fragment_shader(theme),
        )

    def set_program_inputs(self):
        # buffer format needed by shader and used to create vbo
        self.vertex_buffer_format = '3f/i'
        self.vertex_buffer_name = 'in_move'

        # uniform names
        self.mvp = self.prog['Mvp']
        self.light = self.prog['Light']
  
    def create_vertex_data(self, filepath):
        """Harcoded unit cube (x = [-0.5, +0.5]))
           it will be stretched to +/ 64 by vertex shader.
        """
        scene_gpu = self.loader.load_scene(filepath)
        self.vao = scene_gpu.root_nodes[0].mesh.vao
        filepath = from_cache(filepath)
        mesh = MeshLoader().load(filepath)[0]
        self.mesh=mesh
        # TODO: for now get the vao from the loaded scene in stead of creating from cpu mesh
        # vao = create_vao_from_context_and_array(self.ctx, self.prog, mesh.verts, mesh.normals)

        # store the cpu mesh in the vao intended for gpu rendering
        self.vao.mesh = mesh

    def load_vertex_shader(self):
        vertex_shader='''
            #version 330

            uniform mat4 Mvp;

            vec3 in_move = vec3(0.0, 0.0, 0.0);

            in vec3 in_position;
            in vec3 in_normal;

            out vec3 v_vert;
            out vec3 v_norm;

            void main() {
                float s = 1.0;
                gl_Position = Mvp * vec4(s*in_position + in_move, 1.0);
                v_vert = in_position + in_move;
                v_norm = in_normal;
            }
            '''
        return vertex_shader

    def load_fragment_shader(self, name):

        f_shader_firepit='''
            #version 330

            uniform vec3 Light;

            in vec3 v_vert;
            in vec3 v_norm;

            out vec4 f_color;

            void main() {
                float dist = length((v_vert - 0))/255.0;
                float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.3 + 0.7;

                //float proximity = 1.0 - length(v_vert) / 255.0;
                lum = 1.0;

                // front red back blue
                float b = clamp(dist * 1.3, 0.0, 1.0);
                float r = 1.0 - b;
                f_color = vec4(lum*r, 0.1, lum*b, 1.0);

            }
        '''

        f_shader_modulated_y='''
            #version 330

            uniform vec3 Light;

            in vec3 v_vert;
            in vec3 v_norm;

            out vec4 f_color;

            void main() {
                float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.7 + 0.3;
                float b = 1.0 - (-(v_vert.z))/255.0;
                b *= 0.5;
                float dy = 15.0;
                float g = (int(abs(v_vert.y))%int(dy))/dy;
                float r = 1.0 - b;

                f_color = vec4(r, g, b, 1.0);
            }
        '''

        f_shader_illuminated='''
            #version 330

            uniform vec3 Light;

            in vec3 v_vert;
            in vec3 v_norm;

            out vec4 f_color;

            void main() {
                float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.7 + 0.3;
                float b = 0.0; //mod(v_vert.z - fract(v_vert.z), 2)/2;
                f_color = vec4(0.0, 1.0, b, 0.5);
            }
        '''
        fragment_shader = {
            'illuminated' : f_shader_illuminated,
            'mody' : f_shader_modulated_y,
            'firepit' : f_shader_firepit
        }
        return fragment_shader[name]

    
class Effect:
    def __init__(self, assembley, max_samples=1):
        self.name = "zone"
        self.program_assembley = assembley
        self.max_samples = max_samples
        self.on = {'fill' : False}

    def init(self):
        wo, ho, ww, hw = 224, 171, 255, 255
        # object to world matrix to multiply vy MVP before render
        w = ww/(wo-1)
        h = hw/(ho-1)
        d = 1
        self.obj_to_world = np.array([
            [w,0,0,0],
            [0,-h,0,0],
            [0,0,-d,0],
            [0,255,0,1]])
        self.vao_wrapper = self.program_assembley.vao
        self.init_dynamic_data()
        filepath = self.program_assembley.filepath
        # cpu mesh was previously loaded by gpu-program-assembler to create va in gpu
        mesh = self.program_assembley.mesh
        self.collider = MeshCollider(mesh)

    def init_dynamic_data(self):
        assembley = self.program_assembley

        # Add a new buffer into the VAO wrapper in the scene.
        # This is simply a collection of named buffers that is auto mapped
        # to attributes in the vertex shader with the same name.
        self.vbo = assembley.ctx.buffer(reserve=12 * self.max_samples, dynamic=True)

        self.vao_wrapper.buffer(self.vbo, assembley.vertex_buffer_format, assembley.vertex_buffer_name)
        # Create the actual vao instance (auto mapping in action)
        self.vao = self.vao_wrapper.instance(assembley.prog)

    def enable(self, on):
        for k in on.keys():
            self.on[k] = on[k] 

    def render(self, mvp_matrix, data=None, max_count=None):
        """Render with updated data, and transforming eye space to clip with MVP
           
           input:
               mvp : model view projection matrix (from model/world to clip)
               data : 3d point data with [0, N, 3] shape

        """ 
        M = mvp_matrix
        P = self.obj_to_world
        mvp_matrix = M * P 

        self.program_assembley.mvp.write(mvp_matrix.astype('f4').tobytes())
        self.program_assembley.light.value = (1.0, 1.0, 1.0)
        ctx = self.program_assembley.ctx

        #points = self.collider.check(data) # np.array([np.array([0, 0, 0])]) 
        points = np.array([np.array([0, 0, 0])]) 
        if points is not None:
            if max_count is None:
                max_count = len(points[0])
            self.vbo.clear()
            self.vbo.write(points.astype('f4').tobytes())
            if self.on['fill']:
                self.vao.render(instances=max_count, mode=moderngl.TRIANGLES)

            ctx.disable(moderngl.BLEND)
            self.vao.render(instances=max_count, mode=moderngl.LINE_STRIP)





