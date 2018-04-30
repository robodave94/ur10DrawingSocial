def ImageContoursCustomSet1(img,isTesting=False):
    import cv2
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
