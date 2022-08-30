import os
import glob
import pathlib
import pywavefront
import struct
import numpy as np


def resource_location():
    """Get absolute resource folder"""
    p = pathlib.Path(__file__)
    default = p.parents[1]
    location = os.path.join(os.environ.get('P3_HOME', default), 'data')
    return location

def from_cache(uri):
    """Map uri to absolute path so that uri can be loaded from any folder."""
    location = resource_location()
    filepath = os.path.join(location,  uri)
    return filepath

def load_scene(scene_file, loader=None):
    if loader is not None:
        scene = loader.load_scene(scene_file)
    else:
        scene = None
    return scene



def create_gvo_from_scene(scene):
    """create a general cpu-gpu vao from a scene object"""
    gvo = {}
    gvo['vao'] = scene.root_nodes[0].mesh.vao

def create_vao_from_context_and_array(ctx, prog, verts, norms):
    """create vao from vertex position and normal array"""
    verts = verts.astype(np.float32)
    norms = norms.astype(np.float32)
    vx, vy, vz = verts[:,0], verts[:,1], verts[:,2]
    nx, ny, nz = norms[:,0], norms[:,1], norms[:,2]
    #packed_array = struct.pack('6f', vx, vy, vz, nx, ny, nz)

    packed_array = np.hstack((verts,norms))
    packed_array = verts
    vbo = ctx.buffer(packed_array)
    vao = ctx.simple_vertex_array(prog, vbo, 'in_position')
    return vao
