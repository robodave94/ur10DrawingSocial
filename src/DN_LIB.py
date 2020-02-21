import urx
import rospy
import numpy as np
import math
import csv
import time
import random
import RobotObj


class DrawingRobotStructure(RobotObj.RobotResearchObject):

    def InitializeVariablesROS(self):
        self.InitBaseVariables()

        # The parameters of the calibrated canvas
        self.canvasWidth = 0
        self.canvasHeight = 0
        self.canvasMidpoint = 0

        #cropped sizing
        self.canvasCroppedWidth = 0
        self.canvasCroppedHeight = 0
        self.xShift = 0
        # Save each recorded calibrated point into this class
        self.bottomLeftPoint = [0, 0, 0]
        self.topLeftPoint = [0, 0, 0]
        self.topRightPoint = [0, 0, 0]
        self.bottomRightPoint = [0, 0, 0]

        # These parameters represent the variables for translating the alternative values to new coordinates of drawing
        self.theta = 0
        self.Xr = 0
        self.Yr = 0

        self.heightErrorDisplacement = 0

        # The horizontal Planular Equations
        # ax + by + cz + d = 0
        self.plE1_a = 0
        self.plE1_b = 0
        self.plE1_c = 0
        self.plE1_d = 0

        self.endPntPose = [-0.14959202618776724, -0.6892203786569369, 0.45944469344501543,
                           -3.141369099840455, -0.023765232731069934, -0.018604100882098216]
        self.ResetAnimation()
        return

    def constructDrawingCanvas(self):
        p1 = np.array(self.bottomLeftPoint)
        p2 = np.array(self.bottomRightPoint)
        p3 = np.array(self.topLeftPoint)
        # print p1,p2,p3
        v1 = p3 - p1
        v2 = p2 - p1
        cp = np.cross(v1, v2)
        a, b, c = cp
        d = np.dot(cp, p3)
        self.plE1_a = a
        self.plE1_b = b
        self.plE1_c = c
        self.plE1_d = d

        # Display the resulting error margin of the constructed canvas
        testingInputTopRight = self.projectPointToPlane(self.topRightPoint[0], self.topRightPoint[1])
        self.heightErrorDisplacement = testingInputTopRight - self.topRightPoint[2]
        print 'Error of ', self.heightErrorDisplacement, ' found'

        # Estimate the canvas width
        bottomWidth = math.sqrt(pow((self.bottomRightPoint[0] - self.bottomLeftPoint[0]) , 2) + pow((self.bottomRightPoint[1] - self.bottomLeftPoint[1]), 2))
        topWidth = math.sqrt(pow((self.topRightPoint[0] - self.topLeftPoint[0]), 2) + pow((self.topRightPoint[1] - self.topLeftPoint[1]), 2))
        self.canvasWidth = (bottomWidth + topWidth) / 2

        # Estimate the canvas height
        leftHeight = math.sqrt(pow((self.topLeftPoint[0] - self.bottomLeftPoint[0]), 2) + pow((self.topLeftPoint[1] - self.bottomLeftPoint[1]), 2))
        rightHeight = math.sqrt(pow((self.topRightPoint[0] - self.bottomRightPoint[0]), 2) + pow((self.topRightPoint[1] - self.bottomRightPoint[1]), 2))
        self.canvasHeight = (leftHeight + rightHeight) / 2

        self.Xr = self.bottomLeftPoint[0]
        self.Yr = self.bottomLeftPoint[1]

        # Find Theta of the canvas
        # In this method we simply calculate the angles from the theta transform to ours
        angA = math.atan2(self.bottomRightPoint[1] - self.bottomLeftPoint[1], self.bottomRightPoint[0] - self.bottomLeftPoint[0])
        angB = math.atan2(self.topRightPoint[1] - self.topLeftPoint[1],
                          self.topRightPoint[0] - self.topLeftPoint[0])
        #angA = math.atan2(self.topLeftPoint[1] - self.bottomLeftPoint[1], self.topLeftPoint[0] - self.bottomLeftPoint[0])
        #angB = math.atan2(self.topRightPoint[1] - self.bottomRightPoint[1],self.topRightPoint[0] - self.bottomRightPoint[0])
        self.theta = (angA + angB) / 2

        # find the canvas midpoint
        # BLTR
        xM1 = (self.bottomLeftPoint[0] + self.topRightPoint[0]) / 2
        yM1 = (self.bottomLeftPoint[1] + self.topRightPoint[1]) / 2

        xM2 = (self.bottomRightPoint[0] + self.topLeftPoint[0]) / 2
        yM2 = (self.bottomRightPoint[1] + self.topLeftPoint[1]) / 2

        self.canvasMidpoint = [(xM1 + xM2) / 2, (yM1 + yM2) / 2]

        #
        Zini = self.projectPointToPlane(self.canvasMidpoint[0], self.canvasMidpoint[1])
        self.initHoverPos = [self.canvasMidpoint[0], self.canvasMidpoint[1], Zini, 2.213345336120183,-2.212550352198813, 0.01]
        return

    def calculateCroppedSizing(self,imgHeight,imgWidth):
        #ratio of height to width of image
        imgRatio = (float)(imgHeight)/imgWidth
        #canvas ratio
        canvasRatio = (float)(self.canvasHeight)/self.canvasWidth
        #when canvas ratio is less than image, we crop the width
        theta = math.atan(imgRatio)
        if canvasRatio<imgRatio:
            self.canvasCroppedHeight = self.canvasHeight
            self.canvasCroppedWidth = self.canvasHeight / math.tan(theta)
            self.xShift = (self.canvasWidth - self.canvasCroppedWidth) / 2
        elif imgRatio>canvasRatio:
            self.canvasCroppedWidth = self.canvasWidth
            self.canvasCroppedHeight = self.canvasWidth * math.tan(theta)
            self.xShift = 0
        else:
            self.canvasCroppedWidth = self.canvasWidth
            self.canvasCroppedHeight = self.canvasHeight
            self.xShift = 0


        print 'DIMENSIONS FOR EVALUATION'
        print imgRatio
        print canvasRatio
        print imgWidth,imgHeight
        print self.canvasWidth, self.canvasHeight
        print self.canvasCroppedWidth,self.canvasCroppedHeight
        return

    def projectPointToPlane(self,x, y):
        return -(self.plE1_a * x + self.plE1_b * y + self.plE1_d) / self.plE1_c

    def cropPlaneToImage(self):
        return

    def scalePixelsToWorldCoordinates(self,Xi, Yi,imageWidth,imageHeight):
        xS = Xi * (self.canvasCroppedWidth / imageWidth)
        yS = Yi * (self.canvasCroppedHeight / imageHeight)
        return np.array([xS, yS])

    def getTranslatedPositionComponents(self,x, y):
        xS = x+self.xShift
        xR = self.Xr + xS * math.cos(self.theta) - y * math.sin(self.theta)
        yR = self.Yr + y * math.cos(self.theta) + x * math.sin(self.theta)
        return np.array([xR, yR])

    # This code recieves contour points input along the waypoints and converts them to real world systems
    def PixelTranslation(self, xInput, yInput, imageH, imageW):
        '''xS = xInput * (self.canvasWidth / imageWidth)
        yS = yInput * (self.canvasHeight / imageHeight)
        xR = self.Xr + xS * math.cos(self.theta) - yS * math.sin(self.theta)
        yR = self.Yr + yS * math.cos(self.theta) + xS * math.sin(self.theta)
        zR = (-self.plE1_a * xR - self.plE1_b * yR - self.plE1_d) / self.plE1_c
        return [xR,yR,zR]
        '''


        s2 = self.scalePixelsToWorldCoordinates(Xi=xInput, Yi=yInput,imageWidth=imageW,imageHeight=imageH)
        s3 = self.getTranslatedPositionComponents(x=s2[0], y=s2[1])
        return [s3[0], s3[1], self.projectPointToPlane(x=s3[0], y=s3[1])]


    def ResetAnimation(self):
        self.Animations = self.importAnimationCSV()
        return

    def importAnimationCSV(self):
        aniPose = []
        animation = None
        with open(rospy.get_param('AnimationsFileLoc')) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if len(row) == 1:
                    if animation != None:
                        aniPose.append(animation)
                    animation = (str(row).split(':')[1][:-2], [])
                elif len(row) == 6:
                    animation[1].append(
                        [float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])])
                elif len(row) == 2:
                    animation[1].append([row[0], row[1]])
            aniPose.append(animation)
        return aniPose

    def printAniPose(self):
        animationPose = self.rob.getl()
        # get x difference from md
        animationPose[0] = (self.md[0] - animationPose[0])
        # get y difference from md
        animationPose[1] = (self.md[1] - animationPose[1])
        # get z difference from md
        animationPose[2] = (self.zDraw - animationPose[2])
        print
        animationPose
        return

    def FindAnimations(self, Tag):
        aniTag = []
        for i in self.Animations:
            if str(i[0]).__contains__(Tag):
                aniTag.append(i)
        if len(aniTag) == 0:
            print
            Tag
            raise ValueError('No value found for')
        elif len(aniTag) == 1:
            return aniTag[0][0]
        return aniTag[random.randint(0, len(aniTag) - 1)][0]

    def ReturnToInit(self):

        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        return

    def ExecuteAnimationSingular(self, animationName):
        executeble = [i for i in self.Animations if i[0] == animationName]
        velBackup = self.v
        accBackup = self.a
        for e in executeble[0][1]:
            if e[0] != 'delay' and e[0] != 'Description' and e[0] != 'speed':
                #self.ExecuteSingleMotionWithInterrupt(self.translateToDifferential(e))
                self.ExecuteSingleMotionWithInterrupt(e)
                print('robPos: ', self.rob.getl())
            elif e[0] == 'speed':
                self.a = float(e[1])
                self.v = float(e[1])
            elif e[0] == 'delay':
                print('Delaying For ', e[1])
                time.sleep(float(e[1]))
            elif e[0] == 'Description':
                print(e[1])
            if self.IdleCon == False or self.RunningSocialAction == False:
                self.v = velBackup
                self.a = accBackup
                return
        self.v = velBackup
        self.a = accBackup
        return

    def resetPos(self):
        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        return

    # region variableAlterations
    def getAllVariables(self):

        print
        self.xZero, self.yZero, self.xMax, self.yMax, \
        self.initHoverPos, self.endPntPose, self.zHover, \
        self.zDraw, self.a, self.v, self.md
        return

    def SetZvals(self, zD):
        self.zDraw = zD
        self.zHover = self.zDraw + 0.04
        return

    def findIntecepts(self, originpt, horizontalpt, verticalpt):
        # get vertical lines
        pts = [originpt,
               [originpt[0], verticalpt[1]],
               [horizontalpt[0], originpt[1]],
               [horizontalpt[0], verticalpt[1]]]
        return pts

    def setMax_Min(self, btmLft, btmRht, TpLft, TpRht):
        mintercepts = self.findIntecepts([btmLft[0], btmLft[1]], [btmRht[0], btmRht[1]], [TpLft[0], TpLft[1]])
        maxtercepts = self.findIntecepts([TpRht[0], TpRht[1]], [TpLft[0], TpLft[1]], [btmRht[0], btmRht[1]])
        # find the minimum euclidean distance
        minDist = float(50)
        xZero = 0
        yZero = 0
        xMax = 0
        yMax = 0
        for Min in mintercepts:
            for Max in maxtercepts:
                if (minDist > math.sqrt((Max[0] - Min[0]) ** 2 + (Max[1] - Min[1]) ** 2)):
                    xZero = Min[0]
                    yZero = Min[1]
                    xMax = Max[0]
                    yMax = Max[1]

        self.SetZvals(float(sum([btmLft[2], btmRht[2], TpLft[2], TpRht[2]]) / 4))

        return xMax, xZero, yMax, yZero

    def midpoint(self, p1, p2):
        return [float((p1[0] + p2[0]) / 2), float((p1[1] + p2[1]) / 2)]

    def PrintAllVar(self):
        self.printMovementVariables()
        print 'Bottom Left Point',self.bottomLeftPoint
        print 'Top Left Point',self.topLeftPoint
        print 'Top Right Point',self.topRightPoint
        print 'Bottom Right Point',self.bottomRightPoint
        print 'Theta',self.theta
        print 'Relative X pose',self.Xr
        print 'Relative Y pose',self.Yr
        print 'Canvas Width', self.canvasWidth
        print 'Canvas Height',self.canvasHeight
        print 'Canvas Midpoint',self.canvasMidpoint
        print 'current position is', self.rob.getl()
        return


    def Calibrate(self, cmdCal=False):
        if rospy.get_param('AutoCalibrate') and cmdCal == False:
            self.bottomLeftPoint = rospy.get_param('bottomLeftPoint')
            self.topLeftPoint = rospy.get_param('topLeftPoint')
            self.topRightPoint = rospy.get_param('topRightPoint')
            self.bottomRightPoint = rospy.get_param('bottomRightPoint')
        else:
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Bottom Left')
            self.rob.set_freedrive(False)
            calPt = self.rob.getl()
            self.bottomLeftPoint = [calPt[0], calPt[1], calPt[2], ]
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Top Left')
            self.rob.set_freedrive(False)
            calPt = self.rob.getl()
            self.topLeftPoint = [calPt[0], calPt[1], calPt[2], ]
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Top Right')
            self.rob.set_freedrive(False)
            calPt = self.rob.getl()
            self.topRightPoint = [calPt[0], calPt[1], calPt[2], ]
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Bottom Right')
            self.rob.set_freedrive(False)
            calPt = self.rob.getl()
            self.bottomRightPoint = [calPt[0], calPt[1], calPt[2], ]

        self.constructDrawingCanvas()
        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        self.PrintAllVar()
        return
