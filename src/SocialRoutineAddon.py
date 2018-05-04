import DN_LIB
import random
import rospy,os,cv2
from std_msgs.msg import String
class DrawingRobotInstance(DN_LIB.DrawingRobotStructure):

    def InitSocialRoutineSettings(self):
        self.pub = rospy.Publisher('SocialReturnValues', String, queue_size=10)
        self.Step=0
        self.StepsTaken=[
            'idle',
            'Greeting',
            'ExecuteDrawing',
            'ContemplateAnimation',
            'ExecuteDrawing',
            'EncourageDrawing',
            'ObserveUserDrawing',
            'SignDrawing',
            'EncourageSigining',
            'ObserveUserSigning',
            'GoodBye'
        ]
        self.RunningSocialAction=False
        self.InitializeVariablesROS()
        return

    def CancelSocialRoutine(self):
        self.RunningSocialAction = False
        self.pub.publish("Cancelling Social Routine")
        self.Step=0
        self.ExecuteSingleMotionWithInterrupt(self.initHoverPos)
        return

    def InitSocRoutine(self):
        self.RunningSocialAction=True
        self.pub.publish('Social Routine Activated')
        return


    
    def ExtractDrawing(self):
        import glob, cv2
        listImgFiles = []
        for file in glob.glob(os.path.join(rospy.get_param('ImagesPath'), '*_1.png')):
            listImgFiles.append(file[:-6])
        index = random.randint(0, len(listImgFiles) - 1)
        self.Imgs = [cv2.imread(str(listImgFiles[index]) + '_1.png'),
                     cv2.imread(str(listImgFiles[index]) + '_2.png')]
        return

    '''def SocialAction(self,activity, sInd=0):
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

