#!/usr/bin/env python
import rospy
import SocialRoutineAddon
import logging
import cv2
import numpy
import DN_LIB
from std_msgs.msg import String

robotParamters=None
def AnaylseInterupt(data):
    robotParamters.DetectedInteruptSig(data.data)
    return

def ExecuteCommand(data):
    Command =  data.data
    print data
    #parseCommand
    if Command == 'cal':
        robotParamters.Calibrate(cmdCal=True)
    elif Command == 'o':
        robotParamters.printAniPose()
    elif robotParamters.RunningSocialAction==True and Command[0]=='q':
        robotParamters.CancelSocialRoutine()
    elif Command == 'BeginSocialRoutine' or (robotParamters.RunningSocialAction==True and Command[0]!='q'):
        robotParamters.CalledSocialAction()
    elif Command[0] == 'i':
        print Command[3:]
        robotParamters.RunDrawing(cv2.imread(Command[3:], 0))
        #robotParamters.RunDrawing(cv2.imread('/home/naodev/Documents/default_ROSws/src/ur10DrawingSocial/robot_img_v2/grid_1.png', 0))
    elif Command[0]=='A':
        robotParamters.ExecuteAnimationSingular(Command[2:])
    elif Command[0]=='r':
        robotParamters.ReturnToInit()
    elif Command=='S':
        robotParamters.stopRobotInMotion()
    elif Command=='V':
        robotParamters.printMovementVariables()
    elif Command[:6]=='SetPar':
        par = Command.split(',')
        robotParamters.setMovementVariables(float(par[1]),float(par[2]))
    elif Command=='CloseGrip':
        robotParamters.CloseGripper()
    elif Command == 'OpenGrip':
        robotParamters.OpenGripper()
    elif Command == 'ReAn':
        robotParamters.ResetAnimation()
    else:
        print 'Invalid Command Sent'
    return



def initRobot():
    global robotParamters
    robotParamters = SocialRoutineAddon.DrawingRobotInstance()
    robotParamters.InitSocialRoutineSettings()
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
