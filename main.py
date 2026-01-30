import cv2
import pytesseract
from PIL import Image
import numpy as np

def noise_removal(image):
    kernel = np.ones((2,2),np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)

    kernele = np.ones((2,2), np.uint8)
    image = cv2.erode(image, kernele,iterations=1)

    #image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernele)
    image = cv2.medianBlur(image,1)
    return image

def thinner(image): 
    kernel = np.ones((1,1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    return image

def thicker(image):
    kernel = np.ones((2,2),np.uint8)
    image = cv2.dilate(image, kernel,iterations=1)
    return image

# Calculate skew angle of an image
def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)

    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

im_file = "Images/doc.png"

image = cv2.imread(im_file)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
invert = cv2.bitwise_not(gray)
threshold, bw_image = cv2.threshold(invert, 100,255,cv2.THRESH_BINARY)

bw_image = thinner(bw_image)

cv2.imshow("Image",bw_image)

cv2.waitKey()
cv2.destroyAllWindows()


