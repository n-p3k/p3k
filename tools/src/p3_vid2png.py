import cv2
import sys

# Opens the Video file
vidfile = sys.argv[1]
print("convert " + vidfile + " to png files ...")

cap= cv2.VideoCapture(vidfile)
i=0
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == False:
        break
    framepath = "frame{0:05d}.png".format(i)
    print(framepath)
    cv2.imwrite(framepath,frame)
    i+=1
 
cap.release()
cv2.destroyAllWindows()
