#!/usr/bin/env python
import rospy
import threading
import SocialRoutineAddon
import logging
import cv2
import time
import numpy
import DN_LIB
from std_msgs.msg import String

robotParamters=None
def AnaylseInterupt(data):
    robotParamters.DetectedInteruptSig(data.data)
    return



def ExecuteCommand(data):
    Command = data.data
    print 'Registered Command'
    #if social routine is not running
    if Command != '':
        if Command == 'cal':
            robotParamters.Calibrate(cmdCal=True)
        elif Command == 'o':
            robotParamters.printAniPose()
        elif robotParamters.RunningSocialAction==True and Command[0]=='q':
            robotParamters.CancelSocialRoutine()
        elif Command == 'BSR':
            robotParamters.InitSocRoutine()
        elif Command[0] == 'i':
            robotParamters.RunDrawing(cv2.imread(Command[3:], 0))
            #robotParamters.RunDrawing(cv2.imread('/home/naodev/Documents/default_ROSws/src/ur10DrawingSocial/robot_img_v2/grid_1.png', 0))
        elif Command[0]=='A':
            robotParamters.ExecuteAnimationSingular(Command[2:])
        elif Command[0]=='r':
            robotParamters.ReturnToInit()
        elif Command=='V':
            robotParamters.PrintAllVar()
        elif Command[:6]=='SetPar':
            par = Command.split(',')
            robotParamters.setMovementVariables(float(par[1]),float(par[2]))
        elif Command=='CloseGrip':
            robotParamters.CloseGripper()
        elif Command == 'OpenGrip':
            robotParamters.OpenGripper()
        elif Command == 'ReAn':
            robotParamters.ResetAnimation()
        elif Command == '1':
            #Point at cup
            robotParamters.SingleAction('PointAtCup')
        elif Command == '2':
            #Point at paper
            robotParamters.SingleAction('PointAtPaper')
        elif Command == '3':
            #pointAtClips
            robotParamters.SingleAction('PointAtClips')
        elif Command == '4':
            #Point at signature line
            robotParamters.SingleAction('PointAtSigLine')
        elif Command == '5':
            #Point at sign art
            robotParamters.SignArt()
        elif Command == '6':
            #Say goodbye
            robotParamters.SingleAction('Goodbye')
        elif Command == 'Obs':
            # continouslyDraw
            robotParamters.ContinouslyWaitState('Observe')
        elif Command == 'Nod':
            # continouslyNod
            robotParamters.ContinouslyWaitState('NodAtUser')
        elif Command == 'Pse':
            # Move to withdraw and wait
            robotParamters.ContinouslyWaitState('WithdrawPose')
        else:
            print 'Invalid Command Sent'
    else:
        print 'No Command Sent'
    return

#this subscriber will overwrite the social commands
def OverwriteCommand(data):
    if data.data=='FinishIdle':
        robotParamters.IdleCon = False
        time.sleep(0.2)
    #elif data.data=='Interupt':
    #    robotParamters.Interruption=True
    elif data.data=='Q':
        robotParamters.CancelSocialRoutine()

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
    rospy.Subscriber("OverwrittingSubscrier",String, OverwriteCommand)
    rospy.spin()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    initRobot()
    RobotBegin()
