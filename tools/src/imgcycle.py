import shutil
import glob
import sys
import time
import os
try:
    import cv2
except:
    cv2 = False

def cycle(files, dest):
    while True:
        for n, filepath in enumerate(files):
            print("push: " + str(n) + " " + filepath, end="\r")
            shutil.copyfile(filepath, dest)
            if cv2:
                cv2.imshow('depth_null.png', cv2.imread(dest))
                cv2.waitKey(0)
            else:
                input("[next]")
    
if len(sys.argv) < 3:
    print("imgcycle imagefile_pattern dest_filepath")
    print("  example$> imgcycl2 /tmp/data/*.png /dest/pathfile.png")
    exit(0)

files = glob.glob(sys.argv[1], recursive=True)
[print(f) for f in files]
print("---------------------------------")
print("source " + sys.argv[1])
dest = sys.argv[2]
print("dest path: ", dest)

print("cycle to " + dest)
print("---------------------------------")
cycle(files, dest)