import cv2 as cv
import os
import numpy as np



#variables
#################################################################################
#this program either takes from a camera or an image from your computer.
getFromCamera = False
"""if getFromCamera = False we choose an image
note that the image has to be at the same path (same folder) as the pathon code. also do not forget to add the extention of the mage after its name"""
imageName = "1.jpg" 

cameraNumber = 1
#if autoDetectCamera = True then, the above cameraNumber value will note be used
autoDetectCamera = False

#width/height=4/3 (for my camera)
useDefaultResolution = False
resolutionWidth = 10
resolutionHeight = 10

useDefaultSize = False
sizeWidth = 500
sizeHeight = 500

#frames per seconds
fps = 20

#exit ASCII Key Number for cv.waitKey() function (27 = Esc on keyBoard). 
key = 27

#more specific parameters
############
"""HSV => H=Hue, S=saturation, and V=Value.
H range 0-180 and S and V ranges are 0-255.
Also, l for lower range and u for upper range"""
(lowerH, upperH) = (70, 131)
(lowerS, upperS) = (19, 100)
(lowerV, upperV) = (26, 80)

#filters
blur = 2
erosion = 0
dilation = 0

#for largest area
contourAreaRatio = 0.005 #number of pixels of the largest area contour over all of the pixels of the frame/image (or contour area over area of the image)
############
#################################################################################











#create TrackBar Window
windowWidth,windowHight = (500,300)
cv.namedWindow("TrackBar",cv.WINDOW_NORMAL)
cv.resizeWindow("TrackBar",windowWidth,windowHight)

def track(x):
    pass
cv.createTrackbar("Filter","TrackBar",blur,30,track)

cv.createTrackbar("Lower H","TrackBar",lowerH,180,track)
cv.createTrackbar("Upper H","TrackBar",upperH,180,track)
cv.createTrackbar("Lower S","TrackBar",lowerS,255,track)
cv.createTrackbar("Upper S","TrackBar",upperS,255,track)
cv.createTrackbar("Lower V","TrackBar",lowerV,255,track)
cv.createTrackbar("Upper V","TrackBar",upperV,255,track)

cv.createTrackbar("Erosion","TrackBar",erosion,20,track)
cv.createTrackbar("Dilation","TrackBar",dilation,20,track)






