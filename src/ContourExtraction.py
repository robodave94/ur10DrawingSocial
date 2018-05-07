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