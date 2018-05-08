#!/usr/bin/env python
import rospy
import time
from std_msgs.msg import String

'''
2 booleans, scenario goes as follows
|T|T|
Running the state wait command, need to able to interrupt and send to single motion and return,prints in blue
|T|F|
Running the Sequential social routine that does not wait for user, prints in green
|F|T|
Executing a single animation, i.e. point at item or sign
|F|F|
Standard Messages That accept the default commands, i.e. calibrate, variables single animates and drawings etc
'''
class Retcolors:
    def __init__(self):
        return
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
prntngMsg="Please enter your command: "
StateBool1 = False
StateBool2 = False
PrintingSocMsg=False
def SocialMessages(data):
    global StateBool1,StateBool2,PrintingSocMsg,prntngMsg
    PrintingSocMsg= True
    print '\n' +Retcolors.WARNING +data.data+ Retcolors.ENDC+'\n'
    #BSR run
    if data.data=='Social Routine Activated':
        StateBool1=True
        StateBool2=False
    #BSR finished
    elif data.data=='Action Draw Completed, control returned to user':
        StateBool2=True
        pubOver.publish('FinishIdle')
        pub.publish('Nod')
    elif data.data=='Social routine cancelled, control returned to user':
        StateBool1 = False
    #Running a single animation
    elif data.data[0:20]=='RunningSingleAction:':
        StateBool2=True
    elif data.data[0:20] == 'RunningSingleAction:':
        StateBool1 = False
        StateBool2 = True
    # else if data indicates finijshed single animation
    elif data.data[0:21] == 'FinishedSingleAction:':
        StateBool2=False
    elif data.data[0:17]=='RunningWaitState:':
        StateBool1 = True
        StateBool2 = True
    elif data.data=='Cancelling Social Routine':
        StateBool1 = False
        StateBool2 = False

    if StateBool1 == True and StateBool2 == True:
        # Running the state motion command, need to able to interrupt and send to single motion and return
        prntngMsg = Retcolors.OKBLUE + "Running the wait state, enter a command to proceed: " + Retcolors.ENDC

    elif StateBool1 == True and StateBool2 == False:
        # Running the Sequential social routine that does not wait for user, prints in green
        prntngMsg = Retcolors.OKGREEN + "Press Enter To Finish Idle Animation or Q to stop: " + Retcolors.ENDC

    elif StateBool1 == False and StateBool2 == True:
        prntngMsg=Retcolors.UNDERLINE + "Runing single animation, press enter to interupt or wait: " + Retcolors.ENDC

    elif StateBool1 == False and StateBool2 == False:
        prntngMsg = "Please enter your command: "

    print prntngMsg
    PrintingSocMsg = False
    return

pub=None
pubOver=None
def talker():
    global StateBool2,StateBool1,pub,pubOver
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('socialCmd', String, queue_size=10)
    pubOver = rospy.Publisher('OverwrittingSubscrier', String, queue_size=10)
    rospy.Subscriber("SocialReturnValues", String, SocialMessages)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        if PrintingSocMsg==False:
            rwpt = raw_input(prntngMsg)
            if StateBool1==True and StateBool2==True:
                #Running the state motion command, need to able to interrupt and send to single motion and return
                if rwpt == 'Obs' or rwpt == 'Nod' or rwpt == 'Pse' or rwpt == '1' or rwpt == '2' or rwpt == '3' \
                        or rwpt == '4'or rwpt == '5'or rwpt == '6' or rwpt == 'BSR':
                    pubOver.publish('FinishIdle')
                    time.sleep(0.1)
                    pub.publish(rwpt)
                elif rwpt=='q' or rwpt=='Q':
                    pubOver.publish('Q')
                    StateBool1 = False
                    StateBool2 = False
                time.sleep(0.2)
                rate.sleep()
            elif StateBool1==True and StateBool2==False:
                #Running the Sequential social routine that does not wait for user, prints in green)
                if rwpt != 'Q':
                    pubOver.publish('FinishIdle')
                else:
                    pubOver.publish('Q')
                    StateBool1 = False
                    StateBool2 = False
                time.sleep(0.2)
                rate.sleep()
            elif StateBool1==False and StateBool2==True:
                pubOver.publish('Interupt')
                time.sleep(0.1)
                pub.publish('Nod')
                time.sleep(0.2)
                rate.sleep()
            elif StateBool1==False and StateBool2==False:
                if rwpt == 'Obs' or rwpt == 'Nod' or rwpt == 'Pse':
                    StateBool1 = True
                    StateBool2 = True
                pub.publish(rwpt)
                time.sleep(0.2)
                rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
