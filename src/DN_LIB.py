#import urx
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
        self.endPntPose = [-0.14959202618776724, -0.6892203786569369, 0.45944469344501543,
                           -3.141369099840455, -0.023765232731069934, -0.018604100882098216]
        self.ResetAnimation()
        return

    def ResetAnimation(self):
        self.Animations = self.importAnimationCSV()
        return

    def importAnimationCSV(self):
        aniPose = []
        animation=None
        with open(rospy.get_param('AnimationsFileLoc')) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if len(row)==1:
                    if animation!=None:
                        aniPose.append(animation)
                    animation = (str(row).split(':')[1][:-2], [])
                elif len(row)==6:
                    animation[1].append([float(row[0]),float(row[1]),float(row[2]),float(row[3]),float(row[4]),float(row[5])])
                elif len(row)==2:
                    animation[1].append([row[0],row[1]])
            aniPose.append(animation)
        return aniPose

    def convertToTDspaceList(self,input, sz):
        def DetermineZ(x, y):
            return -((self.zPlaneParameters[0] * x) + (self.zPlaneParameters[1] * y) - self.zPlaneParameters[3]) / \
                   self.zPlaneParameters[2]

        Imheight = sz[0]
        Imwidth = sz[1]

        def checkRange(val, Max, Min, typ):
            if (val <= Max and val >= Min) or (val <= Min and val >= Max):
                return True
            print val, ' was out of range between ', Min, ' ', Max, typ
            return False

        if Imwidth > Imheight:
            print 'Recognized width is greater than height'
            lclXMax = self.xZero
            lclXZero = self.xMax
            newheight = float(Imheight) / float(Imwidth) * (abs(float(lclXMax) - lclXZero))
            print newheight, (abs(float(lclXMax) - lclXZero))
            diff = [self.md[1] + float(newheight / 2), self.md[1] - float(newheight / 2)]
            lclYZero = min(diff)
            lclYMax = max(diff)
        else:
            print 'Recognized height is greater than width'
            lclYZero = self.yZero
            lclYMax = self.yMax
            newwidth = Imwidth / Imheight * (abs(lclYMax - lclYZero))
            print Imheight, newwidth
            diff = [self.md[0] + float(newwidth / 2), self.md[0] - float(newwidth / 2)]
            lclXMax = max(diff)
            lclXZero = min(diff)
        #fixes orientation of the image
        opstch = [lclXZero,lclXMax,lclYZero,lclYMax]
        if self.section==0:
            lclXZero = opstch[0]
            lclXMax=opstch[1]
            lclYZero=opstch[2]
            lclYMax=opstch[3]
        elif self.section==1:
            lclXZero = opstch[2]
            lclXMax = opstch[3]
            lclYZero = opstch[1]
            lclYMax = opstch[0]
        elif self.section == 2:
            lclXZero = opstch[1]
            lclXMax=opstch[0]
            lclYZero=opstch[3]
            lclYMax=opstch[2]
        elif self.section == 3:
            lclXZero = opstch[3]
            lclXMax = opstch[2]
            lclYZero = opstch[0]
            lclYMax = opstch[1]

        lclImRatio = float(float(Imheight) / float(Imwidth))
        print 'Image Details:h.w = ', lclImRatio, Imheight, Imwidth, '----', float(lclYMax - lclYZero) / float(
            lclXMax - lclXZero)
        '''if abs(float(lclYMax - lclYZero)/float(lclXMax - lclXZero))!= lclImRatio:
            print (float(lclYMax) - float(lclYZero))/(float(lclXMax) - float(lclXZero)),'---', lclImRatio
            print 'lyMax',' --- ',lclYMax
            print 'lyZero', ' --- ', lclYZero
            print 'lxMax', ' --- ', lclXMax
            print 'lxZero', ' --- ', lclXZero
            print 'yMax', ' --- ', yMax
            print 'yZero', ' --- ', yZero
            print 'xMax', ' --- ', xMax
            print 'xZero', ' --- ', xZero
            raise ValueError('Ratio Off')'''
        print lclXMax, lclXZero, lclYMax, lclYZero, sz[0]
        # print 'xMax_lcl_real', lclXMax, xMax
        # print 'yMax_lcl_real', lclYMax, yMax
        # print 'xZro_lcl_real', lclXZero, xZero
        # print 'yZro_lcl_real', lclYZero, yZero
        ptlst = []
        a = float(lclXMax) - float(lclXZero)
        d = float(lclYMax) - float(lclYZero)
        for each in input:
            # X,Y = self.transposeOrientation(each[0],each[1])
            b = float(each[0]) / float(sz[1])
            c = float(a) * float(b)
            e = float(each[1]) / float(sz[0])
            f = float(e) * float(d)
            x = c + float(lclXZero)
            y = f + float(lclYZero)
            if len(ptlst)==0 or math.sqrt(math.pow(x-ptlst[len(ptlst)-1][0],2)+math.pow(y-ptlst[len(ptlst)-1][1],2))>=0.0002:#euclidean distance between prvious x and y is greater than 0.0002
                ptlst.append([x, y, DetermineZ(x, y), self.endPntPose[3], self.endPntPose[4], self.endPntPose[5]])
            print x, y
            if not checkRange(x, lclXZero, lclXMax, ' for X') or not checkRange(y, lclYZero, lclYMax, ' for Y'):
                raise ValueError('Range Error')
        return ptlst

    def printAniPose(self):
        animationPose = self.rob.getl()
        #get x difference from md
        animationPose[0] = (self.md[0]-animationPose[0])
        #get y difference from md
        animationPose[1] = (self.md[1]-animationPose[1])
        #get z difference from md
        animationPose[2] = (self.zDraw-animationPose[2])
        print animationPose
        return

    def FindAnimations(self,Tag):
        aniTag = []
        for i in self.Animations:
            if str(i[0]).__contains__(Tag):
                aniTag.append(i)

        if len(aniTag)==0:
            print Tag
            raise ValueError('No value found for')
        elif len(aniTag)==1:
            return aniTag[0][0]
        return aniTag[random.randint(0,len(aniTag)-1)][0]

    def ReturnToInit(self):

        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        return

    '''
    Unexpected results... DO NOT USE
    def CompileAndRunAnAnimationDirectSocket(self, animationName):
        executable=[i for i in self.Animations if i[0] == animationName]
        strprog = "def RunAnimation():\n"
        for e in executable[0][1]:
            if e[0] != 'delay' and e[0] != 'Description':
                strprog += '    movel('+str(self.translateToDifferential(e))+',a='+str(self.a)+',v='+str(self.v)+')\n'
            elif e[0] == 'delay':
                strprog += '    sleep('+ e[1]+')\n'
            elif e[0] == 'Description':
                print e[1]
        strprog += "end"
        self.rob.send_program(strprog)

        return'''

    def ExecuteAnimationSingular(self, animationName):
        executeble = [i for i in self.Animations if i[0] == animationName]
        for e in executeble[0][1]:
            if e[0] != 'delay' and e[0] != 'Description':
                self.ExecuteSingleMotionWithInterrupt(self.translateToDifferential(e))
                print 'robPos: ', self.rob.getl()
            elif e[0] == 'delay':
                print 'Delaying For ', e[1]
                time.sleep(float(e[1]))
            elif e[0] == 'Description':
                print e[1]
            if self.IdleCon==False or self.RunningSocialAction==False:
                return
        return

    def resetPos(self):
        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        return


    #region variableAlterations
    def getAllVariables(self):

        print self.xZero, self.yZero, self.xMax, self.yMax,\
            self.initHoverPos, self.endPntPose, self.zHover,\
            self.zDraw, self.a, self.v, self.md
        return

    def SetZvals(self,zD):
        self.zDraw = zD
        self.zHover = self.zDraw + 0.04
        return

    def findIntecepts(self,originpt, horizontalpt, verticalpt):
        # get vertical lines
        pts = [originpt,
               [originpt[0], verticalpt[1]],
               [horizontalpt[0], originpt[1]],
               [horizontalpt[0], verticalpt[1]]]
        return pts

    def setMax_Min(self,btmLft, btmRht, TpLft, TpRht):
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


    def midpoint(self,p1, p2):
        return [float((p1[0] + p2[0]) / 2), float((p1[1] + p2[1]) / 2)]
    def GetAutoParam(self):
        self.initHoverPos = self.rob.getl()
        if self.initHoverPos[0] > 1:
            if self.initHoverPos[1] < 1:
                # 90
                print 'Calibrating For Section 1'
                positions = rospy.get_param('Section1_AutoFill')
            else:
                # 0
                positions = rospy.get_param('Section0_AutoFill')
        else:
            if self.initHoverPos[1] < 1:
                # 180
                positions = rospy.get_param('Section2_AutoFill')
            else:
                # 270
                positions = rospy.get_param('Section3_AutoFill')
        self.BottomLeft = positions[0]
        self.TopLeft = positions[1]
        self.TopRight = positions[2]
        self.BottomRight = positions[3]
        return
    def buildZCartisianPlane3Pts(self,bottomLeft, topLeft, topRight, bottomRight):
        index = [bottomLeft[2], topLeft[2], topRight[2], bottomRight[2]].index(
            min([bottomLeft[2], topLeft[2], topRight[2], bottomRight[2]]))
        indices = [index - 1, index, index + 1]
        if indices[0] < 0:
            indices[0] = 3
        elif indices[2] > 3:
            indices[2] = 0
        pts = [bottomLeft, topLeft, topRight, bottomRight]
        p1 = np.array(pts[indices[0]])
        p2 = np.array(pts[indices[1]])
        p3 = np.array(pts[indices[2]])
        # print p1,p2,p3
        v1 = p3 - p1
        v2 = p2 - p1

        # the cross product is a vector normal to the plane
        cp = np.cross(v1, v2)
        a, b, c = cp

        # This evaluates a * x3 + b * y3 + c * z3 which equals d
        d = np.dot(cp, p3)

        print('The equation is {0}x + {1}y + {2}z = {3}'.format(a, b, c, d))

        #import matplotlib.pyplot as plt
        #from mpl_toolkits.mplot3d import Axes3D
        #fig = plt.figure()
        #ax = fig.add_subplot(111, projection='3d')

        x = np.linspace(-2, 14, 5)
        y = np.linspace(-2, 14, 5)
        X, Y = np.meshgrid(x, y)

        #Z = (d - a * X - b * Y) / c

        # plot the mesh. Each array is 2D, so we flatten them to 1D arrays
        #ax.plot(X.flatten(),Y.flatten(),Z.flatten(), 'bo ')

        # plot the original points. We use zip to get 1D lists of x, y and z
        # coordinates.
        #ax.plot(*zip(p1, p2, p3), color='r', linestyle=' ', marker='o')

        # adjust the view so we can see the point/plane alignment
        #ax.view_init(0, 22)
        #plt.tight_layout()
        # plt.savefig('images/plane.png')
        # plt.show()

        self.zPlaneParameters = [a, b, c, d]
        return


    def PrintAllVar(self):
        self.printMovementVariables()
        print 'Midpoint = ',self.md
        return

    #endregion
    def Calibrate(self,cmdCal=False):
        if rospy.get_param('AutoCalibrate') and cmdCal==False:
            self.GetAutoParam()
        else:
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Bottom Left')
            self.rob.set_freedrive(False)
            self.BottomLeft = self.rob.getl()
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Top Left')
            self.rob.set_freedrive(False)
            self.TopLeft = self.rob.getl()
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Top Right')
            self.rob.set_freedrive(False)
            self.TopRight = self.rob.getl()
            self.rob.set_freedrive(True)
            raw_input('Press Enter to confirm Bottom Right')
            self.rob.set_freedrive(False)
            self.BottomRight = self.rob.getl()
            print self.BottomLeft
            print self.TopLeft
            print self.TopRight
            print self.BottomRight

        self.xMax, self.xZero, self.yZero, self.yMax=self.setMax_Min(self.BottomLeft,self.BottomRight,self.TopLeft,self.TopRight)
        self.buildZCartisianPlane3Pts([self.BottomLeft[0],self.BottomLeft[1],self.BottomLeft[2]],[self.TopLeft[0],self.TopLeft[1],self.TopLeft[2]],
                                      [self.TopRight[0],self.TopRight[1],self.TopRight[2]],[self.BottomRight[0],self.BottomRight[1],self.BottomRight[2]])
        self.md = self.midpoint([self.xZero, self.yZero], [self.xMax, self.yMax])
        if abs(self.xMax - self.xZero) < abs(self.yMax - self.yZero):
            # x value is drawback,need to invert axis
            print 'case1'
            x = self.xMax - ((self.xMax - self.xZero) * 1.5)
            y = self.yZero + ((self.yMax - self.yZero) * 0.5)
            z = self.zDraw + 0.4
            # invert axis
            inv = [self.xZero, self.xMax, self.yZero, self.yMax]
            self.xMax = inv[3]
            self.yMax = inv[1]
            self.xZero = inv[2]
            self.yZero = inv[0]
        else:
            print 'case2'
            x = self.xZero + ((self.xMax - self.xZero) * 0.5)
            y = self.yMax - ((self.yMax - self.yZero) * 1.5)
            z = self.zDraw + 0.4
        self.initHoverPos = [x, y, z, 2.213345336120183,
                        -2.212550352198813, 0.01]
        print 'Please Step Away, Moving to Init Hover Position'
        if self.initHoverPos[0] > 1:
            if self.initHoverPos[1] < 1:
                self.section = 1
            else:
                self.section = 0
        else:
            if self.initHoverPos[1] < 1:
                self.section = 2
            else:
                self.section = 3

        #print initHoverPos,xMax, xZero, yMax, yZero
        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        return
