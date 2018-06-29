# #############################################################################
#
#  radiolog_viewer.py - watch a radiolog .csv file that is being written by
#    the full radiolog program, presumably running on a different computer
#    writing to a shared drive that this program can see
#
#
#   developed for Nevada County Sheriff's Search and Rescue
#    Copyright (c) 2018 Tom Grundy
#
#  http://github.com/ncssar/radiolog_viewer
#
#  Contact the author at nccaves@yahoo.com
#   Attribution, feedback, bug reports and feature requests are appreciated
#
#  REVISION HISTORY
#-----------------------------------------------------------------------------
#   DATE   |  AUTHOR  |  NOTES
#-----------------------------------------------------------------------------

# #############################################################################
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  See included file LICENSE.txt for full license terms, also
#  available at http://opensource.org/licenses/gpl-3.0.html
#
# ############################################################################
#

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pygtail import Pygtail
import sys
import os
import glob
import regex
import time

from radiolog_viewer_ui import Ui_radiolog_viewer

statusColorDict={}
statusColorDict["At IC"]=["22ff22","000000"]
statusColorDict["In Transit"]=["2222ff","eeeeee"]
statusColorDict["Waiting for Transport"]=["2222ff","eeeeee"]

class MyWindow(QMainWindow,Ui_radiolog_viewer):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.parent=parent
        self.rcFileName="radiolog_viewer.rc"
        self.ui=Ui_radiolog_viewer()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.panels={}
#         self.dockTableWidgets={}
        
        self.watchedDir="C:\\Users\\caver\\Documents"
#         self.watchedFile=""
#         self.ui.watchedDirField.setText(self.watchedDir)
#         self.setCentralWidget(self.ui.groupBox)
#         self.setStyleSheet("QDockWidget {font-size:12pt;font-weight:bold}")
        # disable AllowTabbedDocks - tabbed docks are not immediately obvious
#         self.setDockOptions(self.AnimatedDocks|self.AllowNestedDocks)
#         self.mindockHeight=50
#         self.panelColCount=1
#         self.panelRowCount=0
        self.panelWidth=300
        self.panelHeight=120
        self.panelSpacing=2
        # if a new dock would cause the window to expand taller than
        #  maxDockAreaHeight, then add a column instead and start at the top
        #  of the new column
        self.maxGridHeight=600
        self.setStyleSheet("background-color:gray")
        # default window geometry; overridden by previous rc file
        self.x=100
        self.y=100
        self.w=self.panelWidth+20
        self.h=400
        self.fontSize=10
        self.grid=[[0]]
        
        self.loadRcFile()
        self.setGeometry(int(self.x),int(self.y),int(self.w),int(self.h))
        
        self.latestCallsign=""
        self.latestColor=[230,230,255]    
        self.updateClock()
        self.rescan()
        
        self.refreshTimer=QTimer(self)
        self.refreshTimer.timeout.connect(self.refresh)
        self.refreshTimer.timeout.connect(self.updateClock)
        self.refreshTimer.start(3000)
        
    def rescan(self):
        print("scanning for latest valid csv file...")
        self.csvFiles=[]
        self.log=[]
        self.callsigns=[]
        for callsign in self.panels:
            self.ui.gridLayout.removeWidget(self.panels[callsign])
            self.panels[callsign].setParent(None)
            self.panels[callsign].deleteLater()
        self.panels={}
        self.readDir()
        self.watchedFile=self.csvFiles[0][0]
        # remove the pygtail offset file, if any, so pygtail will
        #  read from the beginning even if this file has already
        #  been read by pygtail
        if os.path.isfile(self.watchedFile+".offset"):
            os.remove(self.watchedFile+".offset")
#         self.ui.watchedFileField.setText(self.watchedFile)
        print("  found "+self.watchedFile)
        self.refresh(throb=False)
#         print("callsigns after refresh:"+str(self.callsigns))
#         print("panels after refresh:"+str(self.panels))
        if self.latestCallsign!="":
            self.panels[self.latestCallsign].throb(self.latestColor)
#         self.getGridLocations()
    
    # refresh - this is the main loop
    #  - read any new lines from the log file
    #  - process each new line
    #    - add a new panel (and place it correctly) if it's a new callsign
    #    - add a row to the appropriate panel's table    
    def refresh(self,throb=True):
        newEntries=self.readWatchedFile()
        if newEntries:
