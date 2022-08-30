import numpy as np
import cv2
import time


class Mesh:
    def __init__(self, verts=None, faces=None):
        self.cfg = {'mode' : 'ldn'}
        self.verts = verts 
        self.faces = faces 
        self.name = 'unit n/a' 
        if verts is None or faces is None:
            self.normals = []
        else:
            self.normals = self.compute_normals(faces, verts)

    def box_from_verts(self, verts, t=0.3):
        """Create face triangle for a 3d box.
           Last faces are (dynamic) compressed mesh for LDN, MNT, LMT  mounts
        """
        # faces (16x)
        self.faces = np.array([[4, 0, 1], [4, 1, 5], # left
                         [5, 1, 2], [5, 2, 6],
                         [6, 2, 3], [6, 3, 7],
                         [7, 3, 0], [7, 0, 4],
                         [3, 2, 1], [3, 1, 0],  # bottom, and top
                         [7, 4, 5], [7, 5, 6], 
                         [8, 9, 10], [8, 10, 11], # comporessed top-to-bottom
                         [12, 13, 14],[12, 14, 15]]).astype(np.int) # compressed front-to-back
        # vertices (12x)
        self.verts = verts 
        # add compressed meshes (top-to-bottom and front-to-back)
        print('add compressed tops (wnt,ldn): ', self.verts.shape)
        self.verts = add_compressed(self.verts, t, axis=1)

        # duplicate the base, will be needed as future copy (original bottom)
        print('add copy of the bottom')
        bottom = self.verts[0:4]
        tmp = np.vstack((self.verts[0:12], bottom))
        self.verts = tmp 

        # normals (16x)
        self.recompute_normals()

    def import_from(self, filename, ignore_compressed=False):
        verts = []
        normals = []
        faces = []
        with  open(filename, 'r') as infile:
            infile.readline() # skip the first line
            for line in infile:
                #print(line)
                words = line.split()
                if len(words) == 0:
                    continue
                if words[0] == 'v':
                    v = []
                    for i in range(3):
                        v.append(float(words[i + 1]))
                    verts.append(v)
                elif words[0] == 'vn':
                    n = []
                    for i in range(3):
                        n.append(float(words[i + 1]))
                    normals.append(n)
                elif words[0] == 'f':
                    f = []
                    for i in range(3):
                        word = words[i + 1]
                        f.append(int(word.split("/")[0]))
                    faces.append(f)


        verts = np.array(verts)
        if ignore_compressed:
            verts = verts[0:8, :]

        #print('imported verts ', verts.shape)
        self.verts = verts

        self.normals = np.array(normals)
        # make vertex indices start at 0 instead of 1 (as in wavefront obj)
        self.faces = np.array(faces).astype(np.int) - 1

    def export_to(self, filename, verts=None, tris=None, normals=[], scale=1.0):
        #assert len(verts) == 8
        #assert len(tris) >= 8
        if filename is None or filename == '':
            return
        if verts is not None:
            assert type(verts) == np.ndarray
            self.verts = verts
        if tris is not None:
            self.faces = tris

        self.normals = normals

        # at least 1 vertex to export (for pointcloud tests)
        assert len(self.verts) >= 1
        
        with open(filename, "w") as f:

            print("export Mesh file ", filename)
            f.write("# filename {0}\n".format(self.name))
            f.write('# metric coordinate system\n')
            f.write('# LV pattern: p0 is left-most lower corner, f0 is low left face\n')
            f.write('g volume\n\n')

            # vertices
            for p in self.verts:
                p[0] = p[0] / scale
                p[1] = p[1] / scale

            header = {0 : "# bottom\n", 4 : "# top\n", 8 : "# compressed top-to-bottom\n", 12 : "# original bottom\n"}
            # vertices
            for n, p in enumerate(self.verts):

                if header.get(n, False):
                    f.write(header[n])
                col = "1 1 1"
                if n < 4:
                    col = "1 0 0"
                elif n < 8:
                    col = "0.5 0 1"
                elif n < 12:
                    col = "1 1 0"
                elif n < 16:
                    col = "0 1 0"
                d_val = np.round(p[2]/255, 2)
                y_val = np.round((p[1]%30)/30, 2)
                y_val = y_val*y_val*y_val
                x_val = 1.0 - np.round(p[0]/224, 2)
                mod_val = min(x_val + 1.0-d_val, 1.0)

                # overwrite colospectrum mode
                #mod_val *= mod_val
                #y_val, d_val = mod_val, mod_val
                
                col = "{} {} {}".format(d_val, d_val, d_val)
                line = "v {} {} {}   {}\n".format(
                    p[0],
                    p[1],
                    p[2],
                    col)  # do not scale depth range
                 
                #print(line)
                f.write(line)

            # normal
            if len(self.faces) > 0 and len(self.normals) <= 1:
                self.normals = self.compute_normals(self.faces, self.verts)

            f.write('\n')
            for n in self.normals:

                line = "vn {} {} {}\n".format(n[0], n[1], n[2])
                f.write(line)

            # faces
            header = {12 : "# compressed top-to-bottom\n", 14 : "# original base\n"}
            f.write('\n')
            for n, raw_t in enumerate(self.faces):
                if header.get(n, False):
                    f.write(header[n])
                # map from ojb face index (starts at 1) to vertex index (s=0)
                t = np.array(raw_t) + 1
                # obj format required vertex index in face to start at 1
                n0 = t[0]
                n1 = t[1]
                n2 = t[2]

                line = "f {}//{} {}//{} {}//{}\n".format(
                    t[0], n0, t[1], n1, t[2], n2)
                f.write(line)

    def compute_normals(self, tris, iverts):
        """Compute normals from vertcies.
        
            Args
                tris : np-array of (integer) face index triplet
                iverts : np-arary of (range-integer) 3d-points

        """
        normals = []
        verts = iverts.astype(np.float)

        for face_index in tris:
            # obj faces start from 1 but in python from 0
            vi_1st = face_index[0]
            vi_2nd = face_index[1]
            vi_3rd = face_index[2]
            
            # identify th 2nd vertex as the pitvot (local frame origin)
            v_1st = verts[vi_1st]
            v_2nd = verts[vi_2nd]
            v_3rd = verts[vi_3rd]

            # make two vectors that point outward the face
            v0 = v_1st - v_2nd
            v1 = v_3rd - v_2nd
            
            # cross product:
            #             
            # rule is: a x b is up and b x a is down
            #        : a x b = - b x a
            nx = v0[1] * v1[2] - v0[2] * v1[1]
            ny = v0[2] * v1[0] - v0[0] * v1[2]
            nz = v0[0] * v1[1] - v0[1] * v1[0]

            # in this code, 
            #        : a = v1, and 
            #          b = v0
            # and our LV face pattern is like UP
            #
            # therefore, we want a x b = -b x a
            n = -np.array([nx, ny, nz]).astype(np.float)
            
            # normalize vectors
            n = n / np.sum(np.abs(n) + 1e-9)
            normals.append(n)

        # quick check: first normal should point left, towards camera
        n = normals[0]
        if (n[0] <= 0 and n[2] < 0) is False:
            raise RuntimeError("the first normal is invalid")

        return np.array(normals).astype(np.float)

    def recompute_normals(self):
        """Recompute the mesh normals when verts change."""
        self.normals = self.compute_normals(self.faces, self.verts)
