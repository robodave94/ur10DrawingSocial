import cv2



def TestImageContours(img):
    try:
        cimg2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        gray = cv2.cvtColor(cimg2, cv2.COLOR_BGR2GRAY)
    except:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if md[0] > 1:
        if md[1] < 1:
            np.rot90(gray, 1)
    else:
        if md[1] < 1:
            #180
            np.rot90(gray, 3)
        else:
            #270
            np.rot90(gray,2)

    contours, _ = cv2.findContours(255 - gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    lstcont = []
    for i in contours:
        cont = []
        for y in i:
            cont.append(y[0])
        lstcont.append(cont)
    return lstcont


def ImageContoursCustomSet1(img,isTesting=False):
    from skimage import measure
    try:
        cimg2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        gray = cv2.cvtColor(cimg2, cv2.COLOR_BGR2GRAY)
    except:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if abs(md[0])>abs(md[1]):
        if md[0] > 0:
            #90
            print 'Recognized Region 1'
            np.rot90(gray, 3)
        else:
            #270
            print 'Recognized Region 3'
            gray = np.rot90(gray, 1)
    #Rotated to 0 or 180
    else:
        if md[1] > 0:
            #0
            print 'Recognized Region 0'
            gray = np.rot90(gray, 2)
        else:
            #180
            print 'Recognized Region 2'
            gray = np.rot90(gray,2)

    gray = 255-gray
    if isTesting:
        cv2.imshow('', gray)
        cv2.waitKey(10101010)


    cnts,hierachy=cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE);
    lstcont = []

    for i in cnts:
        print i
        cont = []
        for y in i:
            cont.append(y[0])
        lstcont.append(cont)
    if isTesting:
        print len(lstcont)
        disp = np.zeros(gray.shape)
        cv2.drawContours(disp,cnts,-1,255,1)
        cv2.imshow('', disp)
        cv2.waitKey(20202020)
        print lstcont
    return lstcont

def ImageContoursStatic(img,isTesting=False):
    try:
        cimg2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        gray = cv2.cvtColor(cimg2, cv2.COLOR_BGR2GRAY)
    except:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Rotated to 270 or 90
    #if abs(md[0])>abs(md[1]):
        '''if md[0] > 0:
            #90
            print 'Recognized Region 1'
            np.rot90(gray, 3)
        else:
            #270
            print 'Recognized Region 3'
            gray = np.rot90(gray, 1)
    #Rotated to 0 or 180
    else:
        if md[1] > 0:
            #0
            print 'Recognized Region 0'
            gray = np.rot90(gray, 2)
        else:
            #180
            print 'Recognized Region 2'
            #gray = np.rot90(gray,2)'''
    _, gray = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
    if isTesting:
        cv2.imshow('',gray)
        cv2.waitKey(10101010)
    contours, out = cv2.findContours(gray, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    lstcont = []
    for i in contours:
        cont = []
        for y in i:
            cont.append(y[0])
        lstcont.append(cont)
    if isTesting:
        print len(contours)
        disp = np.zeros(gray.shape)
        cv2.drawContours(disp, contours, -1, 255, 1)
        cv2.imshow('', disp)
        cv2.waitKey(20202020)
        print lstcont
    return lstcont

def ImageContoursSubjective(img,isTesting=False):
    def dodgeV2(image, mask):
        return cv2.divide(image, 255 - mask, scale=256)

    def burnV2(image, mask):
        return 255 - cv2.divide(255 - image, 255 - mask, scale=256)

    img_rgb = cv2.imread(img)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    img_gray_inv = 255 - img_gray
    img_blur = cv2.GaussianBlur(img_gray_inv, ksize=(51,51),sigmaX=0, sigmaY=0)

    img_blend = 255-dodgeV2(img_gray, img_blur)
    #_,img_blend = cv2.threshold(img_blend,30,255,cv2.THRESH_BINARY)
    res = ExtrapolateDrawing(img_blend)
    #ImageContoursStatic(res,isTesting=True)
    cv2.imshow('',res)
    cv2.waitKey(20202020)
    #ImageContoursStatic(res,isTesting=True)
    #return lstcont
    return

def ExtrapolateDrawing(image):
    (h, w) = image.shape[:2]

    # convert the image from the RGB color space to the L*a*b*
    # color space -- since we will be clustering using k-means
    # which is based on the euclidean distance, we'll use the
    # L*a*b* color space where the euclidean distance implies
    # perceptual meaning
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # reshape the image into a feature vector so that k-means
    # can be applied
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # apply k-means using the specified number of clusters and
    # then create the quantized image based on the predictions
    clt = cluster.MiniBatchKMeans(n_clusters=3)
    labels = clt.fit_predict(image)
    quant = clt.cluster_centers_.astype("uint8")[labels]

    # reshape the feature vectors to images
    quant = quant.reshape((h, w, 3))
    image = image.reshape((h, w, 3))

    # convert from L*a*b* to RGB
    quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)

    # display the images and wait for a keypress
    #cv2.imshow("image", np.hstack([image, quant]))
    #cv2.waitKey(0)
    im = cv2.cvtColor(quant, cv2.COLOR_BGR2GRAY)
    return im

def TestSystem():
    return