#             self.ui.logField.append(str(len(newEntries))+" new entries:\n")
            for entry in newEntries:
                if len(entry)==10:
                    time,tf,callsign,msg,radioLoc,status,epoch,d1,d2,d3=entry
                    
                    # add a new panel if needed
                    if not callsign in self.callsigns:
                        self.newPanel(callsign)
                        
                    # add new entry to the callsign's panel's table
                    p=self.panels[callsign]
                    p.statusWidget.setText(status)
                    p.statusWidget.setStyleSheet("color:#"+statusColorDict.get(status,["","000000"])[1]+";background-color:#"+statusColorDict.get(status,["eeeeee",""])[0])
                    t=p.tableWidget
                    newRowCount=t.rowCount()+1
                    t.setRowCount(newRowCount)
                    if tf=="TO":
                        tf=">"
                    elif tf=="FROM":
                        tf="<"
                    else:
                        tf="?"

 
                    t.setItem(newRowCount-1,0,QTableWidgetItem(time))
                    t.setItem(newRowCount-1,1,QTableWidgetItem(tf))
                    t.setItem(newRowCount-1,2,QTableWidgetItem(msg))
#                     p.setWindowTitle(callsign+" : "+status)

#                     self.dockTableWidgets[callsign].setSelectionMode(QAbstractItemView.NoSelection)
                    t.resizeColumnsToContents()
#                     self.dockTableWidgets[callsign].resizeRowsToContents()
#                     self.docks[callsign].palette.setColor(QPalette.Background,QColor(220,220,255))
#                     self.docks[callsign].setStyleSheet("background:rgb(220,220,255)")
#                     for d in self.docks:
#                         self.docks[d].palette.setColor(QPalette.Background,QColor(255,255,255))
#                         self.docks[d].setStyleSheet("background:white;border:1px solid gray")
#                         self.setStyleSheet("QDockWidget#"+d+"::title {background:gray}")
#                     self.docks[callsign].setStyleSheet("border:3px solid blue")
#                     self.setStyleSheet("QDockWidget#"+str(callsign).replace(" ","")+"::title {background:green}")
#                     self.ui.mdi.setActiveSubWindow(self.docks[callsign])
                    if throb:
                        p.throb(self.latestColor)
                    self.latestCallsign=callsign
        
    # get a list of non-clueLog filenames, modification times, and sizes
    #  in the watchedDir, sorted by modification time (so that the most recent
    #  file is the first item in the list)
    def readDir(self):
        f=glob.glob(self.watchedDir+"\\*.csv")
        f=[x for x in f if not regex.match('.*_clueLog.csv$',x)]
        f=[x for x in f if not regex.match('.*_fleetsync.csv$',x)]
        f=[x for x in f if not regex.match('.*_bak[123456789].csv$',x)]
        f=sorted(f,key=os.path.getmtime,reverse=True)
        for file in f:
            l=[file,os.path.getsize(file),os.path.getmtime(file)]
            self.csvFiles.append(l)

    def readWatchedFile(self):
        newEntries=[]
        for line in Pygtail(self.watchedFile):
            newEntries.append(line.split(','))
        return newEntries

    # need an intelligent method of (re)tiling MDI subwindows
    #  in a method that works best for this specific application;
    # for each new dock, follow these rules in order:
    # - define a fixed mindockHeight
    # - if there is enough vertical space for another dock on the
    #     leftmost existing column of docks, add it there; otherwise
    #     start another column of docks
    # - if mdiHeight>(maxVerticaldockCount*mindockHeight)
#     def retile(self):
#         # 1. decide what docks should go in what rows/columns
#         dockGrid=[[]]
#         mdiHeight=self.ui.mdi.height()
#         mdiWidth=self.ui.mdi.width()
#         maxRows=int(mdiHeight/self.mindockHeight)
#         col=0
#         row=0
#         for dock in self.docks.values():
#             if row>maxRows:
#                 row=0
#                 col=col+1
#                 dockGrid.append([])
#             dockGrid[col].append(dock)
#             row=row+1
#         # 2. place and size the docks accordingly
#         dockWidth=mdiWidth/(col+1)
#         x=0
#         pos=QPoint(0,0)
#         print(str(dockGrid))
#         for col in dockGrid:
#             dockHeight=mdiHeight/len(col)
#             y=0
#             for dock in col:
#                 rect=QRect(0,0,dockWidth,dockHeight)
#                 dock.setGeometry(rect)
#                 dock.move(pos)
#                 pos.setY(pos.y()+dockHeight)
#             pos.setX(pos.x()+dockWidth)

    def newPanel(self,callsign):
        self.callsigns.append(callsign)
        panel=Panel(self,callsign)
        self.panels[callsign]=panel
        panel.titleWidget.setText(callsign)
        t=panel.tableWidget
        t.horizontalHeader().setMinimumSectionSize(15)
        t.horizontalHeader().setStretchLastSection(True)
        t.verticalHeader().setDefaultSectionSize(15)
        t.horizontalHeader().hide()
        t.verticalHeader().hide()
        t.setSelectionMode(QAbstractItemView.NoSelection)
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setObjectName(callsign.replace(" ",""))
        t.setMaximumHeight(self.panelHeight-40)
        t.setMinimumHeight(self.panelHeight-40)
        t.setMaximumWidth(self.panelWidth-8)
        t.setMinimumWidth(self.panelWidth-8)
        t.setGeometry(QRect(0,0,300,200))
        self.addPanelToGrid(panel)

    def redoGrid(self):
