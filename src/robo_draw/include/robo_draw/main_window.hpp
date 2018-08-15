/**
 * @file /include/robo_draw/main_window.hpp
 *
 * @brief Qt based gui for robo_draw.
 *
 * @date November 2010
 **/
#ifndef robo_draw_MAIN_WINDOW_H
#define robo_draw_MAIN_WINDOW_H

#include <QtGui/QMainWindow>
#include "ui_main_window.h"
#include "qnode.hpp"
#include <QDialog>
#include <QtGui>
#include <QtCore>
#include <QGraphicsScene>
#include <QList>
#include <QGraphicsView>
#include <QMouseEvent>

#include <QLine>

namespace robo_draw {

/**
 * @brief Qt central, all operations relating to the view part here.
 */
class MainWindow : public QMainWindow {
Q_OBJECT

public:
	MainWindow(int argc, char** argv, QWidget *parent = 0);
	~MainWindow();
/*
	void ReadSettings(); // Load up qt program settings at startup
	void WriteSettings(); // Save qt program settings when closing
*/
    QList< QList<QPoint> > tempLst;
   QList< QList<QPoint> >  LineLst;
    //QList<QLine> DrawnLst;
    QPoint p1, p2;
    QList<QPoint> currentLine;
    QPen robotPen;
    QPen mousePen;
    bool isFirstPoint;
    float scaleX;
float limit;
    float scaleY;
	void closeEvent(QCloseEvent *event); // Overloaded function
float euclideanDist(QPoint p1, QPoint p2);
	//void showNoMasterMessage();

public Q_SLOTS:
    //void on_actionAbout_triggered();
    //void on_button_connect_clicked(bool check );
    //void on_checkbox_use_environment_stateChanged(int state);

    void mousePressEvent(QMouseEvent *e);
    void mouseMoveEvent(QMouseEvent *e);
    void mouseReleaseEvent(QMouseEvent *e);
    
    void on_button_clear_clicked();
    void on_button_undo_clicked();
    void on_button_redo_clicked();
    void on_button_draw_clicked();

  //  void updateLoggingView(); // no idea why this can't connect automatically

private:
	Ui::MainWindowDesign ui;
     QGraphicsScene *scene;
	QNode qnode;

protected:
    void renderDrawing();
};

}  // namespace robo_draw

#endif // robo_draw_MAIN_WINDOW_H
