import cv2
import os
import glob
import numpy as np


class File:

    def __init__(self):
        self.folder = 'static'
        self.image_name = self.findFile()

    
    def findFile(self):
        search = os.path.join(self.folder,'upload.*')
        files = glob.glob(search)

        if files:
            return os.path.basename(files[0])
        return "No file found"
    
    def getPath(self):
        if self.image_name:
            return os.path.join(self.folder, self.image_name)
        return None

class Process:

    def __init__(self):
        self.image = None;
        
    def read(self):
        file_obj = File()
        path = file_obj.getPath()
        if path and os.path.exists(path):
            return cv2.imread(path)
        return None

    def display(self,label,image,resize=False):

        if resize == True:
            image = cv2.resize(image,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA);

        cv2.imshow(label,image);
        cv2.waitKey(0);
        cv2.destroyAllWindows();

    def invert(self,image):
        invert = cv2.bitwise_not(image);
        return invert;

    def grayScale(self,image):
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY);
        return gray;

    def thresholdBinary(self,image,maxt=255,block=11,C=2):
        bw = cv2.adaptiveThreshold(image,maxt,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,block,C);
        return bw;

    def thicker(self,image,iteration=1,kx=1,ky=1):
        kernel = np.ones((kx,ky),np.uint8);
        dilate=  cv2.dilate(image,kernel,iteration);
        return dilate;

    def thinner(self,image,iteration=1,kx=1,ky=1):
        kernel = np.ones((kx,ky),np.uint8);
        erode =  cv2.erode(image,kernel,iteration);
        return erode;

    def medianBlur(self,image,strength):
        image = cv2.medianBlur(image,strength);
        return image;

    def gaussianBlur(self,image,k=1,strength=0):
        image = cv2.GaussianBlur(image,(k,k),strength);
        return image;


    def removeNoise(self,image,dilate=False,dIteration=0,erode=False,eIteration=0,k=1):
        kernel = np.ones((k,k),np.uint8)

        if dilate == True:
            image = self.thicker(image,dIteration,k,k);
        if erode == True:
            image = self.thinner(image,eIteration,k,k);

        image = cv2.morphologyEx(image,cv2.MORPH_CLOSE,kernel);
        image = self.medianBlur(image,3);
        return image;

    def getSkewAngle(self,image):
        copy = image.copy();

        gray = self.grayScale(copy);
        gaussian = self.gaussianBlur(gray,7,0);
        x,threshold = cv2.threshold(gaussian,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernal = cv2.getStructuringElement(cv2.MORPH_RECT,(30,5));
        dilate = cv2.dilate(threshold,kernal,iterations=2);

        contours, hierarchy = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours,key = cv2.contourArea, reverse=True)
        for c in contours:
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            cv2.rectangle(copy,(x,y),(x+w,y+h),(0,255,0),2)

        large_contour = contours[0]
        minAreaRect = cv2.minAreaRect(large_contour)

        cv2.imwrite("temp/c.jpg",copy);
        angle =  minAreaRect[-1]

        if angle < -45:
            angle = 90 + angle
        
        return -1.0*angle


    def rotate(self,image,angle):
        copy = image.copy()
        (h,w) = copy.shape[:2]
        center = (w//2,h//2)

        M = cv2.getRotationMatrix2D(center,angle,1.0)

        copy = cv2.warpAffine(copy,M,(w,h),flags=cv2.INTER_CUBIC,borderMode = cv2.BORDER_REPLICATE)

        return copy

    def deskew(self,image):
        angle = self.getSkewAngle(image);
        return self.rotate(image, -1.0*angle)
    
    def remove_borders(self,image):
        contours,heirarchy = cv2.findContours(image,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
        cntsSorted = sorted(contours, key=lambda x:cv2.contourArea(x))
        cnt = cntsSorted[-1]
        x, y, w, h = cv2.boundingRect(cnt)
        crop = image[y:y+h, x:x+w]
        return (crop)
    

