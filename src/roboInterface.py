#!/usr/bin/env python
import rospy
import logging
import DN_LIB
from std_msgs.msg import String

robotParamters=None
def AnaylseInterupt(data):
    print data.data

def ExecuteCommand(data):
    intxt= data.data
    try:
        # quit
        if intxt[0] == 'S':
            robotParameters.RunningSocialRoutineV1()
        if intxt[0] == 'q':
            robotParameters.ShutdownRoutine()
        # reset position
        elif intxt[0] == 'r':
            robotParameters.resetPos()
        elif intxt[0] == 'p':
            robotParameters.getAllVariables()
        # stop
        elif intxt[0] == 's':
            robotParameters.rob.stop()
        elif intxt[0] == 't':
            print 'TODO: read a textfile'
        # variable
        elif intxt[0] == 'v':
            arrayseries = str(intxt[1:])
            arrayseries = arrayseries.split(',')
            robotParameters.setVar(float(arrayseries[0]), float(arrayseries[1]), float(arrayseries[2]))
        # calibrate
        elif intxt[0] == 'c' and not isTesting:
            robotParameters.Calibrate()
            # image location im:blabla.png
        elif intxt[0] == 'i':
            im = cv2.imread(intxt[3:], 0)
            # TODO: This needs to be rewritten to convert contours to smaller contours and escapeables
            robotParameters.RunDrawing(im, isTesting=isTesting)
        elif intxt[0] == 'o':
            # get robot positioning
            robotParameters.printAniPose()
            # Keep everything except convert x and y to discrepancy variables, use md
            # robotParameters.md
        elif intxt[0] == 'a':
            robotParameters.ExecuteAnimation(intxt[2:])
        elif intxt[0] == 'l':
            robotParameters.ResetAnimation()
            print 'Reimported Animation CSV'
        else:
            print 'print invalid command'
    except Exception as e:
        robotParameters.setFreeDriveFalse()
        print 'An error occured ', e
    except KeyboardInterrupt:
        robotParameters.ShutdownRoutine()

def initRobot(ip='10.0.0.157'):
    global robotParameters
    robotParameters = DN_LIB.DrawingRobotInstance()
    robotParameters.setGlobVarInit(ip)
    robotParameters.Calibrate()

def RobotBegin():
    rospy.init_node('ur10ArtInterface', anonymous=True)
    rospy.Subscriber("visionCollisionDetection", String, AnaylseInterupt)
    rospy.Subscriber("socialCmd", String, ExecuteCommand)
    rospy.spin()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    initRobot()
    RobotBegin()
