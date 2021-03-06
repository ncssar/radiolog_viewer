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
import shutil
import glob
import regex
import time

from radiolog_viewer_ui import Ui_radiolog_viewer

statusColorDict={}
statusColorDict["At IC"]=["22ff22","000000"]
statusColorDict["Available"]=["00ffff","000000"]
statusColorDict["In Transit"]=["2222ff","eeeeee"]
statusColorDict["Waiting for Transport"]=["2222ff","eeeeee"]

stateColorDict={}
stateColorDict["#ff4444"]="#eeeeee"
stateColorDict["#eeeeee"]="#ff4444"

class MyWindow(QDialog,Ui_radiolog_viewer):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.parent=parent
        self.rcFileName="radiolog_viewer.rc"
        self.configFileName="./local/radiolog_viewer.cfg"
        self.readConfigFile()
        if not os.path.isdir(self.watchedDir):
            err=QMessageBox(QMessageBox.Critical,"Error","Specified directory to be watched does not exist:\n \n  "+self.watchedDir+"\n \nAborting.",
                            QMessageBox.Close,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            err.show()
            err.raise_()
            err.exec_()
            exit(-1)
        self.ui=Ui_radiolog_viewer()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose) 
        self.panels={}
        self.panelWidth=500
        self.panelHeight=120
        self.panelSpacing=2      
        # if a new panel would cause the window to expand taller than
        #  maxGridHeight, then add a column instead and start at the top
        #  of the new column
        self.maxGridHeight=600
        self.setStyleSheet("background-color:#333333")
        self.ui.groupBox.setStyleSheet("background-color:lightgray")
        # default window geometry; overridden by previous rc file
        self.x=100
        self.y=100
        self.w=self.panelWidth+20
        self.h=400
        self.fontSize=12
        self.grid=[[0]]
        self.sidebarMode=False
        self.sidebarJustToggled=False
        self.setMinimumSize(200,200)
        
        self.normalTableFont=QFont()
        self.normalTableFont.setPixelSize(self.fontSize)
        self.latestTableFont=QFont()
        self.latestTableFont.setPixelSize(self.fontSize)
        self.latestTableFont.setBold(True)
         
        self.latestCallsign=""
        self.normalFrameColor=[150,150,150]
        self.latestFrameColor=[230,230,255]
        self.normalTableColor=[200,200,200]
        self.latestTableColor=[255,255,255]  
        
        sidebarTableFont=QFont()
        sidebarTableFont.setFamily("Segoe UI")
        sidebarTableFont.setPointSize(14)
        sidebarTableFont.setBold(True)
        self.sidebarTableWidget=QTableWidget(0,2,self)
        self.sidebarTableWidget.setFont(sidebarTableFont)
        self.ui.verticalLayout.addWidget(self.sidebarTableWidget)
        self.sidebarTableWidget.hide()
        self.sidebarTableWidget.horizontalHeader().hide()
        self.sidebarTableWidget.verticalHeader().hide()
        self.sidebarTableWidget.setStyleSheet("background:rgb(240,240,240)")
        self.sidebarTableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.sidebarTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.loadRcFile()
        self.setGeometry(int(self.x),int(self.y),int(self.w),int(self.h))
 
        self.resizeTimer=QTimer()
        self.resizeTimer.setSingleShot(True)
        self.resizeTimer.timeout.connect(self.resizeEventPost)
                 
        self.updateClock()

