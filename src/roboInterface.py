#!/usr/bin/env python
import rospy
import SocialRoutineAddon
import logging
import cv2
import DN_LIB
from std_msgs.msg import String

robotParamters=None
def AnaylseInterupt(data):
    print data.data

def ExecuteCommand(data):
    Command =  data.data
    #parseCommand
    if Command == 'cal':
        robotParamters.Calibrate()
    elif Command == 'o':
        robotParamters.printAniPose()
    elif Command == 'BeginSocialRoutine':
        #robotParamters.SocialRoutineLoop()
    elif Command[0] == 'i':
        robotParamters.RunDrawing(cv2.imread(Command[3:], 0))
    elif Command[0]=='A':
        robotParamters.ExecuteAnimationSingular(cv2.imread(Command[2:], 0))
    else:
        print 'Invalid Command Sent'
    return



def initRobot():
    global robotParamters
    robotParamters = SocialRoutineAddon.DrawingRobotInstance()
    robotParamters.InitializeVariablesROS()
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
