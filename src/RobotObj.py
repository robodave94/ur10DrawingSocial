import urx
from urx import ursecmon
import time
import rospy
class RobotResearchObject (object):
    #endregion
    def _init_(self):
        self.a = rospy.get_param('speedParameters')
        self.v = rospy.get_param('speedParameters')
        self.rob = urx.Robot(rospy.get_param('roboIP'))
        self.interuptExec = False
        self.secmon = ursecmon.SecondaryMonitor(self.rob.host)
        return

    def printRobotPose(self):
        print "Robot Joints = ",self.rob.getj()
        print "Robot Endpoint = ", self.rob.getl()
        return

    def setFreeDriveFalse(self):
        self.rob.set_freedrive(False)
        return

    def setFreeDriveTrue(self):
        self.rob.set_freedrive(True)
        return

    def DelayWhileExecuting(self):
        time.sleep(0.25)
        while self.rob.is_program_running() and not self.interuptExec:
            rospy.loginfo("Moving")
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

    def stopRobotInMotion(self):
        self.rob.stopl()
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