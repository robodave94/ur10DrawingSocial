import urx
from urx import ursecmon
import time
import SocialRoutineAddon
import numpy as np
import rospy
from std_msgs.msg import String


class RobotResearchObject(object):
    # endregion
    def InitBaseVariables(self):
        self.pub = rospy.Publisher('SocialReturnValues', String, queue_size=10)
        self.ImageIndex = 0
        self.ExtraContours = []
        self.StateOfWait = False
        self.StepsTaken = [
            'Idle',
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
        self.RunningSocialAction = False
        self.IdleCon = False
        self.withdrawPose = rospy.get_param('WithdrawPose')
        self.NodPose = rospy.get_param('NodDifferentials')
        self.initHoverPos = [0, 0, 0, 0, 0, 0]
        self.md = [0, 0]
        self.zDraw = 0
        self.zHover = 0
        self.xZero = 0
        self.yZero = 0
        self.xMax = 0
        self.yMax = 0
        self.a = rospy.get_param('speedParameters')
        self.v = rospy.get_param('speedParameters')
        self.rob = urx.Robot(rospy.get_param('roboIP'))
        self.leftwithDraw = rospy.get_param('leftRetreat')
        self.rightwithDraw = rospy.get_param('RightRetreat')
        self.Interruption = False
        self.StopCommand = False
        self.InteruptedPosition = self.rob.getl()
        self.secmon = ursecmon.SecondaryMonitor(self.rob.host)
        return

    def printRobotPose(self):
        print "Robot Joints = ", self.rob.getj()
        print "Robot Endpoint = ", self.rob.getl()
        return

    def DetectedInteruptSig(self, stringInput):
        strparam = stringInput.split(',')
        if strparam[0] == 'Collision':
            self.Interruption = True
            self.InteruptVector = np.array([float(strparam[1][1:]), float(strparam[2]), float(strparam[3][:-1])])
            self.InteruptedPosition = self.rob.getl()
            print self.InteruptVector
            if self.rob.is_program_running() == False:
                self.RunRetreat()
        return

    def UserDrawsInteruptSig(self, stringInput):
        strparam = stringInput.split('|')
        width = 0;
        height = 0;
        if strparam[0] == 'w':
            width = int(strparam[1])
        if strparam[2] == 'h':
            height = int(strparam[3])
        lns = strparam[4].split('.')
        lstcont = []
        for l in lns:
            pnts = l.split('*')
            cont = []
            for p in pnts:
                p = p.split(',')
                val_1 = int(p[0])
                val_2 = int(p[1])
                point = np.array([val_1, val_2])
                print point
                cont.append(point)
            lstcont.append(cont)
        print str(width) + " *** " + str(height)
        self.RunUserDrawing(lstcont, width, height)
        return

    def setFreeDriveFalse(self):
        self.rob.set_freedrive(False)
        return

    def setFreeDriveTrue(self):
        self.rob.set_freedrive(True)
        return

    def DelayWhileExecuting(self):
        time.sleep(0.25)
        while self.rob.is_program_running() and self.Interruption == False and self.StopCommand == False:
            time.sleep(0.01)
        if self.Interruption:
            self.InteruptedPosition = self.rob.getl()
            self.rob.stopl(acc=0.8)
            self.RunRetreat()
        # elif self.StopCommand==True:

        return

    def RunRetreat(self, drawing=False):
        print self.xZero, self.xMax, self.InteruptedPosition[0]
        if max(self.xZero, self.xMax) > self.InteruptedPosition[0] and min(self.xZero, self.xMax) < \
                self.InteruptedPosition[0]:
            self.ExecuteSingleMotionWait(self.initHoverPos)
        elif max(self.xZero, self.xMax) < self.InteruptedPosition[0]:
            #
            self.ExecuteSingleMotionWait(self.translateToDifferential(self.leftwithDraw))
        elif min(self.xZero, self.xMax) > self.InteruptedPosition[0]:
            self.ExecuteSingleMotionWait(self.translateToDifferential(self.rightwithDraw))
        self.Interruption = False
        return

    def ExecuteMultiMotionWait(self, pts):
        self.rob.movels(pts, acc=self.a, vel=self.v, wait=True)
        return

    def ExecuteMultiMotionWithInterrupt(self, pts):

        self.rob.movels(pts, acc=self.a, vel=self.v, wait=False)
        self.DelayWhileExecuting()
        return

    def ExecuteSingleMotionWithInterrupt(self, pt):
        print pt
        self.rob.movel(pt, acc=self.a, vel=self.v, wait=False)
        self.DelayWhileExecuting()
        return

    def ExecuteSingleMotionWait(self, pt):
        self.rob.movel(pt, acc=self.a, vel=self.v, wait=True)
        return

    def ShutdownRoutine(self):
        self.rob.close()
        self.secmon.close()
        exit()
        return

    def OpenGripper(self):
        self.rob.move_RG2gripper(110)
        return

    def CloseGripper(self):
        self.rob.move_RG2gripper(0)
        return

    def printMovementVariables(self):
        print 'Acceleration=', self.a
        print 'Velocity=', self.v
        return

    def setMovementVariables(self, accel=0.3, veloc=0.3):
        self.a = accel
        self.v = veloc
        print 'updated acceleration and velocity'
        return

    def translateToDifferential(self, pt):
        newpt = [pt[0], pt[1], pt[2], pt[3], pt[4], pt[5]]
        if self.initHoverPos[0] > 1:
            if self.initHoverPos[1] < 1:
                # 90
                print 'Animating To Section 1'
                newpt[1] = self.md[0] + (pt[0])
                newpt[0] = self.md[1] + (pt[1])
                newpt[2] = self.zDraw + abs(pt[2])
            else:
                # 0
                print 'Animating To Section 0'
                newpt[0] = self.md[0] + (pt[0])
                newpt[1] = self.md[1] + (pt[1])
                newpt[2] = self.zDraw + abs(pt[2])
        else:
            if self.initHoverPos[1] < 1:
                # 180
                print 'Animating To Section 2'
                newpt[0] = self.md[0] + (pt[0] * -1)
                newpt[1] = self.md[1] + (pt[1] * -1)
                newpt[2] = self.zDraw + abs(pt[2])
            else:
                # 270
                print 'Animating To Section 3'
                newpt[1] = self.md[0] + (pt[0] * -1)
                newpt[0] = self.md[1] + (pt[1] * -1)
                newpt[2] = self.zDraw + abs(pt[2])
        print 'Data from CSV: ', pt
        print 'The MidPoint is ', self.md, ' at height ', self.zDraw
        print 'New Point: ', newpt
        return newpt
