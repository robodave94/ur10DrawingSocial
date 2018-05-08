import cv2
def ImageContoursCustomSet1(img,isTesting=False):

    try:
        cimg2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        gray = cv2.cvtColor(cimg2, cv2.COLOR_BGR2GRAY)
    except:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = 255-gray
    _,cnts,_=cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    lstcont = []
    for i in cnts:
        cont = []
        for y in i:
            cont.append([y[0][0],y[0][1]])
        lstcont.append(cont)
    return lstcont


def ImageContoursCustomSet2(img,isTesting=False):
    try:
        cimg2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        gray = cv2.cvtColor(cimg2, cv2.COLOR_BGR2GRAY)
    except:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = 255-gray
    cv2.imshow('',gray)
    cv2.waitKey(2020202)
    #_,cnts,_=cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts=cv2.findNonZero(gray)
    lstcont = []
    for i in cnts:
        lstcont.append([i[0,0],i[0,1]])
    return lstcont

#print ImageContoursCustomSet2(cv2.imread('/home/naodev/Documents/default_ROSws/src/ur10DrawingSocial/robot_img_v2/human_2.png'))


def JamesContourAlg(img):
    import math,numpy as np
    dist_thresh = 6

    retval, gray = cv2.threshold(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY), 200, 255, cv2.THRESH_BINARY_INV)

    #cv2.imshow('',gray)
    #cv2.waitKey(20202002)
    # Code to find contours
    _,cnts, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    lstcont = []
    approx = []

    for c in cnts:
        # Simplify
        epsilon = 0.0002 * cv2.arcLength(c, False)
        approx.append(cv2.approxPolyDP(c, epsilon, False))

    for c in approx:
        cont = []
        pv = c[0][0]
        for p in c:
            point = np.array([p[0,0],p[0,1]])
            print point
            # if euclidean_dist(pv, point) > dist_thresh:
            #print math.sqrt((pv[0] - point[0]) * (pv[0] - point[0]) + (pv[1] - point[1]) * (pv[1] - point[1]))
            if math.sqrt((pv[0] - point[0]) * (pv[0] - point[0]) + (pv[1] - point[1]) * (pv[1] - point[1])) > dist_thresh:
                cont.append(point)
                pv = point
        lstcont.append(cont)
    return lstcont