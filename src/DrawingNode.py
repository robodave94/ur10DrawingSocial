import urx
from urx import ursecmon
import logging
import cv2
import DN_LIB as drawingLib
import sys
from Tkinter import *

def ExecuteCMDLine(ip="10.0.0.157",isTesting=False,autoCal=False):
    #initializes programs global variables
    robotParameters = drawingLib.DrawingRobotInstance()
    robotParameters.setGlobVarInit(ip)
    try:
        #setup robot
        #inputpt=[[25,30],[50,60]]
        print 'ExecuteCalibration'
        if not autoCal:
            robotParameters.Calibrate()
        else:
            robotParameters.AutoCalibrate()
    except Exception as e:

        print 'An error occured ', e
        robotParameters.ShutdownRoutine()
    except KeyboardInterrupt:
        robotParameters.ShutdownRoutine()


    while(True):
        try:
            intxt = raw_input("Enter Command : ")
            #quit
            if intxt[0] =='S':
                robotParameters.RunningSocialRoutineV1()
            if intxt[0] == 'q':
                robotParameters.ShutdownRoutine()
            #reset position
            elif intxt[0] == 'r':
                robotParameters.resetPos()
            elif intxt[0] == 'p':
                robotParameters.getAllVariables()
            #stop
            elif intxt[0] == 's':
                robotParameters.rob.stop()
            elif intxt[0] == 't':
                print 'TODO: read a textfile'
            #variable
            elif intxt[0] == 'v':
                arrayseries = str(intxt[1:])
                arrayseries = arrayseries.split(',')
                robotParameters.setVar(float(arrayseries[0]), float(arrayseries[1]), float(arrayseries[2]))
            #calibrate
            elif intxt[0] == 'c' and not isTesting:
                robotParameters.Calibrate()
                #image location im:blabla.png
            elif intxt[0] == 'i':
                im = cv2.imread(intxt[3:], 0)
                #TODO: This needs to be rewritten to convert contours to smaller contours and escapeables
                robotParameters.RunDrawing(im,isTesting=isTesting)
            elif intxt[0] == 'o':
                #get robot positioning
                robotParameters.printAniPose()
                #Keep everything except convert x and y to discrepancy variables, use md
                #robotParameters.md
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

    return

def ExecuteGUI(ip="10.0.0.157"):
    robotParameters = drawingLib.DrawingRobotInstance()
    robotParameters.setGlobVarInit(ip)
    robotParameters.InitGUI()
    '''rob = urx.Robot(ip)
    secmon = ursecmon.SecondaryMonitor(rob.host)
    try:
        # setup robot
        # inputpt=[[25,30],[50,60]]
        print 'Robot Starting and moving to home initialization'
        rob.set_tcp((0, 0, 0.1, 0, 0, 0))
        rob.set_payload(2, (0, 0, 0.1))
        print 'ExecuteCalibration'
        robotParameters.Calibrate(rob)
    except Exception as e:

        print 'An error occured ', e
        rob.close()
        secmon.close()
        exit()
'''
    return

def main():
    if sys.argv.__contains__('-A'):
        AutoCalibrate=True
    else:
        AutoCalibrate=False

    if sys.argv.__contains__('-T'):
        testing=True
    else:
        testing=False
    #evaulates how to start the program
    if sys.argv.__contains__('-G'):
        print 'Command line requesting GUI detected'
        print 'Initiating GUI based interface'
        if sys.argv.__contains__('-I'):
            IPadd = raw_input("Please enter the IP address")
            ExecuteGUI(ip=IPadd)
        else:
            ExecuteGUI()

    else:
        print 'No request for GUI passed.'
        print 'Initiating default command line interface'
        if sys.argv.__contains__('-I'):
            IPadd = raw_input("Please enter the IP address")
            ExecuteCMDLine(ip=IPadd,isTesting=testing,autoCal=AutoCalibrate)
        else:
            ExecuteCMDLine(isTesting=testing,autoCal=AutoCalibrate)


    return


logging.basicConfig(level=logging.INFO)
main()