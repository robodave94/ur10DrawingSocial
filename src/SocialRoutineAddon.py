import DN_LIB
import random
class DrawingRobotInstance(DN_LIB.DrawingRobotStructure):

    def RunningSocialRoutineV1(self):
        import cv2
        def ExtractDrawing():
            import glob, cv2
            listImgFiles = []
            for file in glob.glob(os.path.join(rospy.get_param('ImagesPath'), '*_1.png')):
                listImgFiles.append(file[:-6])
            index = random.randint(0, len(listImgFiles) - 1)
            self.Imgs = [cv2.imread(str(listImgFiles[index]) + '_1.png'),
                         cv2.imread(str(listImgFiles[index]) + '_2.png')]
            return

        def SocialAction(activity, sInd=0):
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
                self.ExecuteAnimation(ac)
            return

        def RunContinousSocialAction(Action):
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
            ExtractDrawing()
            print 'Got Drawing'
            self.LoopActive = True
            rob.movel(initHoverPos, wait=True, acc=a, vel=v)
            RunContinousSocialAction('idle')
            print bcolors.WARNING + 'Completed idle, Running greeting' + bcolors.ENDC
            self.LoopActive = True
            SocialAction('Greeting')
            print bcolors.WARNING + 'Completed greeting, Running First Drawing' + bcolors.ENDC
            self.LoopActive = True
            # run first set of drawing Points
            SocialAction('ExecuteDrawing')
            print bcolors.WARNING + 'Completed First Drawing, Running Contemplate animation' + bcolors.ENDC
            self.LoopActive = True
            SocialAction('ContemplateAnimation')
            print bcolors.WARNING + 'Completed comptempation, Running Second Drawing' + bcolors.ENDC
            self.LoopActive = True
            SocialAction('ExecuteDrawing', sInd=1)
            print bcolors.WARNING + 'Now encouraging user to draw' + bcolors.ENDC
            self.LoopActive = True
            RunContinousSocialAction('EncourageDrawing')
            print bcolors.WARNING + 'Now observing user draw' + bcolors.ENDC
            self.LoopActive = True
            RunContinousSocialAction('ObserveUser')
            # sigining
            print bcolors.WARNING + 'User has finished drawing now signing' + bcolors.ENDC
            self.LoopActive = True
            self.RunDrawing(cv2.imread(os.path.join('robot_img_v2/', 'robosign.png')))
            print bcolors.WARNING + 'Now encourage user to draw' + bcolors.ENDC
            self.LoopActive = True
            RunContinousSocialAction('EncourageSigining')
            print bcolors.WARNING + 'Observing user signing' + bcolors.ENDC
            self.LoopActive = True
            RunContinousSocialAction('ObserveUserSigning')
            print bcolors.WARNING + 'Waving goodbye' + bcolors.ENDC
            self.LoopActive = True
            RunContinousSocialAction('GoodBye')
            rtxt = raw_input("Enter q to quit of enter to repeat : ")
            if rtxt == 'q':
                break


        return