#!/usr/bin/env python
import rospy
import time
from std_msgs.msg import String


class bcolors:
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

PrintingSocMsg = False
def SocialMessages(data):
    global PrintingSocMsg
    PrintingSocMsg= True
    print bcolors.WARNING  +data.data+ bcolors.ENDC
    PrintingSocMsg = False
    return

def talker():
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('socialCmd', String, queue_size=10)
    rospy.Subscriber("SocialReturnValues", String, SocialMessages)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        if not PrintingSocMsg:
            inptstr=raw_input("Please enter your command: ")
            pub.publish(inptstr)
            time.sleep(0.2)
            rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
