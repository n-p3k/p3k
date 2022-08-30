import numpy as np 

 
def make_rot_matrix_from_rvector(deg):
    rx, ry, _ = np.deg2rad(deg)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx),  np.cos(rx)]])
    Ry = np.array([
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry),  0, np.cos(ry)]])
    """ TODO Rz """
    Rz = None
    return np.matmul(Rx, Ry)

def apply_pose_vecs(pts, rvec, tvec):
    """Transform coordinates to intented rigid pose."""
    R = make_rot_matrix_from_rvector(rvec)
    pts = np.array([R.dot(p-tvec) for p in pts]) 
    return pts
