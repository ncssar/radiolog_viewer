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

from radiolog_viewer_ui import Ui_radiolog_viewer


class MyWindow(QDialog,Ui_radiolog_viewer):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.parent=parent
        self.ui=Ui_radiolog_viewer()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.watchedDir="C:\\Users\\caver\\Documents"
        self.ui.watchedDirField.setText(self.watchedDir)
        self.rescan()
        self.refresh()
        self.readTimer=QTimer(self)
        self.readTimer.timeout.connect(self.refresh)
        self.readTimer.start(3000)
        
    def rescan(self):
        print("scanning for latest valid csv file...")
        self.csvFiles=[]
        self.log=[]
        self.callsigns=[]
        self.panels={}
        self.panelTableWidgets={}
        self.ui.logField.clear()
        self.readDir()
        self.watchedFile=self.csvFiles[0][0]
        # remove the pygtail offset file, if any, so pygtail will
        #  read from the beginning even if this file has already
        #  been read by pygtail
        os.remove(self.watchedFile+".offset")
        self.ui.watchedFileField.setText(self.watchedFile)
        print("  found "+self.watchedFile)
        
    def refresh(self):
        newEntries=self.readWatchedFile()
        if newEntries:
            self.ui.logField.append(str(len(newEntries))+" new entries:\n")
            for entry in newEntries:
                if len(entry)==10:
                    self.log.append(entry)
                    time,tf,callsign,msg,radioLoc,status,epoch,d1,d2,d3=entry
                    self.ui.logField.append(str(entry))
                    
                    # add a new panel if needed
                    if not callsign in self.callsigns:
                        self.callsigns.append(callsign)
                        sub=Panel(self)
                        self.panels[callsign]=sub
                        table=QTableWidget(0,3)
                        self.panelTableWidgets[callsign]=table
                        table.horizontalHeader().setMinimumSectionSize(15)
                        table.horizontalHeader().setStretchLastSection(True)
                        table.verticalHeader().setDefaultSectionSize(15)
                        table.horizontalHeader().hide()
                        table.verticalHeader().hide()               
                        sub.setWidget(table)
                        sub.setWindowFlags(Qt.WindowTitleHint)
                        sub.setWindowTitle(callsign)
                        self.ui.mdi.addSubWindow(sub)
                        sub.show()
                        self.ui.mdi.tileSubWindows()
                        
                    # add new entry to the callsign's table
                    newRowCount=self.panelTableWidgets[callsign].rowCount()+1
                    self.panelTableWidgets[callsign].setRowCount(newRowCount)
                    if tf=="TO":
                        tf=">"
                    elif tf=="FROM":
                        tf="<"
                    else:
                        tf="?"
                    self.panelTableWidgets[callsign].setItem(newRowCount-1,0,QTableWidgetItem(time))
                    self.panelTableWidgets[callsign].setItem(newRowCount-1,1,QTableWidgetItem(tf))
                    self.panelTableWidgets[callsign].setItem(newRowCount-1,2,QTableWidgetItem(msg))
                    self.panels[callsign].setWindowTitle(callsign+" : "+status)
                    self.panelTableWidgets[callsign].resizeColumnsToContents()
                    self.ui.mdi.setActiveSubWindow(self.panels[callsign])
        
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
    # for each new panel, follow these rules in order:
    # - define a fixed minPanelHeight
    # - if there is enough vertical space for another panel on the
    #     leftmost existing column of panels, add it there; otherwise
    #     start another column of panels
    # - if mdiHeight>(maxVerticalPanelCount*minPanelHeight)
#     def retile(self):
#         # 1. decide what panels should go in what rows/columns
#         panelGrid=[][]
#         mdiHeight=self.ui.mdi.height()
#         maxRows=int(mdiHeight/self.minPanelHeight)
#         col=0
#         row=0
#         for panel in self.panels:
#             if row>maxRows:
#                 row=0
#                 col=col+1
#             panelGrid[col][row]=panel
#             row=row+1
#         # 2. place and size the panels accordingly
#         panelWidth=mdiWidth/(col+1)
#         x=0
#         pos=QPoint(0,0)
#         for col in panelGrid:
#             panelHeight=mdiHeight/len(panelGrid[col])
#             y=0
#             for row in panelGrid[col]:
#                 rect=QRect(0,0,colWidth,panelHeight)
#                 panelGrid[col][row].setGeometry(rect)
#                 panelGrid[col][row].move(pos)
#                 pos.setY(pos.y()+panelHeight)
#             pos.setX(pos.x()+panelWidth)


class Panel(QMdiSubWindow):
    def __init__(self,parent,*args):
        QMdiSubWindow.__init__(self,*args)
        self.parent=parent
    
    def closeEvent(self,event):
        print("closing")
        QTimer.singleShot(200,self.parent.ui.mdi.tileSubWindows)
        
        
def main():
    app = QApplication(sys.argv)
    w = MyWindow(app)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
