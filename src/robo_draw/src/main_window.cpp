#include <QList>
#include <QtGui>
#include <QString>
#include <math.h> 
#include <QMessageBox>
#include <iostream>
#include "../include/robo_draw/main_window.hpp" 
 
namespace robo_draw {

using namespace Qt;
 
MainWindow::MainWindow(int argc, char** argv, QWidget *parent)
	: QMainWindow(parent)
	, qnode(argc,argv)
{
    ui.setupUi(this); 
    setWindowIcon(QIcon(":/images/icon.png"));  
	
    scene = new QGraphicsScene();
    this->scene->setSceneRect(0, 0, 600, 600);
    ui.graphicsView->setScene(scene);

    robotPen.setWidth(6);
    mousePen.setColor(Qt::red);
    mousePen.setWidth(10);

    isFirstPoint = true;

   connect(ui.clearBtn, SIGNAL(clicked()), this, SLOT(on_button_clear_clicked()));
   connect(ui.undoBtn, SIGNAL(clicked()), this, SLOT(on_button_undo_clicked()));
   connect(ui.redoBtn, SIGNAL(clicked()), this, SLOT(on_button_redo_clicked()));
   connect(ui.drawBtn, SIGNAL(clicked()), this, SLOT(on_button_draw_clicked()));

   connect(ui.straightLineRBtn,  SIGNAL(clicked()), this, SLOT(on_button_draw_clicked()));
 
   this->scene->setSceneRect(QRect( 0, 0, MainWindow::width(), MainWindow::height()));
   ui.graphicsView->setScene(scene);
   renderDrawing();

   ui.straightLineRBtn->setChecked(true);
   ui.graphicsView->setAttribute(Qt::WA_TransparentForMouseEvents);
   setMouseTracking(true);
 
    qnode.init();
}

MainWindow::~MainWindow() {}
 
 
 
void MainWindow::closeEvent(QCloseEvent *event)
{ 
   QMainWindow::closeEvent(event);
}


void MainWindow::on_button_draw_clicked()
{
    //Send ROS code 
int w = ui.graphicsView->size().width();//1200;//594;//MainWindow::width(); //594;
int h = ui.graphicsView->size().height();//700;//420;//MainWindow::height();//420;
    qnode.sendMsg(LineLst, w,h);
   ui.label->setText(QString::number(w) + " " + QString::number(h));
//MainWindow::width(), MainWindow::height();
}


void MainWindow::on_button_undo_clicked()
{
    if(LineLst.length() > 0)
    {
     QList<QPoint> tempL = LineLst.last();
    LineLst.removeLast();
    tempLst.append(tempL);
     renderDrawing();
    }
}

void MainWindow::on_button_redo_clicked()
{
    if(tempLst.length() > 0)
    {
     QList<QPoint> tempL = tempLst.last();
     tempLst.removeLast();
     LineLst.append(tempL);
     renderDrawing();
    }
}

void MainWindow::on_button_clear_clicked()
{
    LineLst.clear();
    tempLst.clear();
    renderDrawing();
}
void MainWindow::mouseReleaseEvent(QMouseEvent *e)
{ 
	  if(ui.straightLineRBtn->isChecked() == true)
	{
		 if(LineLst[LineLst.size()-1][LineLst[LineLst.size()-1].size()-1] != LineLst[LineLst.size()-1][LineLst[LineLst.size()-1].size()-2])
		{
			isFirstPoint = true;
		}
	}
	else{isFirstPoint = true;}

}

void MainWindow::mouseMoveEvent(QMouseEvent *e)
{
    QPoint origin = e->pos() - QPoint(15,15);
	//ui.label->setText(QString::number(origin.x()) + " , " + QString::number(origin.y()));
 
	if(origin.x() > 0 && origin.x() < ui.graphicsView->width() && origin.y() > 0 && origin.y() < ui.graphicsView->height())
	{
		   if(ui.curveLineRBtn->isChecked() == true)
		    { 
			if(isFirstPoint != true)
			{
				ui.label->setText(QString::number(origin.x()) + " , " + QString::number(origin.y()));
				if(euclideanDist(LineLst[LineLst.size()-1][LineLst[LineLst.size()-1].size()-1],  origin) > ui.pntDistDblSpnr->value())
				{
					LineLst[LineLst.size()-1].append(origin); 
				}
			}
		    }
		   else
		    { 
			int sz = LineLst.size();
			if(sz > 0)
			{
				if(LineLst[sz-1].size() > 0)
				{
					if(euclideanDist(LineLst[LineLst.size()-1][LineLst[LineLst.size()-1].size()-1],  origin) > ui.pntDistDblSpnr->value())
					{
						LineLst[LineLst.size()-1][LineLst[LineLst.size()-1].size()-1] = origin;
					}				
				}
			}
		   } 
	}
    renderDrawing();

}
 
float MainWindow::euclideanDist(QPoint p1, QPoint p2)
{
	return sqrt(pow((p2.x() - p1.x()),2) + pow((p2.y() - p1.y()),2));
}

void MainWindow::mousePressEvent(QMouseEvent *e)
{
   this->scene->setSceneRect(QRect( 0, 0, MainWindow::width(), MainWindow::height()));
  QPoint origin = e->pos() - QPoint(15,15);
	if(ui.curveLineRBtn->isChecked() == true)
	{ 
 		QList<QPoint> l; 
		LineLst.append(l);
             isFirstPoint = false;
	}
	else
	{ 
	    if(isFirstPoint == true)
	    {
		isFirstPoint = false;
		p1.setX(origin.x());
		p1.setY(origin.y());
		QList<QPoint> l;
		l.append(p1);
		l.append(p1);
		LineLst.append(l); 
	    }
	    else
	    {
		if(euclideanDist(LineLst[LineLst.size()-1][LineLst[LineLst.size()-1].size()-1],  origin) > ui.pntDistDblSpnr->value())
		{
			isFirstPoint = true;
			p2.setX(origin.x());
			p2.setY(origin.y());  
			if(origin.x() > 0 & origin.x() < MainWindow::width())
			{
				LineLst[LineLst.size()-1][LineLst[LineLst.size()-1].size()-1] = p2; 
			}
		}
	    }
	}
     renderDrawing();
     scene->addRect(origin.x(), origin.y(), 1, 1, mousePen, QBrush(Qt::SolidPattern));
}

void MainWindow::renderDrawing()
{
 
    ui.graphicsView->scene()->clear();
    

     for (int y =0; y<LineLst.size(); y++) 
    {
    	QList<QPoint> line = LineLst.value(y); 
	QPoint oldPoint = line.value(0);

         for (int x=1; x<line.size(); x++) 
	 {
	 	QPoint curPoint = line.value(x);;
		scene->addLine(curPoint.x(),curPoint.y(), oldPoint.x(), oldPoint.y(), robotPen);
		oldPoint = curPoint;
	 }
    }

    ui.graphicsView->setScene(scene);
 
}

}  // namespace robo_draw

