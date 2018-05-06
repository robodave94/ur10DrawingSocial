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

StateBool1 = False
StateBool2 = False
def SocialMessages(data):
    global StateBool1,StateBool2
    PrintingSocMsg= True
    print Retcolors.WARNING  +data.data+ Retcolors.ENDC
    if data.data=='Social Routine Activated':
        waitingSignal=True
    elif data.data=='Action Draw Completed, control returned to user' or data.data=='Social routine cancelled, control returned to user':
        waitingSignal=False
    PrintingSocMsg = False
    return

def talker():
    global waitingSignal
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('socialCmd', String, queue_size=10)
    pubOver = rospy.Publisher('OverwrittingSubscrier', String, queue_size=10)
    rospy.Subscriber("SocialReturnValues", String, SocialMessages)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        #
        if StateBool1==True and StateBool2==True:
            #Running the state motion command, need to able to interrupt and send to single motion and return
            rwpt = raw_input(Retcolors.OKBLUE + "Running the wait state, enter a command to proceed: " + Retcolors.ENDC)
            if rwpt != 'Q':
                pubOver.publish('FinishIdle')
            else:
                pubOver.publish('Q')
                waitingSignal = False
            time.sleep(0.2)
            rate.sleep()
        elif StateBool1==True and StateBool2==False:
            #Running the Sequential social routine that does not wait for user, prints in green
            rwpt = raw_input(Retcolors.OKGREEN + "Press Enter To Finish Idle Animation or Q to stop: " + Retcolors.ENDC)
            if rwpt != 'Q':
                pubOver.publish('FinishIdle')
            else:
                pubOver.publish('Q')
                waitingSignal = False
            time.sleep(0.2)
            rate.sleep()
        elif StateBool1==False and StateBool2==True:

        elif StateBool1==False and StateBool2==False:
            inptstr = raw_input("Please enter your command: ")
            pub.publish(inptstr)
            time.sleep(0.2)
            rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
