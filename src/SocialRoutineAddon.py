import DN_LIB
import rospy
import ContourExtraction
import os
import time
import random
from std_msgs.msg import String
class DrawingRobotInstance(DN_LIB.DrawingRobotStructure):

    def InitSocialRoutineSettings(self):
        #first node pose higher one
        self.InitializeVariablesROS()
        self.WaitingAction = 'WithdrawPose'
        self.ep_valP=[0,0]
        self.dist_threshP=[0,0]
        return

    def CancelSocialRoutine(self):
        self.RunningSocialAction = False
        self.IdleCon=False
        self.pub.publish("Cancelling Social Routine")
        self.ReturnToInit()
        return
 
    def InitSocRoutine(self):
        self.RunningSocialAction=True
        self.pub.publish('Social Routine Activated')
        self.RunArtSequence()
        return

    def SocialAction(self, activity, sInd=0):
        if activity == 'ExecuteDrawing':
            print self.Imgs[sInd]
            self.RunDrawing(self.Imgs[sInd],inputVals=sInd)
        elif activity == 'Greet':
            # execute a single greeting animation
            ac = self.FindAnimations('Greet')
            self.ExecuteAnimationSingular(ac)
        elif activity == 'ContemplateAnimation':
            # execute a single greeting animation
            ac = self.FindAnimations('Contemplate')
            self.ExecuteAnimationSingular(ac)
        return


    def ContinouslyWaitState(self,action):
        self.IdleCon=True
        self.RunningSocialAction = True
        self.pub.publish('RunningWaitState: '+action)
        if action=='Observe':
            self.WaitingAction = 'Observe'
            while self.IdleCon == True:
                # running idle animations
                # find AnimationNAMEwithidletage
                ac = self.FindAnimations('Observe')
                self.ExecuteAnimationSingular(ac)
        elif action=='NodAtUser':
            self.WaitingAction = 'NodAtUser'
            while self.IdleCon == True:
                # running idle animations
                # find AnimationNAMEwithidletage
                time.sleep(random.randint(2,5))
                self.ExecuteSingleMotionWithInterrupt(self.NodPose[0])
                self.ExecuteSingleMotionWithInterrupt(self.NodPose[1])
                self.ExecuteSingleMotionWithInterrupt(self.NodPose[0])
        elif action == 'WithdrawPose':
            self.WaitingAction = 'WithdrawPose'
            self.ExecuteSingleMotionWithInterrupt(self.withdrawPose)
            while self.IdleCon == True:
                time.sleep(0.01)
        return

    def ChooseAniSet(self,code):
        self.ResetAnimation()
        names=['_Greet',
               '_PointAtCup',
               '_PointAtPaper',
               '_Sign',
               '_PointAtLine',
               '_PointAtClips',
               '_Goodbye']
        if code=='A':
            codesToRem=['B','C']
        elif code=='B':
            codesToRem = ['A', 'C']
        elif code=='C':
            codesToRem = ['A', 'B']
        else:
            return

        for codeitem in codesToRem:
            for nm in names:
                print 'Finding ',str(codeitem)+str(nm)
                ac = [i for i in self.Animations if i[0] == str(codeitem)+str(nm)]
                self.Animations.remove(ac[0])
                print 'Removed animation ',ac
        return


    '''def DrawSig(self):
        #self.pub.publish('RunningSingleAction: Signing')
        imsz = [420,594]
        print [imsz[0], imsz[1]]
        sigpts=[[[413,400],[567,400]],
                [[479,370],[510,370]],
                [[492,350],[492,394]],
                [[516,345],[516,396],[545,399],[534,345]],
                [[550,394],[550,352],[563,373],[550,380],[567,387]],
                [[550, 333], [550, 367], [565, 365], [565, 333], [550, 333]],
                [[565,332],[565,369]],
                [[575,333],[575,367],[578,367],[581,370],[583,371],[586,374],[589,377],[592,380],[590,333],[575,333]]]

        for y in sigpts:
            self.ExtraContours.append(y)
            if len(y)>0:
                pts = self.convertToTDspaceList(y, [imsz[0], imsz[1]])
                if self.RunningSocialAction==False:
                    return
                self.DrawContour(pts)
            self.ExtraContours.remove(y)


        #self.pub.publish('FinishedSingleAction: Signing') 
        return'''


    def DrawContour(self,pts,validate=False):
        if self.RunningSocialAction == False:
            return
        self.ExecuteSingleMotionWithInterrupt(
            [pts[0][0], pts[0][1], self.zHover, self.endPntPose[3], self.endPntPose[4], self.endPntPose[5]])
        if self.RunningSocialAction == False:
            return
        self.ExecuteMultiMotionWithInterrupt(pts)
        if self.RunningSocialAction == False:
            return
        self.ExecuteSingleMotionWithInterrupt(
            [pts[len(pts) - 1][0], pts[len(pts) - 1][1], self.zHover, self.endPntPose[3], self.endPntPose[4],
             self.endPntPose[5]])
        if self.RunningSocialAction == False:
            return
        return

    def RunDrawing(self,image,inputVals=0):
        lines = ContourExtraction.JamesContourAlg(image,self.ep_valP[inputVals],self.dist_threshP[inputVals])
        print lines
        #Crop the image space to match the input image size
        self.calculateCroppedSizing(image.shape[0], image.shape[1])
        line_num = 0
        for q in range(0,len(lines)):
            y = lines[q]
            line_num += 1
            print y
            self.ExtraContours.append(y)
            if len(y)>0:
                #pts = self.convertToTDspaceList(y, [image.shape[0], image.shape[1]])
                pts = []
                for eachPoint in y:
                    #print 'point is'
                    #print eachPoint
                    coords = self.PixelTranslation(eachPoint[0], eachPoint[1], image.shape[0], image.shape[1])
                    print pts
                    robotCoordFormat = [coords[0],coords[1],-coords[2],self.endPntPose[3],self.endPntPose[4],self.endPntPose[5]]
                    pts.append(robotCoordFormat)
                    #pts.append([coords[0],coords[1],coords[2],self.endPntPose[3],self.endPntPose[4],self.endPntPose[5]])
                if self.RunningSocialAction==False:
                    return
                self.DrawContour(pts)
            self.ExtraContours.remove(y)
        while len(self.ExtraContours)>0:
            self.DrawContour(self.ExtraContours[0])
            self.ExtraContours.remove(self.ExtraContours[0])
        print ('Completed Contour Construction', line_num)
        #self.rob.movel(self.initHoverPos, acc=self.a, vel=self.v, wait=True)
        return
 

    def validateFineDetails(self,points):
        import math
        #separation into substrings based on groups of three, hardcoded ur10 parameters
        indexlist = []
        print 'POINTS 1'
        print points
        print 'POINTS 2'
        for x in range(0, len(points[0])-4):
            p1 = points[0][x]
            p2 = points[0][x+2]
            print p1,p2
            print '---',math.sqrt(math.pow(p1[0]-p2[0],2)+math.pow(p1[1]-p2[1],2))
            #get difference between the point and the point two spots ahead
            '''if math.sqrt(math.pow(p1[0]-p2[0],2)+math.pow(p1[1]-p2[1],2))<=0.02:
                indexlist.append(x)
                indexlist.append(x+1)
                indexlist.append(x+2)'''
        print '------List of indices'
        print indexlist
        print '------End'
        self.ExecuteSingleMotionWithInterrupt(
                    [pts[0][0], pts[0][1], self.zHover, self.endPntPose[3], self.endPntPose[4], self.endPntPose[5]])
        self.ExecuteMultiMotionWithInterrupt(pts)
        self.ExecuteSingleMotionWithInterrupt([pts[len(pts) - 1][0], pts[len(pts) - 1][1], self.zHover, self.endPntPose[3], self.endPntPose[4],self.endPntPose[5]])
        return pts


    def RunUserDrawing(self, lines, width, height): 
        def DrawUsrContour(pts,validate=False):
            '''if(validate==True):
                pts = self.validateFineDetails(pts)
                print pts
            else:'''
            self.ExecuteSingleMotionWithInterrupt(
            [pts[0][0], pts[0][1], self.zHover, self.endPntPose[3], self.endPntPose[5], self.endPntPose[5]])
            self.ExecuteMultiMotionWithInterrupt(pts)
            self.ExecuteSingleMotionWithInterrupt([pts[len(pts) - 1][0], pts[len(pts) - 1][1], self.zHover, self.endPntPose[3], self.endPntPose[4],self.endPntPose[5]])
            return
        print lines
        line_num = 0 
        for q in range(0,len(lines)):
            y = lines[q]
            line_num += 1
            #print y
            self.ExtraContours.append(y)
            if len(y)>0:
                pts = self.convertToTDspaceList(y, [height, width])
                DrawUsrContour(pts,validate=True)
        #print 'ending'
            self.ExtraContours.remove(y)
        print ('Completed Contour Construction', line_num)
        #self.rob.movel(self.initHoverPos, acc=self.a, vel=self.v, wait=True)
        return


    def SingleAction(self,activity):
        self.IdleCon=True
        self.RunningSocialAction=True
        self.pub.publish('RunningSingleAction: '+activity)
        if activity=='Signing':
            self.SignArt()
        elif activity=='SDE':
            self.ExtractDrawing()
            self.SocialAction('ExecuteDrawing')
            self.SocialAction('ExecuteDrawing',sInd=1)
            self.SocialAction('ContemplateAnimation')
        else:
            ac = self.FindAnimations(activity)
            self.ExecuteAnimationSingular(ac)	    
        self.pub.publish('FinishedSingleAction: '+activity)
        self.ContinouslyWaitState(self.WaitingAction)
        return

    def SignArt(self):
        import cv2
        self.ep_valP = [0.0015, 0.0015]
        self.dist_threshP = [4, 4]
        self.pub.publish('RunningSingleAction: SignArt')
        print os.path.join(rospy.get_param('ImagesPath'), 'robosign.png')
        self.RunDrawing(cv2.imread(os.path.join(rospy.get_param('ImagesPath'), 'robosign.png')))
        print os.path.join(rospy.get_param('ImagesPath'), 'robosignLine.png')
        self.RunDrawing(cv2.imread(os.path.join(rospy.get_param('ImagesPath'), 'robosignLine.png')))
        self.pub.publish('FinishedSingleAction: SignArt')
        self.SingleAction('PointAtPaper')
        self.ContinouslyWaitState(self.WaitingAction)
        return


    def BeginSequenceofDraw(self):
        # Run Greet, Draw, Comptemplate and Draw
        pubmsgs=['Completed idle, Running greeting',
                 'Draw First Image Set',
                 'Completed First Draw, Now Running Contemplate Animation',
                 'Completed comptemplation, Running Second Drawing']
        socialCmds=['Greet',
                 'ExecuteDrawing',
                 'ContemplateAnimation',
                 'ExecuteDrawing']
        self.ExtractDrawing()
        for i in range(0,4):
            if self.RunningSocialAction == True:
                print self.RunningSocialAction
                #self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
                self.pub.publish(pubmsgs[i])
                if i==3:
                    self.SocialAction(socialCmds[i],sInd=1)
                    self.pub.publish('Completed Second Drawing')
                else:
                    self.SocialAction(socialCmds[i])
        return

    '''def SetIdleOFF(self):
        if self.IdleCon!=False:
            self.IdleCon=False
        return'''

    def RunArtSequence(self):
        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        self.IdleCon=True
        while self.IdleCon == True:
            print 'Idle',self.IdleCon
            #continously run idle animation
            ac = self.FindAnimations('Search')
            self.ExecuteAnimationSingular(ac)
            if self.IdleCon==False or self.RunningSocialAction==False:
                break
            #self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        self.IdleCon=True
        if self.RunningSocialAction==True:
            self.BeginSequenceofDraw()
        if self.RunningSocialAction == True:
            self.pub.publish('Action Draw Completed, control returned to user')
        else:
            self.pub.publish('Social routine cancelled, control returned to user')
        self.RunningSocialAction = False
        return
    
    def ExtractDrawing(self):
        import glob, cv2
        listImgFiles = []
        for file in glob.glob(os.path.join(rospy.get_param('ImagesPath'), '*_1.png')):
            listImgFiles.append(file[:-6])
        index = self.ImageIndex
        self.Imgs = [cv2.imread(str(listImgFiles[index]) + '_1.png'),
                     cv2.imread(str(listImgFiles[index]) + '_2.png')]
        self.ImageIndex +=1
        if self.ImageIndex==len(listImgFiles):
            self.ImageIndex = 0
        print 'chose drawing ',str(listImgFiles[index])
        #/home/nao/catkin_ws/src/ur10DrawingSocial/robot_img_v2
        imnm = str(listImgFiles[index])[len(rospy.get_param('ImagesPath')):]
        print imnm
        #SetPar
        '''if imnm=='sea':
            self.ep_valP=[0.0015,0.0015]
            self.dist_threshP=[10,14]
        elif imnm=='elephant':
            self.ep_valP=[0.0015,0.0015]
            self.dist_threshP=[2,10]
        el'''
        if imnm=='island':
            self.ep_valP=[0.0015,0.0015]
            self.dist_threshP=[10,14]
        elif imnm=='space':
            self.ep_valP=[0.0008,0.0015]
            self.dist_threshP=[9,4]
        elif imnm=='clouds':
            self.ep_valP=[0.001,0.001]
            self.dist_threshP=[4,4]
        elif imnm == 'sun':
            self.ep_valP = [0.0015,0.0015]
            self.dist_threshP = [4, 4]
        elif imnm == 'whale':
            self.ep_valP = [0.0015, 0.0015]
            self.dist_threshP = [10, 14]
        elif imnm=='elephant':
            self.ep_valP=[0.0008,0.0015]
            self.dist_threshP=[9,4]
        else:
            raise ValueError('invalid name of file:' + imnm)
        return

    '''

    def RunContinousSocialAction(self,Action):
        """ Method that runs forever """
        if Action == 'ObserveUserDrawing':
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
                print 'Found Animation ', ac
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

    def actionDeterminant(self,step):
        if step==0:
            self.ExtractDrawing()
            print 'Got Drawing'
            self.LoopActive = True
            self.ExecuteAnimationSingular(self.initHoverPos)
            self.RunContinousSocialAction('idle')
        elif step==1:
            print self.bcolors.WARNING + 'Completed idle, Running greeting' + self.bcolors.ENDC
            self.LoopActive = True
            self.SocialAction('Greeting')
            self.Step += 1
            print self.bcolors.WARNING + 'Completed greeting, Running First Drawing' +self.bcolors.ENDC
            # run first set of drawing Points
            self.SocialAction('ExecuteDrawing')
            self.Step += 1
            print self.bcolors.WARNING + 'Completed First Drawing, Running Contemplate animation' +self.bcolors.ENDC
            self.SocialAction('ContemplateAnimation')
            self.Step += 1
            print self.bcolors.WARNING + 'Completed comptempation, Running Second Drawing' +self.bcolors.ENDC
            self.SocialAction('ExecuteDrawing', sInd=1)
            self.Step += 1
            print self.bcolors.WARNING + 'Now encouraging user to draw' +self.bcolors.ENDC
            self.RunContinousSocialAction('EncourageDrawing')
            print self.bcolors.WARNING + 'Now observing user draw' +self.bcolors.ENDC
        elif step == 6:
            self.LoopActive = True
            self.RunContinousSocialAction('ObserveUser')
        elif step==7:
            # sigining
            print self.bcolors.WARNING + 'User has finished drawing now signing' +self.bcolors.ENDC
            self.LoopActive = True
            self.RunDrawing(cv2.imread(os.path.join('robot_img_v2/', 'robosign.png')))
            self.Step += 1
            print self.bcolors.WARNING + 'Now encourage user to draw' +self.bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('EncourageSigining')
        elif step==9:
            print self.bcolors.WARNING + 'Observing user signing' +self.bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('ObserveUserSigning')
        elif step == 10:
            print self.bcolors.WARNING + 'Waving goodbye' +self.bcolors.ENDC
            self.LoopActive = True
            self.RunContinousSocialAction('GoodBye')
            self.step=0
        return'''

