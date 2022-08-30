import numpy as np
import os
import itertools as it
import time

from pyrr import Matrix44
import moderngl
import moderngl_window as mglw
from moderngl_window import geometry

import resource.program.library as library


class ProgramAssembler:
    def __init__(self, ctx, loader, theme="mody"):
        self.ctx = ctx
        self.load_program(loader, theme)
        self.set_program_inputs()
        self.create_vertex_data()

    def load_program(self, loader, theme):
        self.loader = loader
        vp = library.VertexProgram()
        fp = library.FragmentProgram()
        self.prog = self.ctx.program(
            vertex_shader=vp.shader['mvp']['offset'],
            fragment_shader=fp.shader[theme],
        )

    def set_program_inputs(self):
        # buffer format needed by shader and used to create vbo
        self.vertex_buffer_format = '3f/i'
        self.vertex_buffer_name = 'in_move'

        # uniform names
        self.mvp = self.prog['Mvp']
        self.light = self.prog['Light']
  
    def create_vertex_data(self):
        self.scene = self.loader.load_scene('cube.obj')
        self.vao = self.scene.root_nodes[0].mesh.vao

class Effect:
    def __init__(self, assembley, max_samples=320*240):
        self.name = "pointcloud"
        self.program_assembley = assembley
        self.max_samples = max_samples

    def init(self):
        self.vao_wrapper = self.program_assembley.vao
        self.init_dynamic_data()

    def init_dynamic_data(self):
        assembley = self.program_assembley

        # Add a new buffer into the VAO wrapper in the scene.
        # This is simply a collection of named buffers that is auto mapped
        # to attributes in the vertex shader with the same name.
        self.vbo = assembley.ctx.buffer(reserve=12 * self.max_samples, dynamic=True)

        self.vao_wrapper.buffer(self.vbo, assembley.vertex_buffer_format, assembley.vertex_buffer_name)
        # Create the actual vao instance (auto mapping in action)
        self.vao = self.vao_wrapper.instance(assembley.prog)

    def render(self, mvp_matrix, data=None, max_count=None):
        """Render with updated data, and transforming eye space to clip with MVP
           
           input:
               mvp : model view projection matrix (from model/world to clip)
               data : 3d point data with [0, N, 3] shape

        """
        self.program_assembley.mvp.write(mvp_matrix.astype('f4').tobytes())
        self.program_assembley.light.value = (1.0, 1.0, 1.0)

        points = data
        if points is not None:
            if max_count is None:
                max_count = len(points[0])
            self.vbo.clear()
            self.vbo.write(points.astype('f4').tobytes())
            self.vao.render(instances=max_count)