#         self.ui.gridLayoutWidget.deleteLater()
#         self.ui.gridLayout.deleteLater()
#         self.ui.gridLayoutWidget=None
#         self.ui.gridLayout=None
        
        self.ui.gridLayoutWidget = QWidget(self)
        self.ui.gridLayoutWidget.setGeometry(QRect(218, 102, 597, 689))
        self.ui.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.ui.gridLayout = QGridLayout(self.ui.gridLayoutWidget)
        self.ui.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.ui.gridLayout.setSpacing(2)
        self.ui.gridLayout.setObjectName("gridLayout")
        self.ui.gridLayoutWidget.show()
        self.ui.gridLayoutWidget.raise_()

#         for r in range(self.ui.gridLayout.rowCount()):
#             for c in range(self.ui.gridLayout.columnCount()):
#                 print("removing at row="+str(r)+" col="+str(c))
#                 self.ui.gridLayout.removeItem(self.ui.gridLayout.itemAtPosition(r,c))
                
#         for panel in self.panels:
#             print(" removing "+panel+" "+str(self.panels[panel]))
#             self.ui.gridLayout.removeWidget(self.panels[panel])

#         print("\nAfter close:")
#         self.getFirstOpenGridLocation()
        
#             self.panels[panel].hide()
#         self.ui.gridLayout.invalidate()
#         self.ui.gridLayout.update()

        for callsign in self.panels:
            self.addPanelToGrid(self.panels[callsign])
#             self.panels[callsign].show()
#         self.ui.gridLayoutWidget.raise_()
        
        

    def addPanelToGrid(self,panel):
        [row,col]=self.getFirstOpenGridLocation()
        print("adding panel "+panel.callsign+" at row="+str(row)+" col="+str(col))
        self.ui.gridLayout.addWidget(panel,row,col)
        s=max(self.ui.gridLayout.horizontalSpacing(),self.ui.gridLayout.verticalSpacing())
        gridHeight=(self.panelHeight+s)*self.ui.gridLayout.rowCount()-s
        gridWidth=(self.panelWidth+s)*self.ui.gridLayout.columnCount()-s
        self.ui.gridLayoutWidget.setGeometry(QRect(0,50,gridWidth,gridHeight))
    
    def getFirstOpenGridLocation(self):
        rows=self.ui.gridLayout.rowCount()
        cols=self.ui.gridLayout.columnCount()
#         print("the grid currently has "+str(rows)+" rows and "+str(cols)+" columns")
#         for c in range(1,cols+1):
        for c in range(cols):
#             for r in range(1,min(rows,int(self.maxGridHeight/self.panelHeight))+1):
             for r in range(min(rows,int(self.maxGridHeight/self.panelHeight))+1):
#                 print("checking row:"+str(r)+" col:"+str(c)+" = "+str(self.ui.gridLayout.itemAtPosition(r,c)))
                if not self.ui.gridLayout.itemAtPosition(r,c):
#                     print("empty cell found at row="+str(r)+" col="+str(c))
                    return([r,c])
        return([0,c+1])
    
