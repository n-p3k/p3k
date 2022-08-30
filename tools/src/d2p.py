#!/usr/bin/env

import os
import sys
import time

import numpy as np
import cv2
import glob
from src.d2p_mesh import Mesh as Mesh

#sys.path.append("installation")
#from safety.io_utils import ObjFileIo as Mesh

def convert_to_pointcloud_array(depth):

    verts = []

    #cv2.imshow("depth", depth)
    #cv2.waitKey(1)

    for y in range(depth.shape[0]):
        for x in range(depth.shape[1]):
            d = depth[y, x, 0]
            if d > 0:
                p = np.array([x, y, d]).astype(np.int)
                verts.append(p)

    print(len(verts))
    verts = np.array(verts)
    return verts


def convert_to_pointcloud(depth, outputfile):

    mesh = Mesh()
 
    #cv2.imshow("depth", depth)
    #cv2.waitKey(1)

    verts = convert_to_pointcloud_array(depth)

#    verts = []
#     for y in range(depth.shape[0]):
#         for x in range(depth.shape[1]):
#             d = depth[y, x, 0]
#             if d > 0:
#                 p = np.array([x, y, d]).astype(np.int)
#                 verts.append(p)

#     print(len(verts))
#     verts = np.array(verts)


    mesh.export_to(outputfile, verts, [], [])

def main():
    if len(sys.argv) <= 1:
        print("usage: create_occlusion_mask [mesh filepath]")
        exit(0)


    pattern = sys.argv[1] #"installation/capture00.png"
    files = glob.glob(pattern)
    
    for filename in files:
        print("build mesh from depth image ", filename)
        depth = cv2.imread(filename)

        mesh_filepath = os.path.splitext(filename)[0] + '.obj'
        print('export point cloud to :', mesh_filepath)
        convert_to_pointcloud(depth, mesh_filepath)



if __name__ == "__main__":
    main()
