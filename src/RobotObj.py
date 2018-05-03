import urx
from urx import ursecmon
import time
import numpy as np
import rospy
class RobotResearchObject (object):
    #endregion
    def InitBaseVariables(self):
        self.a = rospy.get_param('speedParameters')
        self.v = rospy.get_param('speedParameters')
        self.rob = urx.Robot(rospy.get_param('roboIP'))
        self.Interruption = False
        self.InteruptedPosition = self.rob.getl()
        self.secmon = ursecmon.SecondaryMonitor(self.rob.host)
        return

    def printRobotPose(self):
        print "Robot Joints = ",self.rob.getj()
        print "Robot Endpoint = ", self.rob.getl()
        return

    def DetectedInteruptSig(self,stringInput):
        strparam = stringInput.split(',')
        if strparam[0] == 'Collision':
            self.Interruption = True
            self.InteruptVector = np.array([float(strparam[1][1:]),float(strparam[2]),float(strparam[3][:-1])])
            print self.InteruptVector
        return

    def setFreeDriveFalse(self):
        self.rob.set_freedrive(False)
        return

    def setFreeDriveTrue(self):
        self.rob.set_freedrive(True)
        return

    def DelayWhileExecuting(self):
        time.sleep(0.25)
        while self.rob.is_program_running() and not self.Interruption:
            time.sleep(0.01)
        if self.Interruption:
            self.InteruptedPosition = self.rob.getl()
            self.stopRobotInMotion()
        return

    def ExecuteMultiMotionWait(self,pts):
        self.rob.movels(pts,acc = self.a,vel=self.v,wait=True)
        return

    def ExecuteMultiMotionWithInterrupt(self,pts):
        self.rob.movels(pts,acc = self.a,vel=self.v,wait=False)
        self.DelayWhileExecuting()
        return

    def ExecuteSingleMotionWithInterrupt(self,pt):
        self.rob.movel(pt, acc=self.a, vel=self.v, wait=False)
        self.DelayWhileExecuting()
        return

    def ExecuteSingleMotionWait(self,pt):
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

    def stopRobotInMotion(self):
        self.rob.stopl(acc=self.a)
        self.Interruption=False
        return

    def printMovementVariables(self):
        print 'Acceleration=',self.a
        print 'Velocity=', self.v
        return

    def setMovementVariables(self, accel=0.3, veloc=0.3):
        self.a = accel
        self.v = veloc
        print 'updated acceleration and velocity'
        return