/**
 * @file /src/qnode.cpp
 *
 * @brief Ros communication central!
 *
 * @date February 2011
 **/

/*****************************************************************************
** Includes
*****************************************************************************/

#include <ros/ros.h>
#include <ros/network.h>
#include <string>
#include <std_msgs/String.h>
#include <sstream>
#include "../include/robo_draw/qnode.hpp"

 
namespace robo_draw {

 
QNode::QNode(int argc, char** argv ) :
	init_argc(argc),
	init_argv(argv)
	{}

QNode::~QNode() {
    if(ros::isStarted()) {
      ros::shutdown(); // explicitly needed since we use ros::start();
      ros::waitForShutdown();
    }
	wait();
}

bool QNode::init() {
	ros::init(init_argc,init_argv,"robo_draw");
	if ( ! ros::master::check() ) {
		return false;
	}
	ros::start(); // explicitly needed since our nodehandle is going out of scope.
	ros::NodeHandle n;
	// Add your ros communications here.
	chatter_publisher = n.advertise<std_msgs::String>("UserDraws", 1000);
	start();
	return true;
}
 /*
bool QNode::init(QList< QList<QPoint> > inputLst, double w, double h) { 
	ros::init(init_argc,init_argv,"robo_draw");
LineLst = inputLst;
width =w;
height =h;
	if ( ! ros::master::check() ) {
		return false;
	}
	ros::start(); // explicitly needed since our nodehandle is going out of scope.
	ros::NodeHandle n;
	// Add your ros communications here.
	chatter_publisher = n.advertise<std_msgs::String>("UserDraws", 1);
	start();

	//sendMsg(inputLst,  w,  h);
	return true;
}
 */

void QNode::run() {
	//ros::Rate loop_rate(1);
/*	 
	//while ( ros::ok() ) {

		std_msgs::String msg;
		std::stringstream ss;
		ss << " width = "<<width  << " height = "<<height << " ";
		for(int i =0; i<LineLst.size();i++)
		{
			ss << "[";
		   	for(int z =0; z<LineLst[i].size(); z++)
			{
			    ss << "["<< LineLst[i][z].x()<< ","<< LineLst[i][z].y()<<"]" ;
				if(z<LineLst[i].size()-1)
				{
					ss << ",";
				}
			}
			ss << "]";
			if(i<LineLst.size()-1)
			{
				ss << ",";
			}
		}
		msg.data = ss.str();
		chatter_publisher.publish(msg);
		//log(Info,std::string("I sent: ")+msg.data);
		ros::spinOnce(); 
	//}
	//std::cout << "Ros shutdown, proceeding to close the gui." << std::endl;
*/	
Q_EMIT rosShutdown(); // used to signal the gui for a shutdown (useful to roslaunch)
}

void QNode::sendMsg(QList< QList<QPoint> > inputLst, int w, int h)
{
	std_msgs::String msg;
		std::stringstream ss;
		ss << "w|"<<w  << "|h|"<<h << "|";
		for(int i =0; i<inputLst.size();i++)
		{
			//ss << "*";
		   	for(int z =0; z<inputLst[i].size(); z++)
			{
			    ss << inputLst[i][z].x()<< ","<< inputLst[i][z].y() ;
				if(z<inputLst[i].size()-1)
				{
					ss << "*";
				}
			}
			//ss << "*";
			if(i<inputLst.size()-1)
			{
				ss << ".";
			}
		}
		msg.data = ss.str();
		chatter_publisher.publish(msg);
		ros::spinOnce(); 
}
/*

void QNode::log( const LogLevel &level, const std::string &msg) {
	logging_model.insertRows(logging_model.rowCount(),1);
	std::stringstream logging_model_msg;
	switch ( level ) {
		case(Debug) : {
				ROS_DEBUG_STREAM(msg);
				logging_model_msg << "[DEBUG] [" << ros::Time::now() << "]: " << msg;
				break;
		}
		case(Info) : {
				ROS_INFO_STREAM(msg);
				logging_model_msg << "[INFO] [" << ros::Time::now() << "]: " << msg;
				break;
		}
		case(Warn) : {
				ROS_WARN_STREAM(msg);
				logging_model_msg << "[INFO] [" << ros::Time::now() << "]: " << msg;
				break;
		}
		case(Error) : {
				ROS_ERROR_STREAM(msg);
				logging_model_msg << "[ERROR] [" << ros::Time::now() << "]: " << msg;
				break;
		}
		case(Fatal) : {
				ROS_FATAL_STREAM(msg);
				logging_model_msg << "[FATAL] [" << ros::Time::now() << "]: " << msg;
				break;
		}
	}
	QVariant new_row(QString(logging_model_msg.str().c_str()));
	logging_model.setData(logging_model.index(logging_model.rowCount()-1),new_row);
	Q_EMIT loggingUpdated(); // used to readjust the scrollbar
}
 */
}  // namespace robo_draw
