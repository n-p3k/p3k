import numpy as np


"""class Frustum
    symmetric frustum object

input:
    n : near plane
    f : far plane
    t : top
    r : right
ouput:
    frustum data structure

"""
class Frustum:
    def __init__(self):
        self.name = "symmetric frustum"
        self.unit = "meter"

    def from_intrinsics(self, focal_length, fov_h, fov_v, max_distance=100):
        """Make symmetric frustum from camera intrinsics"""
        n = focal_length
        f = max_distance
        r = n * (fov_h * np.pi / 360.0) 
        t = n * (fov_v * np.pi / 360.0) 
        self.from_volume(n, f, -r, r, -t, t)

    def from_volume(self, n, f, l, r, b, t):
        self.n = n
        self.f = f
        self.t = t
        self.b = b
        self.r = r
        self.l = l

    def view_to_clip_matrix(self):
        n, f, t, b, r, l = self.n, self.f, self.t, self.b, self.r, self.l

        EyeToClip = np.array(
            [[n/r,  0,    0,   0], 
            [ 0,   n/t,  0,    0],
            [ 0,   0,   f+n/(f-n), 2*f*n/(f-n)],
            [ 0,   0,    -1,   0]])
        return EyeToClip

    def perspective_matrix(self):
        return self.view_to_clip_matrix()

    