#         self.parent.setStyleSheet("QMessageBox QPushButton{background-color: green}")
        self.ui.notYet=QMessageBox(QMessageBox.Information,"Waiting...","No valid radiolog file was found.\nRe-scanning every few seconds...",
                    QMessageBox.Abort,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
        self.ui.notYet.setStyleSheet("background-color: lightgray")
        self.ui.notYet.setModal(False)
        self.ui.notYet.show()
        self.ui.notYet.buttonClicked.connect(self.notYetButtonClicked)

        self.rescanTimer=QTimer(self)
        self.rescanTimer.timeout.connect(self.rescan)
        self.rescanTimer.start(2000)
        
        self.refreshTimer=QTimer(self)
        self.refreshTimer.timeout.connect(self.refresh)
        self.refreshTimer.timeout.connect(self.updateClock)
        self.refreshTimer.start(3000)
    
    def readConfigFile(self):
        # create the file (and its directory) if it doesn't already exist
        dir=os.path.dirname(self.configFileName)
        if not os.path.exists(self.configFileName):
            print("Config file "+self.configFileName+" not found.")
            if not os.path.isdir(dir):
                try:
                    print("Creating config dir "+dir)
                    os.makedirs(dir)
                except:
                    print("ERROR creating directory "+dir+" for config file.  Better luck next time.")
            try:
                defaultConfigFileName=os.path.join(os.path.dirname(os.path.realpath(__file__)),"default.cfg")
                print("Copying default config file "+defaultConfigFileName+" to "+self.configFileName)
                shutil.copyfile(defaultConfigFileName,self.configFileName)
            except:
                print("ERROR copying the config file.  Better luck next time.")
                
        # specify defaults here
        self.watchedDir="Z:\\"
        
        configFile=QFile(self.configFileName)
        if not configFile.open(QFile.ReadOnly|QFile.Text):
            warn=QMessageBox(QMessageBox.Warning,"Error","Cannot read configuration file " + self.configFileName + "; using default settings. "+configFile.errorString(),
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            return
        inStr=QTextStream(configFile)
        line=inStr.readLine()
        if line!="[RadioLogViewer]":
            warn=QMessageBox(QMessageBox.Warning,"Error","Specified configuration file " + self.configFileName + " is not a valid configuration file; using default settings.",
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            configFile.close()
            return
        
        while not inStr.atEnd():
            line=inStr.readLine()
            tokens=line.split("=")
            if tokens[0]=="watchedDir":
                self.watchedDir=tokens[1]
                print("watchedDir specification "+self.watchedDir+" parsed from config file.")
        configFile.close()
        
        # validation and post-processing of each item
        configErr=""

        # process any ~ characters
        self.watchedDir=os.path.expanduser(self.watchedDir)             
            
        if configErr:
            self.configErrMsgBox=QMessageBox(QMessageBox.Warning,"Non-fatal Configuration Error(s)","Error(s) encountered in config file "+self.configFileName+":\n\n"+configErr,
                             QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            self.configErrMsgBox.exec_()

    def notYetButtonClicked(btn):
        exit()
            
    def rescan(self):
        print("scanning "+self.watchedDir+" for latest valid csv file...")
        self.csvFiles=[]
        self.log=[]
        self.callsigns=[]
        self.sidebarTableWidget.setRowCount(0) # delete all rows
        for callsign in self.panels:
            self.ui.gridLayout.removeWidget(self.panels[callsign])
            self.panels[callsign].setParent(None)
            self.panels[callsign].deleteLater()
        self.panels={}
        self.readDir()
        if self.csvFiles!=[]:
            self.rescanTimer.stop()
            self.ui.notYet.close()
            self.watchedFile=self.csvFiles[0][0]
            self.setWindowTitle("RadioLog Viewer - "+os.path.basename(self.watchedFile))
            # remove the pygtail offset file, if any, so pygtail will
            #  read from the beginning even if this file has already
            #  been read by pygtail
            self.offsetFileName=self.watchedFile+".offset"+str(os.getpid())
            if os.path.isfile(self.offsetFileName):
                os.remove(self.offsetFileName)
            print("  found "+self.watchedFile)
            self.refresh(throb=False)
            if self.latestCallsign!="":
                self.panels[self.latestCallsign].throb(self.latestFrameColor)
        
    # refresh - this is the main loop
    #  - read any new lines from the log file
    #  - process each new line
    #    - add a new panel (and place it correctly) if it's a new callsign
    #    - add a row to the appropriate panel's table    
    def refresh(self,throb=True):
        if self.csvFiles!=[]:
            newEntries=self.readWatchedFile()
            if newEntries:
                for entry in newEntries:
                    if len(entry)==10:
                        time,tf,callsign,msg,radioLoc,status,epoch,d1,d2,d3=entry
                        
                        # add a new panel if needed
                        if not callsign in self.callsigns:
                            st=self.sidebarTableWidget
                            newRowCount=st.rowCount()+1
                            st.setRowCount(newRowCount)
                            t1=QTableWidgetItem(callsign)
                            t2=QTableWidgetItem(time)
                            st.setItem(newRowCount-1,0,t1)
                            st.setItem(newRowCount-1,1,t2)
                            self.newPanel(callsign)
                        
                        # update sidebar table
                        st=self.sidebarTableWidget
                        stRow=0
                        for n in range(st.rowCount()):
                            if st.item(n,0):
                                if st.item(n,0).text()==callsign:
                                    stRow=n
                        st1=QTableWidgetItem(callsign)
                        st2=QTableWidgetItem(time)
#                         st2.setBackground(QColor(statusColorDict.get(status,["eeeeee",""])[0]))
                        st.setItem(stRow,0,st1) # redundant, but, will highlight any table sync issues
                        st.setItem(stRow,1,st2)
#                         st.item(stRow,1).setData(Qt.BackgroundRole,QVariant(QColor(statusColorDict.get(status,["eeeeee",""])[0])))
#                         st.item(stRow,1).setData(Qt.BackgroundRole,QVariant(QColor(255,0,0)))
#                         st.item(stRow,1).setBackground(QColor(200,0,0))
#                         st.item(stRow,1).setBackground(QColor("#00ffff"))
                        print("status:"+status+"  color:"+statusColorDict.get(status,["eeeeee",""])[0])
                        st.item(stRow,1).setBackground(QColor("#"+statusColorDict.get(status,["eeeeee",""])[0]))
                        
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
     
                        t1=QTableWidgetItem(time)
                        t2=QTableWidgetItem(tf)
                        t3=QTableWidgetItem(msg)
                        
                        r=newRowCount-2
                        t.setItem(r,0,t1)
                        t.setItem(r,1,t2)
                        t.setItem(r,2,t3)
                        
                        self.setRowColor(t,r,"#ff4444")
    
                        if newRowCount>2:
                            t.item(r-1,0).setFont(self.normalTableFont)
                            t.item(r-1,1).setFont(self.normalTableFont)
                            t.item(r-1,2).setFont(self.normalTableFont)
                        
                        t.item(r,0).setFont(self.latestTableFont)
                        t.item(r,1).setFont(self.latestTableFont)
                        t.item(r,2).setFont(self.latestTableFont)
                        
                        t1.setTextAlignment(Qt.AlignLeft|Qt.AlignTop)
                        t2.setTextAlignment(Qt.AlignLeft|Qt.AlignTop)                    
                        t3.setTextAlignment(Qt.AlignLeft|Qt.AlignTop)
                     
                        t.resizeRowToContents(r)
                        y=t.verticalHeader().sectionSize(r)
                        y2=y
                        if y==30:
                            y2=15
                            t.verticalHeader().resizeSection(r,y2)
                            
    #                     print(callsign+":"+time+"  row size:"+str(y)+"-->"+str(y2))
                        
                        t.verticalHeader().setStyleSheet("border:0px;padding:-1px;margin:-1px")
                        t.verticalHeader().setMinimumSectionSize(1)
                        t.scrollToBottom()
                        self.setColors(p,throb)
                        self.latestCallsign=callsign

    def setRowColor(self,table,row,color):
        for col in range(table.columnCount()):
            table.item(row,col).setBackground(QColor(color))
        
    def tableCellClicked(self,row,col):
        table=self.sender()
        i=table.item(row,col)
        if i:
            prevColor=i.background().color().name()
            newColor=stateColorDict.get(prevColor,"#cccccc")
            self.setRowColor(table,row,newColor)
        
    def setColors(self,panel,throb):
        c=self.normalFrameColor
        t1=self.normalTableColor
        t2=self.latestTableColor
        for callsign in self.panels:
            p1=self.panels[callsign]
            p1.setFrameShape(QFrame.Panel)
            p1.setFrameShadow(QFrame.Sunken)
            p1.palette.setColor(QPalette.Background,QColor(c[0],c[1],c[2]))
            p1.setStyleSheet("background:rgb("+str(c[0])+","+str(c[1])+","+str(c[2])+")")
            p1.tableWidget.setStyleSheet("background:rgb("+str(t1[0])+","+str(t1[1])+","+str(t1[2])+")")
        panel.setFrameShape(QFrame.Panel)
        panel.setFrameShadow(QFrame.Raised)
        panel.tableWidget.setStyleSheet("background:rgb("+str(t2[0])+","+str(t2[1])+","+str(t2[2])+")")
        if throb:
            panel.throb(self.latestFrameColor)

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
        for line in Pygtail(self.watchedFile,offset_file=self.offsetFileName):
            newEntries.append(line.split(','))
        return newEntries

    def newPanel(self,callsign):
        self.callsigns.append(callsign)
        panel=Panel(self,callsign)
        self.panels[callsign]=panel
        panel.titleWidget.setText(callsign)
        t=panel.tableWidget
        t.cellClicked.connect(self.tableCellClicked)
        t.horizontalHeader().setMinimumSectionSize(15)
        t.horizontalHeader().setStretchLastSection(True)
        t.verticalHeader().setDefaultSectionSize(15)
        t.verticalHeader().setMinimumSectionSize(15)
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
        t.setRowCount(1)
        self.addPanelToGrid(panel)
        if self.sidebarMode:
            panel.hide()

    def redoGrid(self):
#         self.ui.gridLayoutWidget = QWidget(self)
#         self.ui.gridLayoutWidget.setGeometry(QRect(218, 102, 597, 689))
#         self.ui.gridLayoutWidget.setObjectName("gridLayoutWidget")
#         self.ui.gridLayout = QGridLayout(self.ui.gridLayoutWidget)
        self.ui.gridLayout=QGridLayout()
        self.ui.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.ui.gridLayout.setSpacing(2)
        self.ui.gridLayout.setObjectName("gridLayout")
        self.ui.verticalLayout.addLayout(self.ui.gridLayout)
#         self.ui.gridLayoutWidget.show()
#         self.ui.gridLayoutWidget.raise_()
        for callsign in self.panels:
            self.addPanelToGrid(self.panels[callsign])

    def addPanelToGrid(self,panel):
        [row,col]=self.getFirstOpenGridLocation()
        print("adding panel "+panel.callsign+" at row="+str(row)+" col="+str(col))
        self.ui.gridLayout.addWidget(panel,row,col)
        s=max(self.ui.gridLayout.horizontalSpacing(),self.ui.gridLayout.verticalSpacing())
        gridHeight=(self.panelHeight+s)*self.ui.gridLayout.rowCount()-s
        gridWidth=(self.panelWidth+s)*self.ui.gridLayout.columnCount()-s
#         self.ui.gridLayoutWidget.setGeometry(QRect(0,50,gridWidth,gridHeight))
    
    def getFirstOpenGridLocation(self):
        rows=self.ui.gridLayout.rowCount()
        cols=self.ui.gridLayout.columnCount()
#         print("the grid currently has "+str(rows)+" rows and "+str(cols)+" columns")
        for c in range(cols):
            for r in range(min(rows,int(self.maxGridHeight/self.panelHeight))+1):
#                 print("checking row:"+str(r)+" col:"+str(c)+" = "+str(self.ui.gridLayout.itemAtPosition(r,c)))
                if not self.ui.gridLayout.itemAtPosition(r,c):
#                     print("empty cell found at row="+str(r)+" col="+str(c))
                    return([r,c])
        return([0,c+1])
                 
    def updateClock(self):
        self.ui.clock.display(time.strftime("%H:%M"))
        
    def saveRcFile(self):
        print("saving...")
        (self.x,self.y,self.w,self.h)=self.geometry().getRect()
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
        out << "x=" << self.x << "\n"
        out << "y=" << self.y << "\n"
        out << "w=" << self.w << "\n"
        out << "h=" << self.h << "\n"
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
        
        # make sure specified screen position and size will fit on the available screens
        #  (in case rc file was saved on dual display but now running on single)
        desktop=QApplication.desktop()
        h=desktop.height()
        w=desktop.width()
        print("Available desktop size: "+str(w)+" x "+str(h))
        if self.x>w:
            self.x=self.x-w # assume the same first screen was used when rc was saved
        if self.x>w:
            self.x=200 # if still off the screen, use a hardcoded fallback
        if self.w+self.x>w:
            self.w=w-self.x-100 # cut it off 100px from the right edge of the screen
        
    def resizeEvent(self,event):
        self.resizeTimer.start(500)
        event.accept()
        
    def resizeEventPost(self):
        self.maxGridHeight=self.height()-190
        if not self.sidebarJustToggled:
            self.redoGrid()
            self.sidebarJustToggled=False
    
    def sidebarToggle(self):
        self.sidebarJustToggled=True # to prevent redoGrid during resizeEventPost
        if self.sidebarMode:
            print("Exiting sidebar mode")
            for p in self.panels:
                self.panels[p].show()
            self.sidebarTableWidget.hide()
            self.setGeometry(self.x,self.y,self.w,self.h)
            self.ui.rescanButton.show()
            self.redoGrid()
            self.sidebarMode=False
        else:
            print("Entering sidebar mode")
            for p in self.panels:
                self.panels[p].hide()
            self.sidebarTableWidget.show()
            (self.x,self.y,self.w,self.h)=self.geometry().getRect()
            self.ui.rescanButton.hide()
            self.setGeometry(0,0,200,QApplication.desktop().screenGeometry().height())
            self.sidebarMode=True

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
        smallFont.setPointSize(10)        
        self.palette=QPalette()
        self.layout=QVBoxLayout(self)
        self.titleBarLayout=QHBoxLayout()
        self.titleWidget=QLabel("label")
        self.titleWidget.setFont(font)
        self.statusWidget=QLabel()
        self.statusWidget.setFont(smallFont)
        self.statusWidget.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.closeButton=QPushButton(self)
        self.closeButton.setMinimumHeight(20)
        self.closeButton.setMaximumHeight(20)
        self.closeButton.setMinimumWidth(20)
        self.closeButton.setMaximumWidth(20)
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
        # default vertical header ResizeToContents behavior apparently gets
        #  rid of vertical padding on rows that have been expanded
        #  for multi-line text, but padding remains on rows that
        #  have not been expanded (only have one line of text);
        #  this is wasted space; would like to have no vertical padding
        #  regardless of number of rows; if sectionResizeMode is
        #  left at the default, there is no vertical padding (but rows
        #  do not get resized, i.e. long entries get chopped off);
        #  the following line does not change the behavior
        # minimumSectionSize gets overridden when ResizeToContents is used
#         self.tableWidget.setStyleSheet("QTableWidget:item {border:0px;padding:0px;margin:0px}")
        self.tableWidget.setWordWrap(True)
        self.tableWidget.setTextElideMode(Qt.ElideNone)
        vh=self.tableWidget.verticalHeader()
        vh.setMinimumSectionSize(20) # minimum row height
        hh=self.tableWidget.horizontalHeader()
        hh.setMinimumSectionSize(20)
        hh.resizeSection(0,40)
        hh.resizeSection(1,20)
        hh.setStretchLastSection(True)
    
        self.layout.insertLayout(0,self.titleBarLayout)
        self.layout.addWidget(self.tableWidget)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.statusWidget.setMinimumHeight(20)
        self.statusWidget.setMaximumHeight(20)
        self.setStyleSheet("background-color:#666666")
        self.titleBarLayout.setSpacing(2)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(2,2,2,2)
        self.setMinimumHeight(self.parent.panelHeight)
        self.setMaximumHeight(self.parent.panelHeight)
        self.setMinimumWidth(self.parent.panelWidth)
        self.setMaximumWidth(self.parent.panelWidth)
        self.throbTimer=None
    
    def closeEvent(self,event):
        print("closed panel "+self.callsign)
        event.accept()
        del self.parent.panels[self.callsign]
        self.parent.callsigns.remove(self.callsign)
        self.parent.redoGrid()
        if self.throbTimer:
            self.throbTimer.stop()
        
    def throb(self,final=[255,255,255],n=0):
        # this function calls itself recursivly 25 times to throb the background blue->white
        self.palette.setColor(QPalette.Background,QColor(n*10,n*10,255))
        self.setStyleSheet("background:rgb("+str(n*10)+","+str(n*10)+",255)")
        self.setPalette(self.palette)
        if n<25:
            self.throbTimer=QTimer()
            self.throbTimer.timeout.connect(lambda:self.throb(final,n+1))
            self.throbTimer.setSingleShot(True)
            self.throbTimer.start(25)
        else:
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