#               
#         c=0
#         for col in self.grid:
#             c=c+1
#             r=0
#             for row in col:
#                 r=r+1
#                 print("checking row:"+str(r)+" col:"+str(c))
#                 if row=="":
#                     return([c,r])
#         # no open location found - the existing grid is full:
#         #  add a column and return the first row in the new column
#         self.grid.append([[]])
#         return([c+1,0])
                 
    def updateClock(self):
        self.ui.clock.display(time.strftime("%H:%M"))
        
    def saveRcFile(self):
        print("saving...")
        (x,y,w,h)=self.geometry().getRect()
        rcFile=QFile(self.rcFileName)
        if not rcFile.open(QFile.WriteOnly|QFile.Text):
            warn=QMessageBox(QMessageBox.Warning,"Error","Cannot write resource file " + self.rcFileName + "; proceeding, but, current settings will be lost. "+rcFile.errorString(),
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            return
        out=QTextStream(rcFile)
        out << "[RadioLog Viewer]\n"
        out << "font-size=" << self.fontSize << "pt\n"
        out << "x=" << x << "\n"
        out << "y=" << y << "\n"
        out << "w=" << w << "\n"
        out << "h=" << h << "\n"
        rcFile.close()
        
    def loadRcFile(self):
        print("loading...")
        rcFile=QFile(self.rcFileName)
        if not rcFile.open(QFile.ReadOnly|QFile.Text):
            warn=QMessageBox(QMessageBox.Warning,"Error","Cannot read resource file " + self.rcFileName + "; using default settings. "+rcFile.errorString(),
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            return
        inStr=QTextStream(rcFile)
        line=inStr.readLine()
        if line!="[RadioLog Viewer]":
            warn=QMessageBox(QMessageBox.Warning,"Error","Specified resource file " + self.rcFileName + " is not a valid resource file; using default settings.",
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            rcFile.close()
            return
        while not inStr.atEnd():
            line=inStr.readLine()
            tokens=line.split("=")
            if tokens[0]=="x":
                self.x=int(tokens[1])
            elif tokens[0]=="y":
                self.y=int(tokens[1])
            elif tokens[0]=="w":
                self.w=int(tokens[1])
            elif tokens[0]=="h":
                self.h=int(tokens[1])
            elif tokens[0]=="font-size":
                self.fontSize=int(tokens[1].replace('pt',''))
        rcFile.close()
        
    def closeEvent(self,event):
        self.saveRcFile()
        event.accept()
        self.parent.quit()


class Panel(QFrame):
    def __init__(self,parent,callsign):
        super().__init__()
        self.parent=parent
        self.callsign=callsign
        font=QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(14)
        font.setBold(True)        
        smallFont=QFont()
        smallFont.setFamily("Segoe UI")
        smallFont.setPointSize(9)        
        self.palette=QPalette()
        self.layout=QVBoxLayout(self)
        self.titleBarLayout=QHBoxLayout()
        self.titleWidget=QLabel("label")
        self.titleWidget.setFont(font)
        self.statusWidget=QLabel()
        self.statusWidget.setFont(smallFont)
        self.statusWidget.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.closeButton=QPushButton(self)
        self.closeButton.setMinimumHeight(24)
        self.closeButton.setMaximumHeight(24)
        self.closeButton.setMinimumWidth(24)
        self.closeButton.setMaximumWidth(24)
        self.closeButton.setStyleSheet("border:none")
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setStyleSheet("""
            QPushButton:hover
                {border-image:url(:/radiolog_viewer_ui/close_dark.png)}
            QPushButton
                {border-image:url(:/radiolog_viewer_ui/close.png)}
            """)
        self.titleBarLayout.addWidget(self.titleWidget)
        self.titleBarLayout.addWidget(self.statusWidget)
        self.titleBarLayout.insertSpacing(2,20)
        self.titleBarLayout.addWidget(self.closeButton)
        self.tableWidget=QTableWidget(0,3,self)
        self.tableWidget.setStyleSheet("background-color:white")
        self.layout.insertLayout(0,self.titleBarLayout)
        self.layout.addWidget(self.tableWidget)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.statusWidget.setMinimumHeight(20)
        self.statusWidget.setMaximumHeight(20)
        self.setStyleSheet("background-color:lightgray")
        self.titleBarLayout.setSpacing(2)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(2,2,2,2)
        self.setMinimumHeight(self.parent.panelHeight)
        self.setMaximumHeight(self.parent.panelHeight)
        self.setMinimumWidth(self.parent.panelWidth)
        self.setMaximumWidth(self.parent.panelWidth)
    
    def closeEvent(self,event):
        print("closed panel "+self.callsign)
        event.accept()
#         self.deleteLater()
        del self.parent.panels[self.callsign]
        self.parent.callsigns.remove(self.callsign)
#         self.parent.ui.gridLayout.removeWidget(self)
        self.parent.redoGrid()
#         self.parent.ui.gridLayoutWidget.repaint()

        
    def throb(self,final=[255,255,255],n=0):
        # this function calls itself recursivly 25 times to throb the background blue->white
#         rprint("throb:n="+str(n))
        self.palette.setColor(QPalette.Background,QColor(n*10,n*10,255))
        self.setStyleSheet("background:rgb("+str(n*10)+","+str(n*10)+",255)")
        self.setPalette(self.palette)
        if n<25:
            #fix #333: make throbTimer a normal timer and then call throbTimer.setSingleShot,
            # so we can just stop it using .stop() when the widget is closed
            # to avert 'wrapped C/C++ object .. has been deleted'
#             self.throbTimer=QTimer.singleShot(15,lambda:self.throb(n+1))
            self.throbTimer=QTimer()
            self.throbTimer.timeout.connect(lambda:self.throb(final,n+1))
            self.throbTimer.setSingleShot(True)
            self.throbTimer.start(25)
        else:
#             rprint("throb complete")
            self.throbTimer=None
            self.palette.setColor(QPalette.Background,QColor(final[0],final[1],final[2]))
            self.setStyleSheet("background:rgb("+str(final[0])+","+str(final[1])+","+str(final[2])+")")
            self.setPalette(self.palette)
        
        
def main():
    app = QApplication(sys.argv)
    w = MyWindow(app)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
