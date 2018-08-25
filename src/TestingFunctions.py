import math
import DN_LIB,cv2,numpy
'''
calculated endpt=0.04543,-0.921935
xZero,yZero,xMax,yMax
0.354360007582 -0.713510701163 -0.26350156373 -1.13036014377
zDraw = -0.0433069014414
zHover = zDraw + 0.04
init hover
[0.04539028597592009, -0.5050933527023307, 0.35669773528119203, 2.2132137442512105, -2.212639604541358, 0.009988270617139626]
DN_LIB.ImageContoursSubjective('human.jpg',isTesting=True)
DN_LIB.ImageContoursSubjective('testModel.jpg',isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('circle.png',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('Images/coffee-cup.png',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('hellokitty.jpg',cv2.IMREAD_GRAYSCALE),isTesting=True)

DN_LIB.ImageContoursStatic(cv2.imread('Images/Association Rule Learning.png',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('Images/brain.png',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('Images/CC-cube.png',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('starbucks.jpg',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('pickachew.png',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('hellokitty.jpg',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursStatic(cv2.imread('optimus.jpg',cv2.IMREAD_GRAYSCALE),isTesting=True)
DN_LIB.ImageContoursSubjective('optimus.jpg',isTesting=True)
#x = DN_LIB.DrawingRobotInstance()
#x.RunningSocialRoutineV1()
#0.112817,-1.016136,0.059108
#print -0.00839948328889*(0.112817) + 0.0022092124382*(-1.016136) + 0.395982160324*(0.059108) #= -0.0265983096379
#print (-0.0083994832888*0.37274 + 0.0022092124382*-0.96751 +0.0265983096379)/ 0.395982160324
#= -0.0265983096379

def inputeq(x,y,z):
    print (-0.00244709145561*x + -0.00296895678887*y + 0.013446003463)/0.243315373562 #= -0.013446003463
    print z

inputeq(-0.2800472771896436, -1.1576054007896723, -0.07220335040254756)


    print 'Looking for person animations --- skipable'
    print 'Starts routine greet animation---detects person WOZ'
    print 'drawing the first contours'
    print 'run contemplating-Random'
    print 'draw second contours'
    print 'begin encouraging --- WOZ,possible skip'
    print 'encouraging Person --- WOZ'
    print 'observe person drawing---WOZ'
    # user has to hit enter to determine when person is finished
    print 'sign painting'
    print 'WOZ encouraging human to sign'
    print 'running goodbye animation --- WOZ'


'''
import os
#os.path.join('robot_img_v2/','meatbag_1.png')
img = cv2.imread(os.path.join('robosignature.png'))
#print img
DN_LIB.ImageContoursCustomSet1(img,isTesting=True)