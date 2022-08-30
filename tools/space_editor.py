import numpy as np
import cv2 
import sys
import transform.projection
import pix.render
import geometry.mesh
import transform.affine 

"""
world space     :  global coord system independent of observer
eye (cam) space :  viewer / camera coordinate system in 3d space
clip space      :  coordinates projected on to 2d image plane embedded in 3d space
NDC             :  coordinates normalized to unit cube     
screen space    : 2d coordinates in physical pixel space
"""

def make_grid(n, z_in_front_negative=True): 
    """Grid of n x n blocks (1/2x1/2 unit each)"""

    dim_count = n + 1
    x_val = np.linspace(-n/4, n/4, dim_count)
    z_val = np.linspace(1, 1 + n/2, dim_count)

    """camera view (eye) space requirs negative z in front.
       sometimes W=V, sometimes W[z] = -V[z]
    """
    if z_in_front_negative:
        z_val = -z_val

    x_coord = np.meshgrid(x_val, z_val)[0].flatten()
    z_coord = np.meshgrid(x_val, z_val)[1].flatten()
    
    y0 = np.ones(dim_count*dim_count)*-0.25
    y1 = np.ones(dim_count*dim_count)*0.25

    base = np.array(list(zip(x_coord, y0, z_coord)))
    top = np.array(list(zip(x_coord, y1, z_coord)))
    grid = np.concatenate((base, top), axis=0)

    return grid

def transform_space(n, outpath, tvector, rvector):
    grid =  make_grid(n, z_in_front_negative=True)
    screen_size = [640, 480]
    W, H = screen_size
    
    """ assume max distance 10m, and focal length 0.01m """
    max_dist = 10  

    """ World to camera - rotate & translate camera in the world """
    grid = transform.affine.apply_pose_vecs(grid, rvector, tvector)

    [print(p) for p in grid]
    min_x, max_x = np.min(grid[:,0]), np.max(grid[:,0])
    min_y, max_y = np.min(grid[:,1]), np.max(grid[:,1])
    min_z, max_z = np.min(grid[:,2]), np.max(grid[:,2])

    """ convert axis-aligned corner distances (corners z) to depth in, 255 = max dist"""
    depth_from_z = (255 * -grid[:,2] / max_dist).astype(np.int)

    frame_buffer = np.zeros((H, W, 3), dtype=np.uint8)
    frustum = transform.projection.Frustum()
    frustum.from_intrinsics(focal_length=0.01, fov_h=90, fov_v=60, max_distance=10)
    P = frustum.perspective_matrix()

    """world and eye space are same, make grid points homogeneous"""
    vertex_position_eye = np.insert(grid, 3, values=1, axis=1)
    vertex_position_clip = vertex_position_eye @ P
    ndc_x = vertex_position_clip[:,0] / -vertex_position_eye[:, 2]
    ndc_y = vertex_position_clip[:,1] / -vertex_position_eye[:, 2]
    ndc_z = vertex_position_clip[:,2] / -vertex_position_eye[:, 2]

    """ NDC to screen coordinates """
    screen_x = (ndc_x + 1)/2 * W
    screen_y = H * (1 - (ndc_y + 1)/2)
    screen_z = 255 * (ndc_z + 1)/2

    pixel_points = np.vstack([screen_x, screen_y, screen_z]).T

    """ insert depth values before clipping for later visualization """    
    """ p = [screen_x, screen_y, depth] """
    pixel_points[:,2] = depth_from_z

    pixel_points = pixel_points[pixel_points[:,0]<W] 
    pixel_points= pixel_points[pixel_points[:,0]>=0] 
    pixel_points = pixel_points[pixel_points[:,1]<H] 
    pixel_points= pixel_points[pixel_points[:,1]>=0] 
    
    pixel_points = pixel_points.astype(np.uint)
    pix.render.points(frame_buffer, pixel_points, th=6)   

    """ First and nearest grid corner at 1 unit from origin """
    ix = n//2 -1
    """ Hack ix to N as first central corners ix changed after clipping """
    ix = n 

    """ Render to buffer only if some points survived the screen clipping """
    if len(pixel_points) > 0:
        x0 = int(pixel_points[ix+0, 0] + 1)
        x1 = int(pixel_points[ix+1, 0] - 1)
        xm = int((x0 + x1) / 2)
        y0 = pixel_points[n//2+0, 1]
        """ Three points between central block corners. """
        color = [255, 255, 255]
        l = [x0, xm, x1]
        for x in l:
            pix.render.points(frame_buffer, [np.array([x, y0])], color, th=8)

    params = [cv2.IMWRITE_PNG_COMPRESSION, 0]
    cv2.imwrite(outpath, frame_buffer, params)

    print("------------- {0}x{0} blocks volume ------------".format(n))
    print("grid corners on floor projected to screen space")
    print("grid blocks start at 1m distance from camera")
    print("----------------------------------------------")
    print("")
    print("X...X...X...X...X...X")
    print(".   .   .   .   .   .")
    print("X...X...X...X...X...X")
    print(".   .   .   .   .   .")
    print("X...X...X...X...X...X")
    print(".   .   .   .   .   .")
    print("X...X...X...X...X...X")
    print(".   .   .   .   .   .")
    print("X...X...X...X...X...X")
    print(".   .   .   .   .   .")
    print("X...X...X...X...X...X")
    print("          ^         ")
    print("          |         ")
    print("          | 1m      ")
    print("          |         ")
    print("          O cam     ")
    print("----------------------------------------------")
    print("volume size: {0}m x {1}m x {2}m".format(max_x-min_x, max_z-min_z, max_y-min_y))
    print("grid x     : {0}m to {1}m ".format(min_x, max_x))
    print("grid z     : {0}m to {1}m ".format(min_z, max_z))
    print("grid height: {0}m to {1}m ".format(min_y, max_y))
    print("----------------------------------------------")
    print("rvector: ", rvector)
    print("tvector: ", tvector)
    print('')
    print("output save to {0} ...".format(outpath))
    print("done.")
    return frame_buffer

def edit(n, outpath, tvect, rvect):
    while True: 
        frame_buffer = transform_space(n, outpath, tvect, rvect)

        tx, ty, tz = tvect
        rx, ry, rz = rvect

        cv2.imshow('projection - world-cameara -> clip -> ndc -> screen space', frame_buffer)
        key = cv2.waitKey(0)
        if key == ord('a'):
            tx -= 0.1
        if key == ord('d'):
            tx += 0.1
        if key == ord('w'):
            tz -= 0.1
        if key == ord('s'):
            tz += 0.1
        if key == ord('q'):
            ty -= 0.1
        if key == ord('e'):
            ty += 0.1

        if key == ord('o'):
            ry -= 1.0
        if key == ord('p'):
            ry += 1.0

        if key == ord('1'):
            exit(0)

        tvect = np.array([tx, ty, tz])
        rvect = np.array([rx, ry, rz])

    
if __name__=="__main__":
    try:
        tvector = np.array([0.0, 0.0, 0.0])
        rvector = np.array([0.0, 0.0, 0.0])

        outpath = sys.argv[1]
        try:
            t = [float(v) for v in sys.argv[2:5]]
            r = [float(v) for v in sys.argv[5:8]]
            tvector = np.array(t)
            rvector = np.array(r) 
        except:
            pass 
    except:
        outpath = 'output_space_as_depth_image.png'

    print("tvector: ", tvector)
    print("rvector: ", rvector)
    edit(5, outpath, tvector, rvector)
