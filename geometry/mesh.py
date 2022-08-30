import pywavefront
import numpy as np
import glob
from utils.path import * 


def load_wavefront_scene(scene_filepath):
    """Load scene in wavefront obj file
       see https://github.com/pywavefront/PyWavefront
    """
    scene = pywavefront.Wavefront(scene_filepath, create_materials=True, collect_faces=True)
    faces = list()
    faces.append(scene.mesh_list[0].faces)

    # format size for each interleaved vertex format
    elems_per_vertex = {}
    elems_per_vertex['C3F_N3F_V3F'] = 9

    # vertex offest where each attribute is found
    pos = 6
    nor = 3
    col = 0

    # groups of vertices and normals (usually only 1)
    verts = list()
    norms = list()
    for name, material in scene.materials.items():
        # Contains the vertex format (string) such as "T2F_N3F_V3F"
        # T2F, C3F, N3F and V3F may appear in this string
        material.vertex_format
        #number of bytes per vertex
        vert_size = elems_per_vertex[material.vertex_format]

        max_vertices = len(material.vertices)//vert_size
        vert = list()
        norm = list()
        for n in range(max_vertices):
            v = material.vertices[n*vert_size:(n*vert_size+vert_size)] 
            vert.append(np.array([v[pos+0], v[pos+1], v[pos+2]]))
            norm.append(np.array([v[nor+0], v[nor+1], v[nor+2]]))

        verts.append(np.array(vert).reshape(-1,3))
        norms.append(np.array(norm).reshape(-1,3))

        # Contains the vertex list of floats in the format described above
        material.vertices
        """
        # Material properties
        material.diffuse
        material.ambient
        material.texture
        """
        print("completed. ", name)
    return scene, verts[0], norms[0], faces[0]

class Mesh:
    def __init__(self):
        self.name = "mesh"
        self.path = ""
        self.scene = None
        self.verts = [] 
        self.faces = []
        self.normals = [] 
        self.vertex_format = '' 

    def __str__(self):
        v = [str(v) for v in self.verts]
        f = [str(f) for f in self.faces]
        n = [str(n) for n in self.normals]
        
        count = "{}:\nv f n : {} {} {}".format(self.path, len(v), len(f), len(n)) 
        return "# " + count + "\nvert:" + str(v) + "\nfaces:" + str(f) + "\nnormals:" + str(n)

    def make_normals(self):
        self.normals = []
        for face in self.faces:
            p0 = self.verts[face[0]]
            p1 = self.verts[face[1]]
            p2 = self.verts[face[2]]
            
            v0 = (p1 - p0)[0:3]
            v1 = (p2 - p0)[0:3]
            n = np.cross(v0, v1)
            self.normals.append(n)

class MeshLoader:
    def __init__(self):
        self.history = [] 

    def load(self, filepaths):
        if isinstance(filepaths, str):
            filepaths = glob.glob(filepaths)
        meshes = []
        for filepath in filepaths:
            print("loading {}".format(filepath))
            meshes.append(self.read_wavefront(filepath))
            self.history.append(filepath)
        return meshes

    def read_wavefront(self, filepath):
        """
        print("Faces:", scene.mesh_list[0].faces)
        print("Vertices:", scene.vertices)
        print("Format:", scene.mesh_list[0].materials[0].vertex_format)
        print("Vertices:", scene.mesh_list[0].materials[0].vertices)
        """
        scene, verts, norms, faces = load_wavefront_scene(filepath)
        mesh = Mesh()
        mesh.scene = scene
        mesh.verts = verts 
        mesh.faces = faces
        mesh.vertex_format = scene.mesh_list[0].materials[0].vertex_format
        mesh.make_normals()
        mesh.normals = norms
        mesh.path = filepath
        print(mesh)
        return mesh


class MeshCollider:
    def __init__(self, mesh):
        self.mesh = mesh
        self.create_bounding_sphere()

    def create_bounding_sphere(self):
        self.sphere = {
            'inside' : [0, 0],
            'away'   : [0, 0],
            'outside': []
        }  

    def check_point(self, p, max_faces=12):
        """check cpu collision between point and mesh in host memory
        input:
            p : a point as (1,3) numpy array of float 64
        output:
            boolean True if point inside mesh, False otherwise
        """

        """ assume mesh has faces, normals, and not a facesless triangle strip. """
        m = self.mesh

        def clip(v, a, b):
            if v < a: v = a
            if v > b: v = b
            return v

        inside = 1
        """TODO : plane / point distance: outside -, inside +
           ax + bx + cz + d = 0
           N dot P + d = 0
           N = (a,b,c)
           P = (x,y,z)
            
           1) check that mesh verts and points in same coordinate system
        """

        #disabled
        if inside:
            return

        for i, f in enumerate(self.mesh.faces[max_faces-1]):
            n = self.mesh.normals[i, :]
            faces = self.mesh.faces[i]
            v0, v1, v2 = self.mesh.verts[faces]
            #p_in = (v0+v1+v2)*0.3333
            #p_out = v0 * 100 - 100
            u0 = v1 - v0
            u1 = v2 - v0
            #n = np.cross(u0, u1)
            #n = n / np.norm(n)
            d = -np.dot(n, v0)
            #side0 = np.dot(n, p_in) + d
            #side1 = np.dot(n, p_out) + d
            side = np.dot(n, p) + d
            #print(side)
            if side < 0:
                inside = 0
                break

        return inside==1 
            
    def check(self, points):
        """check cpu collision
           input:
               points : np array is float64 dim [1, N, 3]
           output:
               a point np array np.int32 and size [N, 3]

               hack for now size to [1, 3]
        """
        """
        TODO
        ======
        . only 1 point works with vbo write
        . shape and type that works with raw points is (1,N,3) float64
        . check when points are None is main render loop (does not draw zones)
        1) implement CPU collision check and return collision points
        2) either mark & color collision points for existing pointcloud in frag shader
        3) or write points in zone render vbo
        4) or explore particle system

        """

        """
        points =  np.random.randint(0, 25, (1, 2*256, 3)).astype(np.float64)*10
        points[:,:,2] = -points[:,:,2]
        points[:,:,1] = points[:,:,1]*0.07 + 128 
        """

        collisions = list() 

        for p in points:
            if self.check_point(p):
                collisions.append(p)
        if len(collisions):
            co = np.array(collisions)
        else:
            co = None
        return co 
