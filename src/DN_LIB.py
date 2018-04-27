import urx
from urx import ursecmon
import logging
import cv2
import numpy as np
import math
from sklearn import cluster
from Tkinter import *
import csv
import scipy.linalg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import time
import threading
import random
import sys,os
#region variables Accessors
class DrawingRobotInstance (object):
    #region variables
    xZero=None
    yZero=None
    xMax=None
    yMax=None
    endPntPose=None
    initHoverPos = None
    delayVar=None
    zDraw=None
    zHover=None
    a=None
    v=None
    md=None
    gui=None
    rob=None
    secmon=None
    Animations=None
    zPlaneParameters=None
    #endregion

    #region variableInitialization
    def setGlobVarInit(self,ipadd):
        global xZero
        global yZero
        global xMax
        global yMax
        global endPntPose
        global delayVar
        global zDraw
        global zHover
        global a,v
        global md
        global gui
        global rob,secmon,Animations
        global zPlaneParameters

        xZero = -0.09482782036275914
        yZero = 0.605186565541524
        xMax = 0.45465803156181367
        yMax = 0.9040947542413041
        endPntPose = [0.7154552911907102, -0.18649728884114203, 0.5345011758600491, 2.213345336120183,
                      -2.212550352198813, 0.01]
        delayVar = 3
        zDraw = -0.027428343556382472
        zHover = zDraw + 0.03
        a=0.2
        v=0.2
        Animations = self.importAnimationCSV()
        md = self.midpoint([xZero, yZero], [xMax, yMax])
        rob = urx.Robot(ipadd)
        secmon = ursecmon.SecondaryMonitor(rob.host)
        rob.set_tcp((0, 0, 0.1, 0, 0, 0))
        rob.set_payload(2, (0, 0, 0.1))
        zPlaneParameters = [5,5,5,5]

        return
    #endregion


    def ResetAnimation(self):
        global Animations
        Animations = self.importAnimationCSV()
        return

    def importAnimationCSV(self):
        aniPose = []
        animation=None
        with open('AnimationCMD.csv') as csvfile:
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



    def RunDrawing(self,image,isTesting=False):
        lines = ImageContoursCustomSet1(image)
        for y in lines:
            pts = self.convertToTDspaceList(y, [image.shape[0], image.shape[1]])
            self.DrawContour(pts)
            # exit script on completion
            #print lines.index(y),' Out of ',len(lines)
        print 'Completed Contour Construction'
        rob.movel(initHoverPos, acc=a, vel=v, wait=True)
        return

    def printAniPose(self):
        animationPose = rob.getl()
        #get x difference from md
        animationPose[0] = (md[0]-animationPose[0])
        #get y difference from md
        animationPose[1] = (md[1]-animationPose[1])
        #get z difference from md
        animationPose[2] = (zDraw-animationPose[2])
        print animationPose
        return

    def ExtractDrawing(self):
        import glob
        listImgFiles=[]
        for file in glob.glob(os.path.join('robot_img_v2/','*_1.png')):
            listImgFiles.append(file[:-6])
        index=random.randint(0, len(listImgFiles) - 1)
        self.Imgs =  [cv2.imread(str(listImgFiles[index])+'_1.png'),
                cv2.imread(str(listImgFiles[index]) + '_2.png')]
        return


    def SocialAction(self,activity,sInd=0):
        if activity == 'ExecuteDrawing':
            print self.Imgs[sInd]
            self.RunDrawing(self.Imgs[sInd])
        elif activity == 'Greeting':
            # execute a single greeting animation
            ac = self.FindAnimations('Greet')
            self.ExecuteAnimation(ac)
        elif activity == 'ContemplateAnimation':
            # execute a single greeting animation
            ac = self.FindAnimations('Contemplate')
            self.ExecuteAnimation(ac)

        # print drawing
        return

    """
    Set Names to contain one of the options
    Search
    Greet
    DrawFirstHalf
    Contemplate
    DrawSecondHalf
    EnourageDraw
    ObserveDraw
    RobotSign
    EnourageSign
    ObserveSign
    Goodbye
    """


    def RunContinousSocialAction(self,Action):
        """ Method that runs forever """
        if Action == 'ObserveUser':
            while self.LoopActive == True:
                # running idle animations
                # find AnimationNAMEwithidletage
                ac = self.FindAnimations('ObserveDraw')
                self.ExecuteAnimationSingular(ac)
        elif Action == 'ObserveUserSigning':
            while self.LoopActive == True:
                # running idle animations
                # find AnimationNAMEwithidletage
                ac = self.FindAnimations('ObserveSign')
                self.ExecuteAnimationSingular(ac)
        elif Action == 'idle':
            while self.LoopActive == True:
                # running idle animations
                # find AnimationNAMEwithidletage
                ac = self.FindAnimations('Search')
                print 'Found Animation ',ac
                self.ExecuteAnimationSingular(ac)
                print "Attempting to return Home"
        elif Action == 'EncourageDrawing':
            # execute a single greeting animation
            while self.LoopActive == True:
                # running idle animations
                # find AnimationNAMEwithidletage
                ac = self.FindAnimations('EncourageDraw')
                self.ExecuteAnimationSingular(ac)
        elif Action == 'EncourageSigining':
            # execute a single greeting animation
            while self.LoopActive == True:
                # running idle animations
                # find AnimationNAMEwithidletage
                ac = self.FindAnimations('EncourageSign')
                self.ExecuteAnimationSingular(ac)
        elif Action == 'GoodBye':
            while self.LoopActive == True:
                ac = self.FindAnimations('Goodbye')
                self.ExecuteAnimationSingular(ac)
        return

    def blockPrint(self):
        sys.stdout = open(os.devnull, 'w')

    # Restore
    def enablePrint(self):
        sys.stdout = sys.__stdout__


    def RunningSocialRoutineV1(self):
        class bcolors:
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'


        while True:
            self.ExtractDrawing()
            print 'Got Drawing'
            self.LoopActive = True
            rob.movel(initHoverPos, wait=True, acc=a, vel=v)
            self.RunContinousSocialAction('idle')
            print bcolors.WARNING + 'Completed idle, Running greeting' + bcolors.ENDC
            self.LoopActive = True
            self.SocialAction('Greeting')
            print bcolors.WARNING + 'Completed greeting, Running First Drawing' + bcolors.ENDC
            self.LoopActive = True
            #run first set of drawing Points
            self.SocialAction('ExecuteDrawing')
            print bcolors.WARNING + 'Completed First Drawing, Running Contemplate animation' + bcolors.ENDC
            self.LoopActive = True
            self.SocialAction('ContemplateAnimation')
            print bcolors.WARNING + 'Completed comptempation, Running Second Drawing' + bcolors.ENDC
            self.LoopActive = True
            self.SocialAction('ExecuteDrawing',sInd=1)
            print bcolors.WARNING + 'Now encouraging user to draw' + bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('EncourageDrawing')
            print bcolors.WARNING + 'Now observing user draw' + bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('ObserveUser')
            #sigining
            print bcolors.WARNING + 'User has finished drawing now signing' + bcolors.ENDC
            self.LoopActive = True
            self.RunDrawing(cv2.imread(os.path.join('robot_img_v2/','robosign.png')))
            print bcolors.WARNING + 'Now encourage user to draw' + bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('EncourageSigining')
            print bcolors.WARNING + 'Observing user signing' + bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('ObserveUserSigning')
            print bcolors.WARNING + 'Waving goodbye' + bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('GoodBye')
            rtxt = raw_input("Enter q to quit of enter to repeat : ")
            if rtxt=='q':
                break

    '''    def StartThread(self,actionableCall):
        thread = threading.Thread(target=self.RunContinousSocialAction(actionableCall), args=())
        thread.daemon = True
        thread.start()
        while True:
            i = raw_input("Press Enter to continue. Currently At " + actionableCall)
            if not i:
                self.LoopActive = False
                break
        rob.stopl()
        return'''

    def setFreeDriveFalse(self):
        rob.set_freedrive(False)
        return

    def FindAnimations(self,Tag):
        aniTag = []
        for i in Animations:
            if str(i[0]).__contains__(Tag):
                aniTag.append(i)

        if len(aniTag)==0:
            print Tag
            raise ValueError('No value found for')
        elif len(aniTag)==1:
            return aniTag[0][0]
        return aniTag[random.randint(0,len(aniTag)-1)][0]

    def ExecuteAnimationSingular(self,animationName,wait=True):
        import select
        sys.stdin
        executeble =  [i for i in Animations if i[0] == animationName]
        for e in executeble[0][1]:
            if e[0]!='delay' and e[0]!='Description':
                rob.movel(self.translateToDifferential(e),wait=True, acc=a, vel=v)
            elif e[0]=='delay':
                print 'Delaying For ',e[1]
                time.sleep(float(e[1]))
            elif e[0]=='Description':
                print e[1]
            q, _, _ = select.select([sys.stdin], [], [], 0.2)
            print q
            if (q):
                self.LoopActive=False
                sys.stdin.read(1)
                break
            else:
                print "You said nothing!"

        return


    def ExecuteAnimation(self,animationName,wait=True):
        executeble =  [i for i in Animations if i[0] == animationName]
        listofpoints=[]
        for e in executeble[0][1]:
            if e[0]!='delay' and e[0]!='Description':
                listofpoints.append(self.translateToDifferential(e))
            elif e[0]=='delay':
                if len(listofpoints)!=0:
                    rob.movels(listofpoints, wait=wait, acc=a, vel=v)
                    listofpoints=[]
                print 'Delaying For ',e[1]
                time.sleep(float(e[1]))
            elif e[0]=='Description':
                print e[1]
                if len(listofpoints)!=0:
                    rob.movels(listofpoints, wait=wait, acc=a, vel=v)
                    listofpoints = []
        if  len(listofpoints)!=0:
            rob.movels(listofpoints,wait=wait, acc=a, vel=v)


        return

    def translateToDifferential(self,pt):
        newpt = [pt[0],pt[1],pt[2],pt[3],pt[4],pt[5]]
        if initHoverPos[0] > 1:
            if initHoverPos[1] < 1:
                #90
                newpt[1] = md[0] + (pt[0])
                newpt[0] = md[1] + (pt[1])
                newpt[2] = zDraw + abs(pt[2])
            else:
                #0
                newpt[0] = md[0] + (pt[0])
                newpt[1] = md[1] + (pt[1])
                newpt[2] = zDraw + abs(pt[2])
        else:
            if initHoverPos[1] < 1:
                # 180
                newpt[0] = md[0] + (pt[0]*-1)
                newpt[1] = md[1] + (pt[1]*-1)
                newpt[2] = zDraw + abs(pt[2])
            else:
                # 270
                newpt[1] = md[0] + (pt[0]*-1)
                newpt[0] = md[1] + (pt[1]*-1)
                newpt[2] = zDraw + abs(pt[2])
        print newpt
        return newpt

    def ShutdownRoutine(self):
        rob.close()
        secmon.close()
        exit()
        return

    def resetPos(self):
        rob.movel(initHoverPos, acc=a, vel=v, wait=True)
        return

    def stopRobot(self):
        rob.stop()
        return

    def InitGUI(self):
        global gui
        gui = Tk()
        gui.minsize(1500,750)
        gui.maxsize(1500, 750)
        entry1 = Entry(gui, width=10)
        entry2 = Entry(gui, width=10)
        button_Calibrate = Button(gui, text='Calibrate',command=self.Calibrate())
        button_shutdown = Button(gui, text='Shutdown', command=self.ShutdownRoutine())
        button_reset = Button(gui, text='Reset Position', command=self.resetPos())
        button_displayVariables = Button(gui, text='Display Robot Parameters', command=self.getAllVariables())
        button_StopMoving = Button(gui, text='Stop Movement', command=self.stopRobot())
        #TODO: upgrade paramters
        button_SetVariables = Button(gui, text='Set movement parameters', command=self.setVar(1,1,1))
        button_imread = Button(gui, text='Draw Image', command=self.RunDrawing(''))
        button_printAniPose = Button(gui, text='Print Animation Pose', command=self.printAniPose())
        button_executeAnimation = Button(gui, text='Run Animation', command=self.ExecuteAnimation(''))
        entry1.pack()
        entry2.pack()
        button_Calibrate.pack()
        button_displayVariables.pack()
        button_executeAnimation.pack()
        button_imread.pack()
        button_printAniPose.pack()
        button_reset.pack()
        button_SetVariables.pack()
        button_shutdown.pack()
        button_StopMoving.pack()
        gui.mainloop()
        return


    #region robotCalibration
    def Calibrate(self):
        global initHoverPos, xMax, xZero, yMax, yZero,md
        rob.set_freedrive(True)
        raw_input('Press Enter to confirm Bottom Left')
        rob.set_freedrive(False)
        BottomLeft = rob.getl()
        rob.set_freedrive(True)
        raw_input('Press Enter to confirm Top Left')
        rob.set_freedrive(False)
        TopLeft = rob.getl()
        rob.set_freedrive(True)
        raw_input('Press Enter to confirm Top Right')
        rob.set_freedrive(False)
        TopRight = rob.getl()
        rob.set_freedrive(True)
        raw_input('Press Enter to confirm Bottom Right')
        rob.set_freedrive(False)
        BottomRight = rob.getl()
        print BottomLeft
        print TopLeft
        print TopRight
        print BottomRight

        xMax, xZero, yZero, yMax=self.setMax_Min(BottomLeft,BottomRight,TopLeft,TopRight)
        self.buildZCartisianPlane3Pts([BottomLeft[0],BottomLeft[1],BottomLeft[2]],[TopLeft[0],TopLeft[1],TopLeft[2]],
                                      [TopRight[0],TopRight[1],TopRight[2]],[BottomRight[0],BottomRight[1],BottomRight[2]])

        if abs(xMax - xZero) < abs(yMax - yZero):
            # x value is drawback,need to invert axis
            print 'case1'
            x = xMax - ((xMax - xZero) * 1.5)
            y = yZero + ((yMax - yZero) * 0.5)
            z = zDraw + 0.4
            # invert axis
            inv = [xZero, xMax, yZero, yMax]
            xMax = inv[3]
            yMax = inv[1]
            xZero = inv[2]
            yZero = inv[0]
        else:
            print 'case2'
            x = xZero + ((xMax - xZero) * 0.5)
            y = yMax - ((yMax - yZero) * 1.5)
            z = zDraw + 0.4
        initHoverPos = [x, y, z, 2.213345336120183,
                        -2.212550352198813, 0.01]
        print 'Please Step Away, Moving to Init Hover Position'
        #print initHoverPos,xMax, xZero, yMax, yZero
        rob.movel(initHoverPos,acc=a,vel=v)
        # print xMax,xZero,yMax,yZero,x,y,z
        # time.sleep(2)
        md = self.midpoint([xZero, yZero], [xMax, yMax])
        return
    #endregion

    def buildZCartisianPlane3Pts(self,bottomLeft,topLeft,topRight,bottomRight):
        global zPlaneParameters
        index = [bottomLeft[2],topLeft[2],topRight[2],bottomRight[2]].index(min([bottomLeft[2],topLeft[2],topRight[2],bottomRight[2]]))
        indices = [index-1,index,index+1]
        if indices[0]<0:
            indices[0]=3
        elif indices[2]>3:
            indices[2]=0
        pts = [bottomLeft, topLeft, topRight,bottomRight]
        p1 = np.array(pts[indices[0]])
        p2 = np.array(pts[indices[1]])
        p3 = np.array(pts[indices[2]])
        #print p1,p2,p3
        v1 = p3 - p1
        v2 = p2 - p1

        # the cross product is a vector normal to the plane
        cp = np.cross(v1, v2)
        a, b, c = cp

        # This evaluates a * x3 + b * y3 + c * z3 which equals d
        d = np.dot(cp, p3)

        print('The equation is {0}x + {1}y + {2}z = {3}'.format(a, b, c, d))

        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x = np.linspace(-2, 14, 5)
        y = np.linspace(-2, 14, 5)
        X, Y = np.meshgrid(x, y)

        Z = (d - a * X - b * Y) / c

        # plot the mesh. Each array is 2D, so we flatten them to 1D arrays
        ax.plot(X.flatten(),
                Y.flatten(),
                Z.flatten(), 'bo ')

        # plot the original points. We use zip to get 1D lists of x, y and z
        # coordinates.
        ax.plot(*zip(p1, p2, p3), color='r', linestyle=' ', marker='o')

        # adjust the view so we can see the point/plane alignment
        ax.view_init(0, 22)
        plt.tight_layout()
        #plt.savefig('images/plane.png')
        #plt.show()

        zPlaneParameters = [a,b,c,d]
        return

    #region variableAlterations
    def getAllVariables(self):
        print xZero, yZero, xMax, yMax,initHoverPos, endPntPose, zHover, zDraw, a, v, md
        return

    def setVar(self,dlay, accel, veloc):
        global delayVar, a, v
        a = accel
        v = veloc
        delayVar = dlay
        print 'updated a,v,delay'
        return

    def setMax_Min(self,btmLft,btmRht, TpLft,TpRht):
        mintercepts = self.findIntecepts([btmLft[0],btmLft[1]],[btmRht[0], btmRht[1]], [TpLft[0],TpLft[1]])
        maxtercepts = self.findIntecepts([TpRht[0], TpRht[1]], [TpLft[0], TpLft[1]],[btmRht[0], btmRht[1]])
        #find the minimum euclidean distance
        minDist = float(50)
        xZero = 0
        yZero = 0
        xMax = 0
        yMax = 0
        for Min in mintercepts:
            for Max in maxtercepts:
                if(minDist>math.sqrt((Max[0]-Min[0])**2+ (Max[1]-Min[1])**2)):
                    xZero = Min[0]
                    yZero = Min[1]
                    xMax = Max[0]
                    yMax = Max[1]

        self.SetZvals(float(sum([btmLft[2],btmRht[2], TpLft[2],TpRht[2]]) / 4))

        return xMax, xZero, yMax, yZero

    def findIntecepts(self,originpt,horizontalpt,verticalpt):
        #get vertical lines
        pts =   [originpt,
                [originpt[0],verticalpt[1]],
                [horizontalpt[0],originpt[1]],
                [horizontalpt[0],verticalpt[1]]]

        #get horizontal lines
        return pts

    def SetZvals(self,zD):
        global zDraw, zHover
        zDraw = zD
        zHover = zDraw + 0.04
        return
    #endregion

    #region Translation to 3d space, redundant as image rotates when calculating contours
    '''def transposeOrientation(self,point, origin, deg):
        angle = np.deg2rad(deg)
        ox = origin[0]
        oy=origin[1]
        px = point[0]
        py = point[1]

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        print px,py,'--',qx,qy
        temp_point = point[0] - origin[0], point[1] - origin[1]
        temp_point = (temp_point[0] * math.cos(angle) - temp_point[1] * math.sin(angle),
                      temp_point[0] * math.sin(angle) + temp_point[1] * math.cos(angle))
        temp_point = temp_point[0] + origin[0], temp_point[1] + origin[1]

        print point[0],point[1],'---',temp_point[0],temp_point[1]

        return temp_point[0],temp_point[1]'''


    def AutoCalibrate(self):
        #calculated endpt=0.04543,-0.921935
        #xZero,yZero,xMax,yMax
        #0.354360007582 -0.713510701163 -0.26350156373 -1.13036014377
        #zDraw = -0.0433069014414
        #zHover = zDraw + 0.04
        #init hover
        #[0.04539028597592009, -0.5050933527023307, 0.35669773528119203, 2.2132137442512105, -2.212639604541358, 0.009988270617139626]
        global initHoverPos, xMax, xZero, yMax, yZero, md,zDraw,zHover
        initHoverPos = rob.getl()
        if initHoverPos[0] > 1:
            if initHoverPos[1] < 1:
                #90
                BottomLeft = []
                BottomRight = []
                TopLeft = []
                TopRight = []
            else:
                #0
                BottomLeft = []
                BottomRight = []
                TopLeft = []
                TopRight = []
        else:
            if initHoverPos[1] < 1:
                # ONLY ONE THAT WORKS
                BottomLeft=[0.30868772001069467, -0.73450335197235, -0.040263117639264066, -2.6036090379801062, 1.7406307646013461,-0.04407629142930036]
                TopLeft=[0.33706190383174456, -1.1063142069948853, -0.03197232823418927, -2.5781467687428163, 1.7878766081392818, -0.07068082254595552]
                TopRight=[-0.20993528866396272, -1.1394550794514793, -0.0381433775605228, 2.0800957274663707, -2.345124674082792,0.0688865874202783]
                BottomRight=[-0.2336725146368419, -0.7698087702804359, -0.04358179327271158, -1.8586905059976577, 2.516313225871966,-0.037392964043835776]

            else:
                # 270
                BottomLeft = []
                BottomRight = []
                TopLeft = []
                TopRight = []


        print "AUTOCALIBRATING",BottomLeft,TopLeft,TopRight,BottomRight
        xMax, xZero, yZero, yMax = self.setMax_Min(BottomLeft, BottomRight, TopLeft, TopRight)
        self.buildZCartisianPlane3Pts([BottomLeft[0], BottomLeft[1], BottomLeft[2]],
                                      [TopLeft[0], TopLeft[1], TopLeft[2]],
                                      [TopRight[0], TopRight[1], TopRight[2]],
                                      [BottomRight[0], BottomRight[1], BottomRight[2]])

        if abs(xMax - xZero) < abs(yMax - yZero):
            # x value is drawback,need to invert axis
            print 'case1'
            x = xMax - ((xMax - xZero) * 1.5)
            y = yZero + ((yMax - yZero) * 0.5)
            z = zDraw + 0.4
            # invert axis
            inv = [xZero, xMax, yZero, yMax]
            xMax = inv[3]
            yMax = inv[1]
            xZero = inv[2]
            yZero = inv[0]
        else:
            print 'case2'
            x = xZero + ((xMax - xZero) * 0.5)
            y = yMax - ((yMax - yZero) * 1.5)
            z = zDraw + 0.4
        initHoverPos = [x, y, z, 2.213345336120183,
                        -2.212550352198813, 0.01]
        print 'Please Step Away, Moving to Init Hover Position'
        # print initHoverPos,xMax, xZero, yMax, yZero
        rob.movel(initHoverPos, acc=a, vel=v)
        # print xMax,xZero,yMax,yZero,x,y,z
        # time.sleep(2)
        md = self.midpoint([xZero, yZero], [xMax, yMax])

    def midpoint(self,p1, p2):
        return [float((p1[0] + p2[0]) / 2), float((p1[1] + p2[1]) / 2)]

    def DetermineZ(self,x, y):
        return -((zPlaneParameters[0] * x) + (zPlaneParameters[1] * y) - zPlaneParameters[3]) / zPlaneParameters[2]

    def convertToTDspaceList(self,input, sz):
        Imheight =sz[0]
        Imwidth = sz[1]
        def checkRange(val,Max,Min,typ):
            if (val<=Max and val>=Min) or (val<=Min and val>=Max):
                return True
            print val,' was out of range between ',Min,' ',Max,typ
            return False

        '''if abs(md[0]) > abs(md[1]):
            if md[0] > 0:
                # 90
                print 'Recognized Region 1'
                #np.rot90(gray, 3)

                lclXMax = xMax
                lclXZero = xZero
                lclYZero = yZero
                lclYMax = yMax
            else:
                # 270
                print 'Recognized Region 3'
                #gray = np.rot90(gray, 1)
                # Rotated to 0 or 180

                lclXMax = xMax
                lclXZero = xZero
                lclYZero = yZero
                lclYMax = yMax
        else:
            if md[1] > 0:
                # 0
                print 'Recognized Region 0'
                lclXMax = xMax
                lclXZero = xZero
                lclYZero = yZero
                lclYMax = yMax

            else:
                # 180
                print 'Recognized Region 2'
                '''
        if Imwidth > Imheight:
            print 'Recognized width is greater than height'
            lclXMax = xZero
            lclXZero = xMax
            newheight = float(Imheight) / float(Imwidth) * (abs(float(lclXMax) - lclXZero))
            print newheight,(abs(float(lclXMax) - lclXZero))
            diff = [md[1] + float(newheight / 2), md[1] - float(newheight / 2)]
            lclYZero = min(diff)
            lclYMax = max(diff)
        else:
            print 'Recognized height is greater than width'
            lclYZero = yZero
            lclYMax = yMax
            newwidth = Imwidth/Imheight*(abs(lclYMax-lclYZero))
            print Imheight, newwidth
            diff =[md[0]+float(newwidth/2),md[0]-float(newwidth/2)]
            lclXMax = max(diff)
            lclXZero = min(diff)
            # gray = np.rot90(gray,2)'''



        lclImRatio=float(float(Imheight) / float(Imwidth))
        print 'Image Details:h.w = ',lclImRatio,Imheight,Imwidth,'----',float(lclYMax - lclYZero)/float(lclXMax - lclXZero)
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
        print lclXMax,lclXZero,lclYMax,lclYZero,sz[0]
        #print 'xMax_lcl_real', lclXMax, xMax
        #print 'yMax_lcl_real', lclYMax, yMax
        #print 'xZro_lcl_real', lclXZero, xZero
        #print 'yZro_lcl_real', lclYZero, yZero
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
            ptlst.append([x, y, self.DetermineZ(x, y), endPntPose[3], endPntPose[4], endPntPose[5]])
            print x,y
            if not checkRange(x,lclXZero,lclXMax,' for X') or not checkRange(y,lclYZero,lclYMax,' for Y'):
                raise ValueError('Range Error')
        return ptlst

    def DrawContour(self,pts):

        rob.movel([pts[0][0], pts[0][1], zHover, endPntPose[3], endPntPose[4], endPntPose[5]], acc=a, vel=v,
                  wait=True)
        rob.movels(pts, wait=True, acc=a, vel=v)
        rob.movel([pts[len(pts) - 1][0], pts[len(pts) - 1][1], zHover, endPntPose[3], endPntPose[4], endPntPose[5]],
                  acc=a, vel=v, wait=True)
        return
    #endregion


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