#if we want to take an image (getFromCamera = False)
#############################################################
if getFromCamera == True:

    #this code will catch the camera even if the camera number is wrong
    ###########################
    if autoDetectCamera ==True:
        cameraNumber =0
        cap=cv.VideoCapture(cameraNumber)
        while True:
            if (cap.isOpened()==True):
                break
            else:
                cameraNumber += 1
    else:
        cap = cv.VideoCapture(cameraNumber)
    ##########################
    if useDefaultResolution ==False:
        cap.set(3,resolutionWidth)
        cap.set(3,resolutionWidth)
    



    while cap.isOpened()==True:
        blur = cv.getTrackbarPos("Filter","TrackBar")

        lowerH = cv.getTrackbarPos("Lower H","TrackBar")
        upperH = cv.getTrackbarPos("Upper H","TrackBar")
        lowerS = cv.getTrackbarPos("Lower S","TrackBar")
        upperS = cv.getTrackbarPos("Upper S","TrackBar")
        lowerV = cv.getTrackbarPos("Lower V","TrackBar")
        upperV = cv.getTrackbarPos("Upper V","TrackBar")

        erosion = cv.getTrackbarPos("Erosion","TrackBar")
        dilation = cv.getTrackbarPos("Dilation","TrackBar")


        ret, frameOriginal = cap.read()

        if useDefaultSize == False:
            frameOriginal = cv.resize(src=frameOriginal,dsize=(sizeWidth,sizeHeight))

        #blur (use cv.medianBlur() or cv.GaussianBlur() the rest is the same )
        ksize = blur*2+1
        frameBlur = cv.medianBlur(src=frameOriginal, ksize=ksize)

        frameHSV = cv.cvtColor(src=frameBlur,code=cv.COLOR_BGR2HSV)
        frameHSVInRange = cv.inRange(src=frameHSV,lowerb=(lowerH,lowerS,lowerV),upperb=(upperH,upperS,upperV))

        

        #erosion and dilation
        erodeSize = 2 #seems good
        dilatSize = 2 #seems good

        eKernal = np.ones((erodeSize,erodeSize),np.uint8)
        frameEroded = cv.erode(src=frameHSVInRange,kernel=eKernal,iterations=erosion)

        dKernal = np.ones((dilatSize,dilatSize),np.uint8)
        frameDilated = cv.dilate(src=frameEroded,kernel=dKernal,iterations=dilation)


        #contour
        frameDrawContours=frameDilated.copy()

        contours, hierarchy  = cv.findContours(image=frameDilated,mode=cv.RETR_TREE,method=cv.CHAIN_APPROX_NONE)
        frameDrawContours = cv.cvtColor(frameDrawContours,cv.COLOR_GRAY2BGR)

        hight, width, channels = frameDrawContours.shape
        totalArea = hight*width
        
        sortedContoursByArea = sorted(contours,key=cv.contourArea, reverse=True)

        try:          
            cv.drawContours(frameDrawContours,sortedContoursByArea[0],-1,color=(0,0,255),thickness=2)

            if cv.contourArea(sortedContoursByArea[0])/totalArea > contourAreaRatio:

                M=cv.moments(sortedContoursByArea[0])
                cx = M["m10"]/M["m00"]
                cy = M["m01"]/M["m00"]                      
                cv.circle(img=frameDrawContours,center=(int(cx),int(cy)),radius=4,color=(0,255,0),thickness=-1)
                #origin in the down left. y increase when we go up and x increase when we go right
                x=cx/width
                y=(hight-cy)/hight
                print("\rx = {:.3f}, y = {:.3f}     ".format(x,y),end="")
        except:
            print("\rContour Not found        ",end="")

                


        
        cv.imshow("1-Original Frame(s)", frameOriginal)
        cv.imshow("2-Filter", frameBlur)
        cv.imshow("3-Color in Range (HSV)", frameHSVInRange)
        cv.imshow("4-Erosion", frameEroded)
        cv.imshow("5-Erosion then Dilation", frameDilated)
        cv.imshow("6-Position (Centroid)",frameDrawContours)


        wait = int(1000/fps) #wait in ms

        if cv.waitKey(wait) == key or cv.getWindowProperty("1-Original Frame(s)", cv.WND_PROP_VISIBLE)<0: 
            break

        if cv.getWindowProperty("1-Original Frame(s)", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("2-Filter", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("3-Color in Range (HSV)", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("4-Erosion", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("5-Erosion then Dilation", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("6-Position (Centroid)", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("TrackBar", cv.WND_PROP_VISIBLE) <1 \
           :
            break

        

    cap.release()
    cv.destroyAllWindows()
#############################################################




#if we want to take an image (getFromCamera = False)
#############################################################
if getFromCamera == False:
    #getting the path of this python file
    currentFolderPath=os.path.dirname(os.path.realpath(__file__))
    #changing the path to the path of this python file
    os.chdir(currentFolderPath)

    imgOriginal = os.path.join(currentFolderPath,imageName)
    #print(originalImagePath)

    frameOriginal =cv.imread(imgOriginal)

    if useDefaultSize == False:
        frameOriginal = cv.resize(src=frameOriginal,dsize=(sizeWidth,sizeHeight))

    while True:
        blur = cv.getTrackbarPos("Filter","TrackBar")

        lowerH = cv.getTrackbarPos("Lower H","TrackBar")
        upperH = cv.getTrackbarPos("Upper H","TrackBar")
        lowerS = cv.getTrackbarPos("Lower S","TrackBar")
        upperS = cv.getTrackbarPos("Upper S","TrackBar")
        lowerV = cv.getTrackbarPos("Lower V","TrackBar")
        upperV = cv.getTrackbarPos("Upper V","TrackBar")

        erosion = cv.getTrackbarPos("Erosion","TrackBar")
        dilation = cv.getTrackbarPos("Dilation","TrackBar")


        #blur (use cv.medianBlur() or cv.GaussianBlur() the rest is the same )
        ksize = blur*2+1
        frameBlur = cv.medianBlur(src=frameOriginal, ksize=ksize)

        frameHSV = cv.cvtColor(src=frameBlur,code=cv.COLOR_BGR2HSV)
        frameHSVInRange = cv.inRange(src=frameHSV,lowerb=(lowerH,lowerS,lowerV),upperb=(upperH,upperS,upperV))

        #erosion and dilation
        erodeSize = 2 #seems good
        dilatSize = 2 #seems good

        eKernal = np.ones((erodeSize,erodeSize),np.uint8)
        frameEroded = cv.erode(src=frameHSVInRange,kernel=eKernal,iterations=erosion)

        dKernal = np.ones((dilatSize,dilatSize),np.uint8)
        frameDilated = cv.dilate(src=frameEroded,kernel=dKernal,iterations=dilation)


        #contour
        frameDrawContours=frameDilated.copy()

        contours, hierarchy  = cv.findContours(image=frameDilated,mode=cv.RETR_TREE,method=cv.CHAIN_APPROX_NONE)
        frameDrawContours = cv.cvtColor(frameDrawContours,cv.COLOR_GRAY2BGR)

        hight, width, channels = frameDrawContours.shape
        totalArea = hight*width
        
        sortedContoursByArea = sorted(contours,key=cv.contourArea, reverse=True)


        try:          
            cv.drawContours(frameDrawContours,sortedContoursByArea[0],-1,color=(0,0,255),thickness=2)

            if cv.contourArea(sortedContoursByArea[0])/totalArea > contourAreaRatio:

                M=cv.moments(sortedContoursByArea[0])
                cx = M["m10"]/M["m00"]
                cy = M["m01"]/M["m00"]                      
                cv.circle(img=frameDrawContours,center=(int(cx),int(cy)),radius=4,color=(0,255,0),thickness=-1)
                #origin in the down left. y increase when we go up and x increase when we go right
                x=cx/width
                y=(hight-cy)/hight
                print("\rx = {:.3f}, y = {:.3f}     ".format(x,y),end="")
        except:
            print("\rContour Not found        ",end="")
            


        cv.imshow("1-Original Frame(s)", frameOriginal)
        cv.imshow("2-Filter", frameBlur)
        cv.imshow("3-Color in Range (HSV)", frameHSVInRange)
        cv.imshow("4-Erosion", frameEroded)
        cv.imshow("5-Erosion then Dilation", frameDilated)
        cv.imshow("6-Position (Centroid)",frameDrawContours)

        wait = int(1000/fps) #wait in ms


        if cv.waitKey(wait) == key or cv.getWindowProperty("1-Original Frame(s)", cv.WND_PROP_VISIBLE)<0: 
            break

        if cv.getWindowProperty("1-Original Frame(s)", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("2-Filter", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("3-Color in Range (HSV)", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("4-Erosion", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("5-Erosion then Dilation", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("6-Position (Centroid)", cv.WND_PROP_VISIBLE) <1 or\
           cv.getWindowProperty("TrackBar", cv.WND_PROP_VISIBLE) <1 \
           :
            break

        
    cv.destroyAllWindows()       
#############################################################







