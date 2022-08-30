import numpy as np


def depth_to_xyz_device(depth8):
    """Convert depth image coordinate system to opengl cs."""
    h, w = depth8.shape[0:2]
    x = np.tile(np.arange(w), w)
    y = np.repeat(np.arange(h), h)
    z = depth8.flatten()
    return x, y, z

def xyz_device_to_eye_gl(x,y,z, dim):
    """Convert point cloud in top-left z-pos-away to gl:
        gl: x positive-to-right, y bottom-up, z-positive-towards cam.
    """
    w, h, z_max = dim 
    y = h - y
    z = -z
    return x, y, z

def domain_range_swap_yz(i, max_range=255):
    """Given an frame swap one domain dimension with range."""
    if i is None:
        return None

    h, w = i.shape[0:2]
    x = np.tile(i[0,:], h).flatten()
    y = np.repeat(i[0,:], w).flatten()
    z = i[:,:,0]

    j = np.zeros((max_range+1, w, 3), np.uint8)
    
    for n in range(w*h):
        xx = n % w
        yy = n // w
         
        zz = max_range-z[yy,xx]

        if j[zz,xx][0] < yy:
            j[zz,xx]=(yy,yy,yy)
    return j