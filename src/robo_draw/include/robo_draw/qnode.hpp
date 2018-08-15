/**
 * @file /include/robo_draw/qnode.hpp
 *
 * @brief Communications central!
 *
 * @date February 2011
 **/
/*****************************************************************************
** Ifdefs
*****************************************************************************/

#ifndef robo_draw_QNODE_HPP_
#define robo_draw_QNODE_HPP_

/*****************************************************************************
** Includes
*****************************************************************************/

#include <ros/ros.h>
#include <string>
#include <QThread>
#include <QStringListModel>


/*****************************************************************************
** Namespaces
*****************************************************************************/

namespace robo_draw {

/*****************************************************************************
** Class
*****************************************************************************/

class QNode : public QThread {
    Q_OBJECT
public:
	QNode(int argc, char** argv );
	virtual ~QNode();
	bool init();
    //bool init(QList< QList<QPoint> > inputLst, double w, double h);
    void run();
    void sendMsg(QList< QList<QPoint> > inputLst, double w, double h);
	QList< QList<QPoint> > LineLst;
	double width;
	double height;
	/*********************
	** Logging
	*********************
	enum LogLevel {
	         Debug,
	         Info,
	         Warn,
	         Error,
	         Fatal
	 };

	QStringListModel* loggingModel() { return &logging_model; }*/
	//void log( const LogLevel &level, const std::string &msg);

Q_SIGNALS:
	//void loggingUpdated();
    void rosShutdown();

private:
	int init_argc;
	char** init_argv;
	ros::Publisher chatter_publisher;
    QStringListModel logging_model;
};

}  // namespace robo_draw

#endif /* robo_draw_QNODE_HPP_ */
