#!/usr/bin/env python
import rospy
import SocialRoutineAddon
import logging
import DN_LIB
from std_msgs.msg import String

robotParamters=None
def AnaylseInterupt(data):
    print data.data

def ExecuteCommand(data):
    Command =  data.data
    #parseCommand


def initRobot():
    global robotParamters
    robotParamters = SocialRoutineAddon.DrawingRobotInstance()
    robotParamters.InitializeVariablesROS()
    print robotParamters.rob.host
    robotParamters.Calibrate()

def RobotBegin():
    rospy.init_node('ur10ArtInterface', anonymous=True)
    rospy.Subscriber("visionCollisionDetection", String, AnaylseInterupt)
    rospy.Subscriber("socialCmd", String, ExecuteCommand)
    rospy.spin()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    initRobot()
    RobotBegin()
