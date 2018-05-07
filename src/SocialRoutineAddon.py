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
        self.WaitingAction = 'NodAtUser'
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
            self.RunDrawing(self.Imgs[sInd])
        elif activity == 'Greeting':
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
                self.ExecuteSingleMotionWithInterrupt(self.translateToDifferential(self.NodPose[0]))
                self.ExecuteSingleMotionWithInterrupt(self.translateToDifferential(self.NodPose[1]))
                self.ExecuteSingleMotionWithInterrupt(self.translateToDifferential(self.NodPose[0]))
                time.sleep(random.randint(2,5))
        elif action == 'WithdrawPose':
            self.WaitingAction = 'WithdrawPose'
            self.ExecuteSingleMotionWithInterrupt(self.translateToDifferential(self.withdrawPose))
            while self.IdleCon == True:
                time.sleep(0.01)
        return



    def RunDrawing(self,image):
        def DrawContour(pts):
            if self.RunningSocialAction==False:
                return
            self.ExecuteSingleMotionWithInterrupt(
                [pts[0][0], pts[0][1], self.zHover, self.endPntPose[3], self.endPntPose[4], self.endPntPose[5]])
            if self.RunningSocialAction==False:
                return
            self.ExecuteMultiMotionWithInterrupt(pts)
            if self.RunningSocialAction==False:
                return
            self.ExecuteSingleMotionWithInterrupt(
                [pts[len(pts) - 1][0], pts[len(pts) - 1][1], self.zHover, self.endPntPose[3], self.endPntPose[4], self.endPntPose[5]])
            if self.RunningSocialAction==False:
                return
            return

        lines = ContourExtraction.ImageContoursCustomSet1(image)
        print lines
        for y in lines:
            pts = self.convertToTDspaceList(y, [image.shape[0], image.shape[1]])
            if self.RunningSocialAction==False:
                return
            DrawContour(pts)
        print 'Completed Contour Construction'
        self.rob.movel(self.initHoverPos, acc=self.a, vel=self.v, wait=True)
        return

    def SingleAction(self,activity):
        self.IdleCon=True
        self.RunningSocialAction=True
        self.pub.publish('RunningSingleAction: '+activity)
        self.ExecuteAnimationSingular(activity)
        self.pub.publish('FinishedSingleAction: '+activity)
        self.ContinouslyWaitState(self.WaitingAction)
        return

    def SignArt(self):
        import cv2
        self.pub.publish('RunningSingleAction: SignArt')
        print os.path.join(rospy.get_param('ImagesPath'), 'robosign.png')
        self.RunDrawing(cv2.imread(os.path.join(rospy.get_param('ImagesPath'), 'robosign.png')))
        self.pub.publish('FinishedSingleAction: SignArt')
        self.ContinouslyWaitState(self.WaitingAction)
        return


    def BeginSequenceofDraw(self):
        # Run Greet, Draw, Comptemplate and Draw
        pubmsgs=['Completed idle, Running greeting',
                 'Draw First Image Set',
                 'Completed First Draw, Now Running Contemplate Animation',
                 'Completed comptemplation, Running Second Drawing']
        socialCmds=['Greeting',
                 'ExecuteDrawing',
                 'ContemplateAnimation',
                 'ExecuteDrawing']
        self.ExtractDrawing()
        for i in range(0,4):
            if self.RunningSocialAction == True:
                print self.RunningSocialAction
                self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
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
            ac = self.FindAnimations('Idle')
            self.ExecuteAnimationSingular(ac)
            if self.IdleCon==False or self.RunningSocialAction==False:
                break
            self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
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
        index +=1
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

