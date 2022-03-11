# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :: Welcome to PipeCAD!                                      ::
# ::  ____                        ____     ______  ____       ::
# :: /\  _`\   __                /\  _`\  /\  _  \/\  _`\     ::
# :: \ \ \L\ \/\_\  _____      __\ \ \/\_\\ \ \L\ \ \ \/\ \   ::
# ::  \ \ ,__/\/\ \/\ '__`\  /'__`\ \ \/_/_\ \  __ \ \ \ \ \  ::
# ::   \ \ \/  \ \ \ \ \L\ \/\  __/\ \ \L\ \\ \ \/\ \ \ \_\ \ ::
# ::    \ \_\   \ \_\ \ ,__/\ \____\\ \____/ \ \_\ \_\ \____/ ::
# ::     \/_/    \/_/\ \ \/  \/____/ \/___/   \/_/\/_/\/___/  ::
# ::                  \ \_\                                   ::
# ::                   \/_/                                   ::
# ::                                                          ::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# PipeCAD - Piping Design Software.
# Copyright (C) 2021 Wuhan OCADE IT. Co., Ltd.
# Author: Shing Liu(eryar@163.com)
# Date: 10:11 2021-09-19

from PythonQt.QtCore import *
from PythonQt.QtGui import *
from PythonQt.QtSql import *

from PipeCAD import *

import os

class CategoryDialog(QDialog):
    """docstring for CategoryDialog"""
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        
        self.setupUi()
    # __init__

    def setupUi(self):
        self.resize(280, 80)

        self.verticalLayout = QVBoxLayout(self)
        self.formLayout = QFormLayout()

        # Name
        self.labelName = QLabel("Name")
        self.textName = QLineEdit()

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelName)
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.textName)

        self.labelDetail = QLabel("Detail")
        self.textDetail = QLineEdit()

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.labelDetail)
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.textDetail)

        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.verticalLayout.addWidget(self.buttonBox)
    # setupUi
# CategoryDialog

class StandardDialog(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)

        aWindowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint

        self.setWindowFlags(aWindowFlags)
        
        self.setupUi()
    # __init__

    def setupUi(self):
        self.resize(860, 680)
        self.setWindowTitle(self.tr("Standard Component"))
        
        self.verticalLayout = QVBoxLayout(self)
        
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        
        self.database = QSqlDatabase.addDatabase("QSQLITE", "PipeStd")
        self.database.setDatabaseName("PipeStd.db")
        self.database.open()

        self.tableModel = QSqlTableModel(self, self.database)

        self.queryModel = QSqlQueryModel()
        
        self.treeWidget = QTreeWidget()
        self.treeWidget.header().setVisible(False)
        self.treeWidget.minimumWidth = 280
        self.treeWidget.maximumWidth = 580
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.customContextMenuRequested)

        self.actionAddCate = QAction(QIcon(":/PipeCad/Resources/plus-white.png"), "Add Category", self)
        self.actionModCate = QAction(QIcon(":/PipeCad/Resources/hammer.png"), "Modify Category", self)
        self.actionDelCate = QAction(QIcon(":/PipeCad/Resources/minus-white.png"), "Delete Category", self)

        self.actionAddCate.triggered.connect(self.addCategory)
        self.actionModCate.triggered.connect(self.modifyCategory)
        self.actionDelCate.triggered.connect(self.deleteCategory)

        self.treeWidget.currentItemChanged.connect(self.currentItemChanged)

        aRootItem = QTreeWidgetItem(self.treeWidget)
        aRootItem.setExpanded(True)
        aRootItem.setText(0, u"STANDARD");
        aRootItem.setIcon(0, QIcon(":/PipeCad/Resources/WORL.png"))

        aCataQueryModel = QSqlQueryModel()
        aSectQueryModel = QSqlQueryModel()
        aCateQueryModel = QSqlQueryModel()
        aItemQueryModel = QSqlQueryModel()

        aItemIcon = QIcon(":/PipeCad/Resources/ITEM.png")

        aCataQueryModel.setQuery("SELECT id, name, icon FROM CATA", self.database)
        for r in range(aCataQueryModel.rowCount()):
            aRecord = aCataQueryModel.record(r)
            aCataId = aRecord.field("id").value()
            aIconName = ":/PipeCad/Resources/" + aRecord.field("icon").value()
            aCataItem = QTreeWidgetItem(aRootItem)
            aCataItem.setText(0, aRecord.field("name").value())
            aCataItem.setIcon(0, QIcon(aIconName))

            aSectQueryModel.setQuery("SELECT id, name, icon FROM SECT WHERE pid=" + str(aCataId), self.database)
            for s in range(aSectQueryModel.rowCount()):
                aRecord = aSectQueryModel.record(s)
                aSectId = aRecord.field("id").value()
                aIconName = ":/PipeCad/Resources/" + aRecord.field("icon").value()
                aSectItem = QTreeWidgetItem(aCataItem)
                aSectItem.setText(0, aRecord.field("name").value())
                aSectItem.setIcon(0, QIcon(":/PipeCad/Resources/CATA.png"))

                aIconFile = QFile(aIconName)
                if aIconFile.exists():
                    aIcon = QIcon(aIconName)
                else:
                    aIcon = aItemIcon

                aCateQueryModel.setQuery("SELECT id, name, tooltip FROM CATE WHERE pid=" + str(aSectId), self.database)
                for c in range (aCateQueryModel.rowCount()):
                    aRecord = aCateQueryModel.record(c)
                    aCateId = aRecord.field("id").value()
                    aCateItem = QTreeWidgetItem(aSectItem, 2)
                    aCateItem.setText(0, aRecord.field("name").value())
                    aCateItem.setIcon(0, aIcon)
                    aCateItem.setData(0, Qt.UserRole, aCateId)
                    aCateItem.setToolTip(0, aRecord.field("tooltip").value())

                    aItemQueryModel.setQuery("SELECT id, name, detail FROM SDTE WHERE pid=" + str(aCateId), self.database)
                    for i in range (aItemQueryModel.rowCount()):
                        aRecord = aItemQueryModel.record(i)
                        aStadItem = QTreeWidgetItem(aCateItem, 1)
                        aStadItem.setData(0, Qt.UserRole, aRecord.field("id").value())
                        aStadItem.setText(0, aRecord.field("name").value())
                        aStadItem.setIcon(0, QIcon(":/PipeCad/Resources/SCOM.png"))
                        aStadItem.setToolTip(0, aRecord.field("detail").value())
                    # for
                # for
            # for
        # for
        
        self.labelDiagram = QLabel(self)
        self.labelDiagram.setMinimumSize(QSize(500, 380))
        self.labelDiagram.setPixmap(QPixmap(":/PipeCad/Resources/tube-diagram.png"))
        
        self.horizontalLayout.addWidget(self.treeWidget)
        self.horizontalLayout.addWidget(self.labelDiagram)
        
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        self.tableView.setGridStyle(Qt.SolidLine)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.tableView.verticalHeader().setMinimumSectionSize(18)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.verticalLayout.addWidget(self.tableView)

        aInsertAction = QAction(QIcon(":/PipeCad/Resources/plus-white.png"), "Insert Record", self)
        aDeleteAction = QAction(QIcon(":/PipeCad/Resources/minus-white.png"), "Delete Record", self)

        aInsertAction.triggered.connect(self.insertRecord)
        aDeleteAction.triggered.connect(self.deleteRecord)

        self.tableView.addAction(aInsertAction)
        self.tableView.addAction(aDeleteAction)

        # Action buttons.
        self.horizontalLayout = QHBoxLayout()
        self.buttonExport = QPushButton("Export")
        self.buttonImport = QPushButton("Import")

        self.buttonExport.clicked.connect(self.exportRecord)
        self.buttonImport.clicked.connect(self.importRecord)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.horizontalLayout.addWidget(self.buttonExport)
        self.horizontalLayout.addWidget(self.buttonImport)
        self.horizontalLayout.addWidget(self.buttonBox)

        self.verticalLayout.addLayout(self.horizontalLayout)
    # setupUi

    def customContextMenuRequested(self, thePos):

        aItem = self.treeWidget.itemAt(thePos)
        if aItem is None:
            return

        aType = aItem.type()
        aContextMenu = QMenu(self)

        if aType == 1:
            aContextMenu.addAction(self.actionAddCate)
            aContextMenu.addAction(self.actionModCate)
            aContextMenu.addAction(self.actionDelCate)
            aContextMenu.exec(QCursor.pos())
        elif aType == 2:
            aContextMenu.addAction(self.actionAddCate)
            aContextMenu.exec(QCursor.pos())

    # customContextMenuRequested

    def insertRecord(self):
        aRowCount = self.tableView.model().rowCount()
        aIndex = self.tableView.currentIndex()
        if aIndex.isValid() or aRowCount == 0:
            self.tableModel.insertRow(aRowCount)
            self.tableModel.setData(self.tableModel.index(aRowCount, 1), self.treeWidget.currentItem().data(0, Qt.UserRole))
    # insertRecord

    def deleteRecord(self):
        aIndex = self.tableView.currentIndex()
        if aIndex.isValid():
            if QMessageBox.question(self, "", "Are you sure to delete the selected record?") == QMessageBox.Yes:
                self.tableView.model().removeRow(aIndex.row())
    # deleteRecord

    def exportRecord(self):
        QMessageBox.information(self, "", "export record")
    # exportRecord

    def importRecord(self):
        QMessageBox.information(self, "", "import record")
    # importRecord

    def currentItemChanged(self, theCurrentItem):

        if theCurrentItem.type() == 1:
            aTable = theCurrentItem.parent().text(0)
            aCateId = theCurrentItem.data(0, Qt.UserRole)

            self.tableModel.setTable(aTable)
            self.tableModel.setFilter("pid=" + str(aCateId))
            self.tableModel.select()

            self.tableView.hideColumn(0)
            self.tableView.hideColumn(1)
            self.tableView.resizeColumnsToContents()

            aPixmap = ":/PipeCad/Resources/" + aTable.lower() + "-diagram.png"
            self.labelDiagram.setPixmap(QPixmap(aPixmap))
        else:
            self.tableModel.setTable("")
            self.tableModel.select()

            self.labelDiagram.setPixmap(QPixmap())

    # currentItemChanged

    def addCategory(self):
        aItem = self.treeWidget.currentItem()
        aCateDlg = CategoryDialog(self)
        aCateDlg.setWindowTitle(self.tr("Add Category"))
        if aCateDlg.exec() == QDialog.Rejected:
            return

        aName = aCateDlg.textName.text
        aDetail = aCateDlg.textDetail.text
        if len(aName) < 1 or len(aDetail) < 1:
            QMessageBox.warning(self, "", "Please enter category name or detail!")
            return

        if aItem.type() == 1:
            aStadItem = QTreeWidgetItem(aItem.parent(), aItem, 1)
            aStadItem.setText(0, aName)
            aStadItem.setIcon(0, QIcon(":/PipeCad/Resources/SCOM.png"))
            aStadItem.setToolTip(0, aDetail)
        elif aItem.type() == 2:
            aStadItem = QTreeWidgetItem(aItem, 1)
            aStadItem.setText(0, aName)
            aStadItem.setIcon(0, QIcon(":/PipeCad/Resources/SCOM.png"))
            aStadItem.setToolTip(0, aDetail)
        else:
            return
        # if

        self.tableModel.setTable("SDTE")
        self.tableModel.select()

        # Insert a dummy record.
        aRecord = self.tableModel.record()
        for i in range(aRecord.count()):
            aFieldName = aRecord.fieldName(i)
            if aFieldName == "pid":
                aRecord.setValue(aFieldName, aStadItem.parent().data(0, Qt.UserRole))
            elif aFieldName == "name":
                aRecord.setValue(aFieldName, aName)
            elif aFieldName == "detail":
                #aRecord.setValue(aFieldName, QUuid.createUuid().toString())
                aRecord.setValue(aFieldName, aDetail)
            #else:
            #    aRecord.setValue(aFieldName, 0)

        # If row is negative, the record will be appended to the end.
        self.tableModel.insertRecord(-1, aRecord)

        # Send current change signal to update table view.
        self.treeWidget.setCurrentItem(aStadItem)

    # addCategory

    def modifyCategory(self):
        aItem = self.treeWidget.currentItem()
        aCateDlg = CategoryDialog(self)
        aCateDlg.setWindowTitle(self.tr("Modify Category"))
        aCateDlg.textName.text = aItem.text(0)
        aCateDlg.textDetail.text = aItem.toolTip(0)
        if aCateDlg.exec() == QDialog.Rejected:
            return

        aNewName = aCateDlg.textName.text
        aOldName = aItem.text(0)
        if aNewName == aOldName:
            return

        if len(aNewName) < 1:
            QMessageBox.warning(self, "", "Please enter category name!")
            return

        aDetail = aCateDlg.textDetail.text

        aSql = "UPDATE SDTE SET name='" + aNewName + "', detail='" + aDetail + "' WHERE id=" + str(aItem.data(0, Qt.UserRole))
        self.database.exec(aSql)

        aItem.setText(0, aNewName)
        aItem.setToolTip(0, aDetail)

    # modifyCategory

    def deleteCategory(self):
        aItem = self.treeWidget.currentItem()
        aAnswer = QMessageBox.question(self, "", "Are you sure to delete the Category <b>" + aItem.text(0) + "</b> ?")
        if aAnswer == QMessageBox.No:
            return

        # Delete it from TreeWidget.
        aItem.parent().removeChild(aItem)

        # Delete it from Database.
        aSql = "DELETE FROM SDTE WHERE id=" + str(aItem.data(0, Qt.UserRole))
        self.database.exec(aSql)

    # deleteCategory

    def accept(self):
        if self.tableModel.rowCount() < 1:
            return

        aItem = self.treeWidget.currentItem()
        aSkey = aItem.parent().text(0)
        if aSkey == "TUBE":
            self.buildTube()
        elif aSkey == "ELBW":
            self.buildElbw()
        elif aSkey == "ELSW":
            self.buildElsw()
        elif aSkey == "TEBW":
            self.buildTebw()
        elif aSkey == "TESW":
            self.buildTesw()
        elif aSkey == "FLWN":
            self.buildFlwn()
        elif aSkey == "FLSW":
            self.buildFlsw()
        elif aSkey == "FLSO":
            self.buildFlso()
        elif aSkey == "VTFL":
            self.buildVtfl()
        elif aSkey == "VGFL":
            self.buildVgfl()
        elif aSkey == "CVFL":
            self.buildCvfl()
        elif aSkey == "VTSW":
            self.buildVtsw()
        elif aSkey == "GASK":
            self.buildGask()
        elif aSkey == "REBW":
            self.buildRebw()
        elif aSkey == "RCBW":
            self.buildRcbw()
        elif aSkey == "ESBW":
            self.buildEsbw()
        elif aSkey == "KABW":
            self.buildKabw()
        elif aSkey == "NZFL":
            self.buildNzfl()
        elif aSkey == "STEA":
            self.buildStea()
        elif aSkey == "STUA":
            self.buildStea()
        elif aSkey == "JISH":
            self.buildJish()
        elif aSkey == "JISI":
            self.buildJisi()
        elif aSkey == "JIST":
            self.buildJist()
        elif aSkey == "JISB":
            self.buildJisb()
        elif aSkey == "BULB":
            self.buildBulb()
        elif aSkey == "BOLT":
            self.buildBolt()

        QDialog.accept(self)
    # accept

    def buildTube(self):
        # print("Build TUBE")

        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard Tube Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "TUBE"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "TUBE"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOM SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "PIPE O/D"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONN TYPE"

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aOd = aRecord.field("OD").value()
            aParam = str(aDn) + " " + str(aOd) + " TUB"

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "TUBE"
            aScomItem.Param = aParam

        PipeCad.CommitTransaction()
    # buildTube

    def buildElbw(self):
        #print("Build ELBW")

        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard ELBW Components")

        try:
            PipeCad.CreateItem("CATE", aCateName)
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName)
        
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "ELBO"
        aCateItem.Description = aToolTip

        try:
            PipeCad.CreateItem("SDTE", aCateName + "-D")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-D")
        
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "ELBW"
        aSdteItem.Rtext = aToolTip

        try:
            PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-PA1")
        
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        try:
            PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-PA2")
        
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CENTRE TO FACE"

        try:
            PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-PA3")
        
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONN TYPE"

        try:
            PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-PA4")
        
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OUTSIDE DIAM"

        try:
            PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-PA5")
        
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "ANGLE"

        try:
            PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-PTSE")
        
        aPtseItem = PipeCad.CurrentItem()

        try:
            PipeCad.CreateItem("PTAX", aCateName + "-P1")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-P1")
        
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2 * math.tan(PARAM5 * math.pi / 360)"
        aPtaxItem.Axis = "-X"

        try:
            PipeCad.CreateItem("PTAX", aCateName + "-P2")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-P2")
        
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2 * math.tan(PARAM5 * math.pi / 360)"
        aPtaxItem.Axis = "X PARAM5 Y"

        PipeCad.SetCurrentItem(aPtseItem)

        hasGmse = False
        try:
            PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        except Exception as e:
            PipeCad.SetCurrentItem("/" + aCateName + "-GMSE")
            hasGmse = True
        
        aGmseItem = PipeCad.CurrentItem()

        if not(hasGmse):
            PipeCad.CreateItem("SCTO")
            aSctoItem = PipeCad.CurrentItem()
            aSctoItem.Aaxis = "P1"
            aSctoItem.Baxis = "P2"
            aSctoItem.Diameter = "PARAM4"
        
        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")
            aAngle = aRecord.field("Angle").value()

            aN = aRecord.field("DN").value()
            aD = aRecord.field("D").value()
            aA = aRecord.field("A").value()
            aC = aRecord.field("C").value()

            aParam = str(aN) + " " + str(aA) + " " + str(aC) + " " + str(aD) + " " + str(aAngle)

            try:
                PipeCad.CreateItem("SCOM", aField.value())
            except Exception as e:
                PipeCad.SetCurrentItem("/" + aField.value())
            
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "ELBO"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()
    # buildElbw

    def buildElsw(self):
        # print("build elsw")
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build ELSW")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "ELBO"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "ELSW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CENTRE TO BOTTOM OF SOCKET"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "INSERTION DEPTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "SOCKET OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "BODY DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "ANGLE"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X PARAM7 Y"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCTO")
        aSctoItem = PipeCad.CurrentItem()
        aSctoItem.Aaxis = "P1"
        aSctoItem.Baxis = "P2"
        aSctoItem.Diameter = "PARAM6"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P1"
        aScylItem.Distance = "-0.4 * PARAM4"
        aScylItem.Height = "1.4 * PARAM4"
        aScylItem.Diameter = "PARAM5"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P2"
        aScylItem.Distance = "-0.4 * PARAM4"
        aScylItem.Height = "1.4 * PARAM4"
        aScylItem.Diameter = "PARAM5"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")
            aAngle = aRecord.field("Angle").value()

            aDn = aRecord.field("DN").value()
            aCt = aRecord.field("CT").value()
            aA = aRecord.field("A").value()
            aB = aRecord.field("B").value()
            aC = aRecord.field("C").value()
            aD = aRecord.field("D").value()

            aParam = str(aDn) + " " + str(aA) + " " + str(aCt) + " " + str(aB) + " " + str(aC) + " " + str(aD) + " " + str(aAngle)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "ELBO"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()
    # buildElsw

    def buildTebw(self):
        #print("Build TEBW")

        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard TEBW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "TEE"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "TEBW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL RUN SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL BRANCH SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "RUN CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "BRANCH CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CENTRE TO RUN END"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CENTRE TO BRANCH END"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "RUN OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA8")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "BRANCH OUTSIDE DIAM"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM5"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM5"
        aPtaxItem.Axis = "X"

        PipeCad.CreateItem("PTAX", aCateName + "-P3")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 3
        aPtaxItem.Connection = "PARAM4"
        aPtaxItem.Bore = "PARAM2"
        aPtaxItem.Distance = "PARAM6"
        aPtaxItem.Axis = "Z"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "Z"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM6"
        aScylItem.Diameter = "PARAM8"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "-2 * PARAM5"
        aScylItem.Diameter = "PARAM7"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aN1 = aRecord.field("N1").value()
            aN2 = aRecord.field("N2").value()
            aD1 = aRecord.field("D1").value()
            aD2 = aRecord.field("D2").value()
            aL1 = aRecord.field("L1").value()
            aL2 = aRecord.field("L2").value()
            aC1 = aRecord.field("C1").value()
            aC2 = aRecord.field("C2").value()

            aParam = str(aN1) + " " + str(aN2) + " " + str(aC1) + " " + str(aC2) + " " + str(aL1) + " " + str(aL2) + " " + str(aD1) + " " + str(aD2)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "TEE"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()
    # buildTebw

    def buildTesw(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard TESW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "TEE"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "TESW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL RUN SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL BRANCH SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HALF RUN LAY LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "BRANCH LAY LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "BODY OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "INSERTION DEPTH"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM4"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM4"
        aPtaxItem.Axis = "X"

        PipeCad.CreateItem("PTAX", aCateName + "-P3")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 3
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM2"
        aPtaxItem.Distance = "PARAM4"
        aPtaxItem.Axis = "Z"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P3"
        aScylItem.Distance = "PARAM7"
        aScylItem.Height = "(PARAM7 + PARAM4) * -1"
        aScylItem.Diameter = "PARAM6"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "-X"
        aScylItem.Distance = "-1 * (PARAM4 + PARAM7)"
        aScylItem.Height = "2 * (PARAM4 + PARAM7)"
        aScylItem.Diameter = "PARAM6"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aN1 = aRecord.field("N1").value()
            aN2 = aRecord.field("N2").value()
            aC1 = aRecord.field("CT").value()
            aL1 = aRecord.field("L1").value()
            aL2 = aRecord.field("L2").value()
            aD1 = aRecord.field("D1").value()
            aLd = aRecord.field("LD").value()

            aParam = str(aN1) + " " + str(aN2) + " " + str(aC1) + " " + str(aL1) + " " + str(aL2) + " " + str(aD1) + " " + str(aLd)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "TEE"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()
    # buildTesw

    def buildFlwn(self):
        #print("Build FLWN")

        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard FLWN Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "FLAN"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "FLWN"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OVERALL LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FACE CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "TUBE CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE THICKNESS"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HUB SMALL DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA8")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HUB LARGE DIAM"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM4"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "-PARAM5"
        aScylItem.Diameter = "PARAM7"

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "X"
        aLsnoItem.Baxis = "Z"
        aLsnoItem.Tdistance = "PARAM2"
        aLsnoItem.Bdistance = "PARAM5"
        aLsnoItem.Tdiameter = "PARAM6"
        aLsnoItem.Bdiameter = "PARAM8"
        aLsnoItem.Offset = "0"

        PipeCad.SetCurrentItem(aGmseItem)

        # Create Bolt Set.
        aBtseItem = aGmseItem
        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)

            aBn = aRecord.field("BN").value()
            aBd = str(aRecord.field("BD").value())

            aBtseName = aCateName + "-" + str(aBn) + "-" + aBd
            try:
                PipeCad.CreateItem("BTSE", aBtseName)
                aBtseItem = PipeCad.CurrentItem()
                aBtseItem.Btype = "BOLT"
                aBtseItem.Noff = aBn
                aBtseItem.Bdiameter = aBd
                aBtseItem.Bthickness = "PARAM5"
            except Exception as e:
                continue
        # for

        PipeCad.SetCurrentItem(aBtseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aOl = aRecord.field("OL").value()
            aFt = aRecord.field("FT").value()
            aFd = aRecord.field("FD").value()
            aPd = aRecord.field("PD").value()
            aHd = aRecord.field("HD").value()
            aPc = aRecord.field("PC").value()
            aFc = aRecord.field("FC").value()

            aBn = str(aRecord.field("BN").value())
            aBd = str(aRecord.field("BD").value())

            aParam = str(aDn) + " " + str(aOl) + " " + str(aFc) + " " + str(aPc) + " " + str(aFt) + " " + str(aPd) + " " + str(aFd) + " " + str(aHd)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "FLAN"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
            aScomItem.Blref = PipeCad.GetItem("/" + aCateName + "-" + aBn + "-" + aBd)

        PipeCad.CommitTransaction()
    # buildFlwn

    def buildFlsw(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard FLSW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "FLAN"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "FLSW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "LAY LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FACE CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "TUBE CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE DIAMETER"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OVERALL THICKNESS"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE THICKNESS"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM4"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="X"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM7"
        aScylItem.Diameter = "PARAM5"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="X"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM6"
        aScylItem.Diameter = "PARAM5 * 0.65"

        PipeCad.SetCurrentItem(aGmseItem)

        # Create Bolt Set.
        aBtseItem = aGmseItem
        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)

            aBn = aRecord.field("BN").value()
            aBd = str(aRecord.field("BD").value())

            aBtseName = aCateName + "-" + str(aBn) + "-" + aBd
            try:
                PipeCad.CreateItem("BTSE", aBtseName)
                aBtseItem = PipeCad.CurrentItem()
                aBtseItem.Btype = "BOLT"
                aBtseItem.Noff = aBn
                aBtseItem.Bdiameter = aBd
                aBtseItem.Bthickness = "PARAM7"
            except Exception as e:
                continue
        # for

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aFd = aRecord.field("FD").value()
            aFt = aRecord.field("FT").value()
            aTa = aRecord.field("TA").value()
            aTl = aRecord.field("TL").value()
            aPc = aRecord.field("PC").value()
            aFc = aRecord.field("FC").value()

            aBn = str(aRecord.field("BN").value())
            aBd = str(aRecord.field("BD").value())

            aParam = str(aDn) + " " + str(aTl) + " " + str(aFc) + " " + str(aPc) + " " + str(aFd) + " " + str(aTa) + " " + str(aFt)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "FLAN"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
            aScomItem.Blref = PipeCad.GetItem("/" + aCateName + "-" + aBn + "-" + aBd)

        PipeCad.CommitTransaction()
    # buildFlsw

    def buildFlso(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard FLSO Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "FLAN"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "FLSO"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "LAY LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FACE CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "TUBE CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE DIAMETER"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OVERALL THICKNESS"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE THICKNESS"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM4"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="X"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM7"
        aScylItem.Diameter = "PARAM5"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="X"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM6"
        aScylItem.Diameter = "(PARAM1 + 15) * 1.075"

        PipeCad.SetCurrentItem(aGmseItem)

        # Create Bolt Set.
        aBtseItem = aGmseItem
        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)

            aBn = aRecord.field("BN").value()
            aBd = str(aRecord.field("BD").value())

            aBtseName = aCateName + "-" + str(aBn) + "-" + aBd
            try:
                PipeCad.CreateItem("BTSE", aBtseName)
                aBtseItem = PipeCad.CurrentItem()
                aBtseItem.Btype = "BOLT"
                aBtseItem.Noff = aBn
                aBtseItem.Bdiameter = aBd
                aBtseItem.Bthickness = "PARAM7"
            except Exception as e:
                continue
        # for

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aDa = aRecord.field("DA").value()
            aDb = aRecord.field("DB").value()
            aDc = aRecord.field("DC").value()
            aDd = aRecord.field("DD").value()
            aPc = aRecord.field("PC").value()
            aFc = aRecord.field("FC").value()

            aBn = str(aRecord.field("BN").value())
            aBd = str(aRecord.field("BD").value())

            aParam = str(aDn) + " " + str(aDa) + " " + str(aFc) + " " + str(aPc) + " " + str(aDd) + " " + str(aDb) + " " + str(aDc)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "FLAN"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
            aScomItem.Blref = PipeCad.GetItem("/" + aCateName + "-" + aBn + "-" + aBd)

        PipeCad.CommitTransaction()
    # buildFlso

    def buildVtfl(self):
        #print("Build VTFL")
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard VTFL Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "VALV"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "VTFL"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HALF FACE TO FACE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HANDWHEEL HEIGHT"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HANDWHEEL DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE THICKNESS"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.CreateItem("PTAX", aCateName + "-P3")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 3
        aPtaxItem.Connection = ""
        aPtaxItem.Bore = ""
        aPtaxItem.Distance = "PARAM4"
        aPtaxItem.Axis = "Z"

        PipeCad.CreateItem("PTCA", aCateName + "-P4")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 4
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "PARAM5 * 0.5"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.CreateItem("PTCA", aCateName + "-P5")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 5
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "PARAM5 * -0.5"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.CreateItem("PTCA", aCateName + "-P6")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 6
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "0"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "-X"

        PipeCad.CreateItem("PTCA", aCateName + "-P7")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 7
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "0"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "-PARAM7"
        aScylItem.Diameter = "PARAM6"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P2"
        aScylItem.Distance = "0"
        aScylItem.Height = "-PARAM7"
        aScylItem.Diameter = "PARAM6"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "Z"
        aScylItem.Distance = "0"
        aScylItem.Height = "0.3 * PARAM4"
        aScylItem.Diameter = "PARAM2"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P1"
        aScylItem.Distance = "-PARAM7"
        aScylItem.Height = "(PARAM2 - PARAM7) * -2"
        aScylItem.Diameter = "PARAM6 * 0.6"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "Z"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM4"
        aScylItem.Diameter = "PARAM7"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P6"
        aScylItem.Distance = "-0.5 * PARAM5"
        aScylItem.Height = "PARAM5"
        aScylItem.Diameter = "PARAM7 * 0.3"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P7"
        aScylItem.Distance = "-0.5 * PARAM5"
        aScylItem.Height = "PARAM5"
        aScylItem.Diameter = "PARAM7 * 0.3"

        PipeCad.CreateItem("SBOX")
        aSboxItem = PipeCad.CurrentItem()
        aSboxItem.Px = "0"
        aSboxItem.Py = "0"
        aSboxItem.Pz = "0.35 * PARAM4"
        aSboxItem.Pxlength = "PARAM2 * 1.3"
        aSboxItem.Pylength = "PARAM2 * 1.3"
        aSboxItem.Pzlength = "PARAM7 * 3"

        PipeCad.CreateItem("SBOX")
        aSboxItem = PipeCad.CurrentItem()
        aSboxItem.Px = "0"
        aSboxItem.Py = "0"
        aSboxItem.Pz = "0.6 * PARAM4"
        aSboxItem.Pxlength = "PARAM2 * 0.5"
        aSboxItem.Pylength = "PARAM2 * 1"
        aSboxItem.Pzlength = "PARAM4 * 0.5"

        PipeCad.CreateItem("SDSH")
        aSdshItem = PipeCad.CurrentItem()
        aSdshItem.Axis = "-Z"
        aSdshItem.Diameter = "1.3 * PARAM2"
        aSdshItem.Height = "0.5 * PARAM6"
        aSdshItem.Radius = "PARAM2"
        aSdshItem.Distance = "0"

        PipeCad.CreateItem("SCTO")
        aSctoItem = PipeCad.CurrentItem()
        aSctoItem.Aaxis = "P4"
        aSctoItem.Baxis = "P5"
        aSctoItem.Diameter = "PARAM7 * 0.5"

        PipeCad.CreateItem("SCTO")
        aSctoItem = PipeCad.CurrentItem()
        aSctoItem.Aaxis = "-P4"
        aSctoItem.Baxis = "-P5"
        aSctoItem.Diameter = "PARAM7 * 0.5"

        PipeCad.SetCurrentItem(aGmseItem)

        # Create Bolt Set.
        aBtseItem = aGmseItem
        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)

            aBn = aRecord.field("BN").value()
            aBd = str(aRecord.field("BD").value())

            aBtseName = aCateName + "-" + str(aBn) + "-" + aBd
            try:
                PipeCad.CreateItem("BTSE", aBtseName)
                aBtseItem = PipeCad.CurrentItem()
                aBtseItem.Btype = "BOLT"
                aBtseItem.Noff = aBn
                aBtseItem.Bdiameter = aBd
                aBtseItem.Bthickness = "PARAM7"
            except Exception as e:
                continue
        # for

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aA = aRecord.field("A").value()
            aB = aRecord.field("B").value()
            aC = aRecord.field("C").value() * 0.5
            aD = aRecord.field("D").value()
            aH = aRecord.field("H").value()
            aFc = aRecord.field("FC").value()

            aBn = str(aRecord.field("BN").value())
            aBd = str(aRecord.field("BD").value())

            aParam = str(aDn) + " " + str(aC) + " " + str(aFc) + " " + str(aH) + " " + str(aD) + " " + str(aA) + " " + str(aB)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "VALV"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
            aScomItem.Blref = PipeCad.GetItem("/" + aCateName + "-" + aBn + "-" + aBd)

        PipeCad.CommitTransaction()
    # buildVtfl

    def buildVgfl(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard VGFL Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "VALV"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "VGFL"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HALF FACE TO FACE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HANDWHEEL HEIGHT"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HANDWHEEL DIAMETER"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE THICKNESS"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE OUTSIDE DIAMETER"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.CreateItem("PTAX", aCateName + "-P3")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 3
        aPtaxItem.Connection = ""
        aPtaxItem.Bore = ""
        aPtaxItem.Distance = "PARAM4"
        aPtaxItem.Axis = "Z"

        PipeCad.CreateItem("PTCA", aCateName + "-P4")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 4
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "PARAM5 * 0.5"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.CreateItem("PTCA", aCateName + "-P5")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 5
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "PARAM5 * -0.5"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.CreateItem("PTCA", aCateName + "-P6")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 6
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "0"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "-X"

        PipeCad.CreateItem("PTCA", aCateName + "-P7")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 7
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "0"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "-P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM6"
        aScylItem.Diameter = "PARAM7"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "-P2"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM6"
        aScylItem.Diameter = "PARAM7"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "-P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM2 * 2"
        aScylItem.Diameter = "PARAM7 * 0.7"

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "Z"
        aLsnoItem.Baxis = "Y"
        aLsnoItem.Tdistance = "PARAM4 * 0.8"
        aLsnoItem.Bdistance = "0"
        aLsnoItem.Tdiameter = "PARAM5 * 0.15"
        aLsnoItem.Bdiameter = "PARAM2 * 1.25"
        aLsnoItem.Offset = "0"

        PipeCad.CreateItem("SDSH")
        aSdshItem = PipeCad.CurrentItem()
        aSdshItem.Axis = "-Z"
        aSdshItem.Diameter = "1.25 * PARAM2"
        aSdshItem.Height = "0.5 * PARAM7"
        aSdshItem.Radius = "0.5 * PARAM2"
        aSdshItem.Distance = "0"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "Z"
        aScylItem.Distance = "0.5 * PARAM7"
        aScylItem.Height = "1.3 * PARAM6"
        aScylItem.Diameter = "PARAM2 * 1.4"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P3"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM4 * -0.2"
        aScylItem.Diameter = "PARAM5 * 0.1"

        PipeCad.CreateItem("SCTO")
        aSctoItem = PipeCad.CurrentItem()
        aSctoItem.Aaxis = "P4"
        aSctoItem.Baxis = "P5"
        aSctoItem.Diameter = "PARAM5 * 0.075"

        PipeCad.CreateItem("SCTO")
        aSctoItem = PipeCad.CurrentItem()
        aSctoItem.Aaxis = "-P4"
        aSctoItem.Baxis = "-P5"
        aSctoItem.Diameter = "PARAM5 * 0.075"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P6"
        aScylItem.Distance = "PARAM5 * -0.5"
        aScylItem.Height = "PARAM5"
        aScylItem.Diameter = "PARAM5 * 0.05"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P7"
        aScylItem.Distance = "PARAM5 * -0.5"
        aScylItem.Height = "PARAM5"
        aScylItem.Diameter = "PARAM5 * 0.05"

        PipeCad.SetCurrentItem(aGmseItem)

        # Create Bolt Set.
        aBtseItem = aGmseItem
        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)

            aBn = aRecord.field("BN").value()
            aBd = str(aRecord.field("BD").value())

            aBtseName = aCateName + "-" + str(aBn) + "-" + aBd
            try:
                PipeCad.CreateItem("BTSE", aBtseName)
                aBtseItem = PipeCad.CurrentItem()
                aBtseItem.Btype = "BOLT"
                aBtseItem.Noff = aBn
                aBtseItem.Bdiameter = aBd
                aBtseItem.Bthickness = "PARAM6"
            except Exception as e:
                continue
        # for

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aA = aRecord.field("A").value()
            aB = aRecord.field("B").value()
            aC = aRecord.field("C").value()
            aD = aRecord.field("D").value()
            aH = aRecord.field("H").value()
            aFc = aRecord.field("FC").value()

            aBn = str(aRecord.field("BN").value())
            aBd = str(aRecord.field("BD").value())

            aParam = str(aDn) + " " + str(aC) + " " + str(aFc) + " " + str(aH) + " " + str(aD) + " " + str(aB) + " " + str(aA)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "VALV"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
            aScomItem.Blref = PipeCad.GetItem("/" + aCateName + "-" + aBn + "-" + aBd)

        PipeCad.CommitTransaction()
    # buildVgfl

    def buildCvfl(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard CVFL Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "VALV"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "CVFL"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HALF FACE TO FACE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE THICKNESS"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE DIAMETER"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.CreateItem("PTAX", aCateName + "-P3")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 3
        aPtaxItem.Connection = ""
        aPtaxItem.Bore = ""
        aPtaxItem.Distance = "DDHEIGHT"
        aPtaxItem.Axis = "Z"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "-PARAM4"
        aScylItem.Diameter = "PARAM5"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P2"
        aScylItem.Distance = "0"
        aScylItem.Height = "-PARAM4"
        aScylItem.Diameter = "PARAM5"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM2 * -2"
        aScylItem.Diameter = "PARAM5 * 0.7"

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "Z"
        aLsnoItem.Baxis = "X"
        aLsnoItem.Tdistance = "PARAM5"
        aLsnoItem.Bdistance = "0"
        aLsnoItem.Tdiameter = "DDRADIUS * 0.3"
        aLsnoItem.Bdiameter = "PARAM5 * 0.6"
        aLsnoItem.Offset = "0"

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "Z"
        aLsnoItem.Baxis = "X"
        aLsnoItem.Tdistance = "PARAM5 * 0.4"
        aLsnoItem.Bdistance = "PARAM5 * -0.4"
        aLsnoItem.Tdiameter = "PARAM5 * 0.9"
        aLsnoItem.Bdiameter = "PARAM5 * 0.2"
        aLsnoItem.Offset = "0"

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "P3"
        aLsnoItem.Baxis = "X"
        aLsnoItem.Tdistance = "DDHEIGHT * -0.05"
        aLsnoItem.Bdistance = "DDHEIGHT * -0.1"
        aLsnoItem.Tdiameter = "DDRADIUS"
        aLsnoItem.Bdiameter = "DDRADIUS * 0.5"
        aLsnoItem.Offset = "0"

        PipeCad.CreateItem("LCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "Z"
        aScylItem.Bdistance = "PARAM5 * 0.4"
        aScylItem.Tdistance = "PARAM5 * 0.6"
        aScylItem.Diameter = "PARAM5 * 0.9"

        PipeCad.CreateItem("LCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P3"
        aScylItem.Bdistance = "PARAM5 - DDHEIGHT"
        aScylItem.Tdistance = "-0.1 * DDHEIGHT"
        aScylItem.Diameter = "0.5 * DDRADIUS"

        PipeCad.CreateItem("SDSH")
        aSdshItem = PipeCad.CurrentItem()
        aSdshItem.Axis = "P3"
        aSdshItem.Diameter = "DDRADIUS"
        aSdshItem.Height = "DDHEIGHT * 0.1"
        aSdshItem.Radius = "DDRADIUS * 0.3"
        aSdshItem.Distance = "DDHEIGHT * -0.05"

        PipeCad.SetCurrentItem(aGmseItem)

        # Create Bolt Set.
        aBtseItem = aGmseItem
        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)

            aBn = aRecord.field("BN").value()
            aBd = str(aRecord.field("BD").value())

            aBtseName = aCateName + "-" + str(aBn) + "-" + aBd
            try:
                PipeCad.CreateItem("BTSE", aBtseName)
                aBtseItem = PipeCad.CurrentItem()
                aBtseItem.Btype = "BOLT"
                aBtseItem.Noff = aBn
                aBtseItem.Bdiameter = aBd
                aBtseItem.Bthickness = "PARAM4"
            except Exception as e:
                continue
        # for

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aA = aRecord.field("A").value()
            aB = aRecord.field("B").value()
            aC = aRecord.field("C").value()
            aFc = aRecord.field("FC").value()

            aBn = str(aRecord.field("BN").value())
            aBd = str(aRecord.field("BD").value())

            aParam = str(aDn) + " " + str(aA) + " " + str(aFc) + " " + str(aB) + " " + str(aC)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "VALV"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
            aScomItem.Blref = PipeCad.GetItem("/" + aCateName + "-" + aBn + "-" + aBd)
            
        PipeCad.CommitTransaction()
    # buildCvfl

    def buildVtsw(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard VTSW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "VALV"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "VTSW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HALF LAY LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HANDWHEEL HEIGHT"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "HANDWHEEL DIAMETER"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "SOCKET DEPTH"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.CreateItem("PTAX", aCateName + "-P3")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 3
        aPtaxItem.Connection = ""
        aPtaxItem.Bore = ""
        aPtaxItem.Distance = "PARAM4"
        aPtaxItem.Axis = "Z"

        PipeCad.CreateItem("PTCA", aCateName + "-P4")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 4
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "PARAM5 * 0.5"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.CreateItem("PTCA", aCateName + "-P5")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 5
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "PARAM5 * -0.5"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "Y"

        PipeCad.CreateItem("PTCA", aCateName + "-P6")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 6
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "0"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "-Y"

        PipeCad.CreateItem("PTCA", aCateName + "-P7")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 7
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Px = "0"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "PARAM4"
        aPtcaItem.Direction = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P1"
        aScylItem.Distance = "PARAM6"
        aScylItem.Height = "-2 * (PARAM2 + PARAM6)"
        aScylItem.Diameter = "PARAM1 + 30"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P3"
        aScylItem.Distance = "0"
        aScylItem.Height = "-2 * (PARAM2 + PARAM6)"
        aScylItem.Diameter = "PARAM5 * 0.1"

        PipeCad.CreateItem("SCTO")
        aSctoItem = PipeCad.CurrentItem()
        aSctoItem.Aaxis = "P4"
        aSctoItem.Baxis = "P5"
        aSctoItem.Diameter = "PARAM5 * 0.1"

        PipeCad.CreateItem("SCTO")
        aSctoItem = PipeCad.CurrentItem()
        aSctoItem.Aaxis = "-P4"
        aSctoItem.Baxis = "-P5"
        aSctoItem.Diameter = "PARAM5 * 0.1"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P6"
        aScylItem.Distance = "PARAM5 * -0.5"
        aScylItem.Height = "PARAM5"
        aScylItem.Diameter = "PARAM5 * 0.075"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis = "P7"
        aScylItem.Distance = "PARAM5 * -0.5"
        aScylItem.Height = "PARAM5"
        aScylItem.Diameter = "PARAM5 * 0.075"

        PipeCad.CreateItem("SBOX")
        aSboxItem = PipeCad.CurrentItem()
        aSboxItem.Px = "0"
        aSboxItem.Py = "0"
        aSboxItem.Pz = "0.3 * PARAM4"
        aSboxItem.Pxlength = "PARAM2 * 0.7"
        aSboxItem.Pylength = "PARAM1 * 2"
        aSboxItem.Pzlength = "PARAM4"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aA = aRecord.field("A").value()
            aB = aRecord.field("B").value()
            aD = aRecord.field("D").value()
            aH = aRecord.field("H").value()
            aFc = aRecord.field("CT").value()

            aParam = str(aDn) + " " + str(aA) + " " + str(aFc) + " " + str(aH) + " " + str(aD) + " " + str(aB)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "VALV"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
        PipeCad.CommitTransaction()
    # buildVtsw

    def buildGask(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build GASKET Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "GASK"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "GASK"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "COMPRESSED THICKNESS"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONNECTION TYPE ARRIVE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONNECTION TYPE LEAVE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OUTSIDE DIAMETER"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM4"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "-PARAM2"
        aScylItem.Diameter = "PARAM5"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aTk = aRecord.field("TK").value()
            aDm = aRecord.field("DM").value()
            aCa = aRecord.field("CA").value()
            aCl = aRecord.field("CL").value()

            aParam = str(aDn) + " " + str(aTk) + " " + str(aCa) + " " + str(aCl) + " " + str(aDm)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "GASK"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()

    # buildGask

    def buildRcbw(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build RCBW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "REDU"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "RCBW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL LARGE SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL REDUCED SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONNECTION TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OVERALL LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "LARGE OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "REDUCED OUTSIDE DIAM"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM2"
        aPtaxItem.Distance = "PARAM4"
        aPtaxItem.Axis = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "X"
        aLsnoItem.Baxis = "-Z"
        aLsnoItem.Tdistance = "PARAM4"
        aLsnoItem.Bdistance = "0"
        aLsnoItem.Tdiameter = "PARAM6"
        aLsnoItem.Bdiameter = "PARAM5"
        aLsnoItem.Offset = "0"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aNa = aRecord.field("NA").value()
            aNb = aRecord.field("NB").value()
            aDa = aRecord.field("A").value()
            aDb = aRecord.field("B").value()
            aLa = aRecord.field("L").value()

            aParam = str(aNa) + " " + str(aNb) + " BWD " + str(aLa) + " " + str(aDa) + " " + str(aDb)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "REDU"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()

    # buildRcbw

    def buildRebw(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build REBW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "REDU"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "REBW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL LARGE SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL REDUCED SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONNECTION TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OVERALL LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "LARGE OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "REDUCED OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OFFSET"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTCA", aCateName + "-P2")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 2
        aPtcaItem.Connection = "PARAM3"
        aPtcaItem.Bore = "PARAM2"
        aPtcaItem.Direction = "X"
        aPtcaItem.Px = "PARAM4"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "-PARAM7"

        PipeCad.CreateItem("PTCA", aCateName + "-P3")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 3
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Direction = "-Z"
        aPtcaItem.Px = "PARAM4"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "-PARAM7"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "X"
        aLsnoItem.Baxis = "-Z"
        aLsnoItem.Tdistance = "PARAM4"
        aLsnoItem.Bdistance = "0"
        aLsnoItem.Tdiameter = "PARAM6"
        aLsnoItem.Bdiameter = "PARAM5"
        aLsnoItem.Offset = "PARAM7"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aNa = aRecord.field("NA").value()
            aNb = aRecord.field("NB").value()
            aDa = aRecord.field("A").value()
            aDb = aRecord.field("B").value()
            aLa = aRecord.field("L").value()
            aOf = aRecord.field("F").value()

            aParam = str(aNa) + " " + str(aNb) + " BWD " + str(aLa) + " " + str(aDa) + " " + str(aDb) + " " + str(aOf)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "REDU"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()

    # buildRebw

    def buildEsbw(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build ESBW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "REDU"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "ESBW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL LARGE SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SMALL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "CONNECTION TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OVERALL LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OFFSET"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "LARGE OUTSIDE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "SMALL OUTSIDE DIAM"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTCA", aCateName + "-P2")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 2
        aPtcaItem.Connection = "PARAM3"
        aPtcaItem.Bore = "PARAM2"
        aPtcaItem.Direction = "X"
        aPtcaItem.Px = "PARAM4"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "-PARAM5"

        PipeCad.CreateItem("PTCA", aCateName + "-P3")
        aPtcaItem = PipeCad.CurrentItem()
        aPtcaItem.Number = 3
        aPtcaItem.Connection = ""
        aPtcaItem.Bore = ""
        aPtcaItem.Direction = "-Z"
        aPtcaItem.Px = "PARAM4"
        aPtcaItem.Py = "0"
        aPtcaItem.Pz = "-PARAM5"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "-0.6 * PARAM4"
        aScylItem.Diameter = "PARAM6"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="P2"
        aScylItem.Distance = "0"
        aScylItem.Height = "-0.2 * PARAM4"
        aScylItem.Diameter = "PARAM7"

        PipeCad.CreateItem("LSNO")
        aLsnoItem = PipeCad.CurrentItem()
        aLsnoItem.Aaxis = "X"
        aLsnoItem.Baxis = "-Z"
        aLsnoItem.Tdistance = "PARAM4 * 0.8"
        aLsnoItem.Bdistance = "PARAM4 * 0.6"
        aLsnoItem.Tdiameter = "PARAM7"
        aLsnoItem.Bdiameter = "PARAM6"
        aLsnoItem.Offset = "PARAM5"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aN1 = aRecord.field("N1").value()
            aN2 = aRecord.field("N2").value()
            aCt = aRecord.field("CT").value()
            aLt = aRecord.field("LT").value()
            aLo = aRecord.field("LO").value()
            aD1 = aRecord.field("D1").value()
            aD2 = aRecord.field("D2").value()

            aParam = str(aN1) + " " + str(aN2) + " " + str(aCt) + " " + str(aLt) + " " + str(aLo) + " " + str(aD1) + " " + str(aD2)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "REDU"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()
    # buildEsbw

    def buildKabw(self):
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build KABW Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "CAP"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "KABW"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL LARGE SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OVERALL LENGTH"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "MAIN CONNECTION TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "OUTLET CONNECTION TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "DIAMETER"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM3"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = "PARAM4"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "PARAM2"
        aPtaxItem.Axis = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="P1"
        aScylItem.Distance = "0"
        aScylItem.Height = "-0.5 * PARAM2"
        aScylItem.Diameter = "PARAM5"

        PipeCad.CreateItem("SDSH")
        aSdshItem = PipeCad.CurrentItem()
        aSdshItem.Axis = "P2"
        aSdshItem.Diameter = "PARAM5"
        aSdshItem.Height = "0.5 * PARAM2"
        aSdshItem.Radius = "0.3 * PARAM1"
        aSdshItem.Distance = "-0.5 * PARAM2"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aLa = aRecord.field("A").value()
            aLb = aRecord.field("B").value()

            aParam = str(aDn) + " " + str(aLa) + " BWD CLOS " + str(aLb)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "CAP"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem

        PipeCad.CommitTransaction()
    # buildKabw

    def buildNzfl(self):
        #print("Build NZFL")
        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard NZFL Components")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "NOZZ"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "NZFL"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOMINAL SIZE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FACE CONN TYPE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE DIAM"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "FLANGE THICKNESS"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "TUBE OUTSIDE DIAM"

        PipeCad.CreateItem("PTSE", aCateName + "-PTSE")
        aPtseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PTAX", aCateName + "-P1")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 1
        aPtaxItem.Connection = "PARAM2"
        aPtaxItem.Bore = "PARAM1"
        aPtaxItem.Distance = "0"
        aPtaxItem.Axis = "-X"

        PipeCad.CreateItem("PTAX", aCateName + "-P2")
        aPtaxItem = PipeCad.CurrentItem()
        aPtaxItem.Number = 2
        aPtaxItem.Connection = ""
        aPtaxItem.Bore = ""
        aPtaxItem.Distance = "DDHEIGHT"
        aPtaxItem.Axis = "X"

        PipeCad.SetCurrentItem(aPtseItem)

        PipeCad.CreateItem("GMSE", aCateName + "-GMSE")
        aGmseItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="X"
        aScylItem.Distance = "0"
        aScylItem.Height = "PARAM4"
        aScylItem.Diameter = "PARAM3"

        PipeCad.CreateItem("SCYL")
        aScylItem = PipeCad.CurrentItem()
        aScylItem.Axis ="X"
        aScylItem.Distance = "0"
        aScylItem.Height = "DDHEIGHT"
        aScylItem.Diameter = "PARAM5"

        PipeCad.SetCurrentItem(aGmseItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDn = aRecord.field("DN").value()
            aFd = aRecord.field("FD").value()
            aFt = aRecord.field("FT").value()
            aTd = aRecord.field("TD").value()
            aFc = aRecord.field("FC").value()

            aParam = str(aDn) + " " + str(aFc) + " " + str(aFd) + " " + str(aFt) + " " + str(aTd)

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "NOZZ"
            aScomItem.Param = aParam
            aScomItem.Ptref = aPtseItem
            aScomItem.Gmref = aGmseItem
            
        PipeCad.CommitTransaction()
    # buildNozz

    def buildStea(self):
        #print("build stea")
        aCateName = self.treeWidget.currentItem().text(0)

        aSectItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("STCA", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "ANG"
        aCateItem.Description = "Angle Section"

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Leg Length Y-Axis"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Leg Length X-Axis"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "X-Axis Offset"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Y-Axis Offset"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Unit Weight"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Root Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA8")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Toe Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA9")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Vertical Backmark"

        PipeCad.CreateItem("TEXT", aCateName + "-PA10")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Horizontal Backmark"

        PipeCad.CreateItem("PTSS", aCateName + "-PTSS")
        aPtssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NA"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LOA"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM3 - PARAM5"
        aPlinItem.Py = "PARAM4 - PARAM3"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAT"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAB"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "PARAM4 - PARAM3"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAL"
        aPlinItem.Plaxis = "-X"
        aPlinItem.Px = "-PARAM5"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAR"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "PARAM3 - PARAM5"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TOAY"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-PARAM5"
        aPlinItem.Py = "PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TOAX"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "-PARAM5"
        aPlinItem.Py = "PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LBOA"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-PARAM5"
        aPlinItem.Py = "PARAM4 - PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RBOA"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM3 - PARAM5"
        aPlinItem.Py = "PARAM4 - PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTTA"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "PARAM2 - PARAM5"
        aPlinItem.Py = "PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTOA"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "PARAM2 - PARAM5"
        aPlinItem.Py = "PARAM4 - PARAM3"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "HOA"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "PARAM3 - PARAM5"
        aPlinItem.Py = "PARAM4 - PARAM9"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "HBA"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM10 - PARAM5"
        aPlinItem.Py = "PARAM4 - PARAM3"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.SetCurrentItem(aPtssItem)

        PipeCad.CreateItem("GMSS", aCateName + "-GMSS")
        aGmssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SPRO")
        aSproItem = PipeCad.CurrentItem()
        aSproItem.Plaxis = "Y"

        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-PARAM5"
        aSpveItem.Py = "PARAM4 - PARAM1"

        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "PARAM3 - PARAM5"
        aSpveItem.Py = "PARAM4 - PARAM1"
        aSpveItem.Pradius = "PARAM8"

        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "PARAM3 - PARAM5"
        aSpveItem.Py = "PARAM4 - PARAM3"
        aSpveItem.Pradius = "PARAM7"

        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "PARAM2 - PARAM5"
        aSpveItem.Py = "PARAM4 - PARAM3"
        aSpveItem.Pradius = "PARAM8"

        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "PARAM2 - PARAM5"
        aSpveItem.Py = "PARAM4"

        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-PARAM5"
        aSpveItem.Py = "PARAM4"

        PipeCad.SetCurrentItem(aGmssItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aParam = []
            for i in range (3, aRecord.count()):
                aValue = aRecord.field(i).value()
                aParam.append(str(aValue))

            PipeCad.CreateItem("SPRF", aField.value())
            aSprfItem = PipeCad.CurrentItem()
            aSprfItem.Param = " ".join(aParam)
            aSprfItem.Gtype = "ANG"

    # buildStea

    def buildJish(self):
        # print("build JISH")
        aCateName = self.treeWidget.currentItem().text(0)

        aSectItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("STCA", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "BEAM"
        aCateItem.Description = "H profiles"

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Depth"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Width"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Web Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Flange Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Unit Weight"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Root Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Cross Sectional Area"

        PipeCad.CreateItem("TEXT", aCateName + "-PA8")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Depth Between Fillets"

        PipeCad.CreateItem("TEXT", aCateName + "-PA9")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Nominal Depth"

        PipeCad.CreateItem("TEXT", aCateName + "-PA10")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Nominal Width"

        PipeCad.CreateItem("TEXT", aCateName + "-PA11")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Surface Area per metre"

        PipeCad.CreateItem("TEXT", aCateName + "-PA12")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Backmark"

        PipeCad.CreateItem("PTSS", aCateName + "-PTSS")
        aPtssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TRW"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0.5 * PARAM3"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TRWB"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM3"
        aPlinItem.Py = "0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TLW"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "-0.5 * PARAM3"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TLWB"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM3"
        aPlinItem.Py = "0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LTOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "-0.5 * PARAM2"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTBS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LTBS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RBOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RBTS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "-0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BRWT"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0.5 * PARAM3"
        aPlinItem.Py = "-0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BLWT"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "-0.5 * PARAM3"
        aPlinItem.Py = "-0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BLW"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-0.5 * PARAM3"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BRW"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM3"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LBTS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "-0.5 * PARAM2"
        aPlinItem.Py = "-0.5 * (PARAM1 - 2.0 * PARAM4)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LBOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-0.5 * PARAM2"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NA"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAL"
        aPlinItem.Plaxis = "-X"
        aPlinItem.Px = "-0.5 * PARAM3"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAR"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "0.5 * PARAM3"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NARO"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NALO"
        aPlinItem.Plaxis = "-X"
        aPlinItem.Px = "-0.5 * PARAM2"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TBHL"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-0.5 * PARAM12"
        aPlinItem.Py = "0.5 * PARAM1 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TBHR"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM12"
        aPlinItem.Py = "0.5 * PARAM1 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BBHL"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "-0.5 * PARAM12"
        aPlinItem.Py = "-0.5 * PARAM1 + PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BBHR"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0.5 * PARAM12"
        aPlinItem.Py = "-0.5 * PARAM1 + PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.SetCurrentItem(aPtssItem)

        PipeCad.CreateItem("GMSS", aCateName + "-GMSS")
        aGmssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SPRO")
        aSproItem = PipeCad.CurrentItem()
        aSproItem.Plaxis = "Y"

        # 1
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM1"

        # 2
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM1"

        # 3
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM8 + PARAM6"

        # 4
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM3"
        aSpveItem.Py = "0.5 * PARAM8 + PARAM6"
        aSpveItem.Pradius = "PARAM6"

        # 5
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM3"
        aSpveItem.Py = "-0.5 * PARAM8 - PARAM6"
        aSpveItem.Pradius = "PARAM6"

        # 6
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "-0.5 * PARAM8 - PARAM6"

        # 7
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "-0.5 * PARAM1"

        # 8
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "-0.5 * PARAM1"

        # 9
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "-0.5 * PARAM8 - PARAM6"

        # 10
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM3"
        aSpveItem.Py = "-0.5 * PARAM8 - PARAM6"
        aSpveItem.Pradius = "PARAM6"

        # 11
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM3"
        aSpveItem.Py = "0.5 * PARAM8 + PARAM6"
        aSpveItem.Pradius = "PARAM6"

        # 12
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM8 + PARAM6"

        PipeCad.SetCurrentItem(aGmssItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aParam = []
            for i in range (3, aRecord.count()):
                aValue = aRecord.field(i).value()
                aParam.append(str(aValue))

            PipeCad.CreateItem("SPRF", aField.value())
            aSprfItem = PipeCad.CurrentItem()
            aSprfItem.Param = " ".join(aParam)
            aSprfItem.Gtype = "BEAM"

    # buildJish

    def buildJisi(self):
        # print("build JISI")
        aCateName = self.treeWidget.currentItem().text(0)

        aSectItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("STCA", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "JISI"
        aCateItem.Description = "I profiles"

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Depth"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Width"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Web Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Flange Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Unit Weight"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Root Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Toe Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA8")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Taper in degress"

        PipeCad.CreateItem("TEXT", aCateName + "-PA9")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Backmark"

        PipeCad.CreateItem("PTSS", aCateName + "-PTSS")
        aPtssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NA"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAL"
        aPlinItem.Plaxis = "-X"
        aPlinItem.Px = "-0.5 * PARAM3"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAR"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "0.5 * PARAM3"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LTOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "-0.5 * PARAM2"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RBOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LBOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-0.5 * PARAM2"
        aPlinItem.Py = "-0.5 * PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TBHL"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-0.5 * PARAM9"
        aPlinItem.Py = "0.5 * PARAM1 - PARAM4 + (PARAM9 * 0.5 - (PARAM2 + PARAM3) / 4) * math.tan(PARAM8 * math.pi / 180)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TBHR"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0.5 * PARAM9"
        aPlinItem.Py = "0.5 * PARAM1 - PARAM4 + (PARAM9 * 0.5 - (PARAM2 + PARAM3) / 4) * math.tan(PARAM8 * math.pi / 180)"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BBHR"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0.5 * PARAM9"
        aPlinItem.Py = "-(0.5 * PARAM1 - PARAM4 + (PARAM9 * 0.5 - (PARAM2 + PARAM3) / 4) * math.tan(PARAM8 * math.pi / 180))"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BBHL"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "-0.5 * PARAM9"
        aPlinItem.Py = "-(0.5 * PARAM1 - PARAM4 + (PARAM9 * 0.5 - (PARAM2 + PARAM3) / 4) * math.tan(PARAM8 * math.pi / 180))"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NARO"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "0.5 * PARAM2"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NALO"
        aPlinItem.Plaxis = "-X"
        aPlinItem.Px = "-0.5 * PARAM2"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.SetCurrentItem(aPtssItem)

        PipeCad.CreateItem("GMSS", aCateName + "-GMSS")
        aGmssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SPRO")
        aSproItem = PipeCad.CurrentItem()
        aSproItem.Plaxis = "Y"

        # 1
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM1"

        # 2
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM1 - PARAM4 + (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180)"
        aSpveItem.Pradius = "PARAM7"

        # 3
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM3"
        aSpveItem.Py = "0.5 * PARAM1 - PARAM4 - (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180)"
        aSpveItem.Pradius = "PARAM6"

        # 4
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM3"
        aSpveItem.Py = "-(0.5 * PARAM1 - PARAM4 - (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180))"
        aSpveItem.Pradius = "PARAM6"

        # 5
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "-(0.5 * PARAM1 - PARAM4 + (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180))"
        aSpveItem.Pradius = "PARAM7"

        # 6
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM2"
        aSpveItem.Py = "-0.5 * PARAM1"
        aSpveItem.Pradius = "0"

        # 7
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "-0.5 * PARAM1"
        aSpveItem.Pradius = "0"

        # 8
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "-(0.5 * PARAM1 - PARAM4 + (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180))"
        aSpveItem.Pradius = "PARAM7"

        # 9
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM3"
        aSpveItem.Py = "-(0.5 * PARAM1 - PARAM4 - (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180))"
        aSpveItem.Pradius = "PARAM6"

        # 10
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM3"
        aSpveItem.Py = "0.5 * PARAM1 - PARAM4 - (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180)"
        aSpveItem.Pradius = "PARAM6"

        # 11
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM1 - PARAM4 + (PARAM2 - PARAM3) / 4 * math.tan(PARAM8 * math.pi / 180)"
        aSpveItem.Pradius = "PARAM7"

        # 12
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM2"
        aSpveItem.Py = "0.5 * PARAM1"
        aSpveItem.Pradius = "0"

        PipeCad.SetCurrentItem(aGmssItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aParam = []
            for i in range (3, aRecord.count()):
                aValue = aRecord.field(i).value()
                aParam.append(str(aValue))

            PipeCad.CreateItem("SPRF", aField.value())
            aSprfItem = PipeCad.CurrentItem()
            aSprfItem.Param = " ".join(aParam)
            aSprfItem.Gtype = "JISI"


    # buildJisi

    def buildJist(self):
        # print("build JIST")
        aCateName = self.treeWidget.currentItem().text(0)

        aSectItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("STCA", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "JIST"
        aCateItem.Description = "T profiles"

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Depth"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Width"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Web Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Flange Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Distance to neutral axis"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Unit Weight"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Root Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA8")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Nominal Width"

        PipeCad.CreateItem("TEXT", aCateName + "-PA9")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Nominal Depth"

        PipeCad.CreateItem("TEXT", aCateName + "-PA10")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Original Depth"

        PipeCad.CreateItem("TEXT", aCateName + "-PA11")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Original Width"

        PipeCad.CreateItem("TEXT", aCateName + "-PA12")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Original Weight"

        PipeCad.CreateItem("TEXT", aCateName + "-PA13")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Backmark"

        PipeCad.CreateItem("PTSS", aCateName + "-PTSS")
        aPtssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "CGEO"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "0"
        aPlinItem.Py = "PARAM5 - PARAM2 * 0.5"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "PARAM5"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LTOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "PARAM1 * -0.5"
        aPlinItem.Py = "PARAM5"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LTBS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM1 * -0.5"
        aPlinItem.Py = "PARAM5 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTOS"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "PARAM1 * 0.5"
        aPlinItem.Py = "PARAM5"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTBS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM1 * 0.5"
        aPlinItem.Py = "PARAM5 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TRWB"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM3 * 0.5"
        aPlinItem.Py = "PARAM5 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TLWB"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM3 * -0.5"
        aPlinItem.Py = "PARAM5 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "BOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "PARAM5 - PARAM2"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RBOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM3 * 0.5"
        aPlinItem.Py = "PARAM5 - PARAM2"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LBOS"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM3 * -0.5"
        aPlinItem.Py = "PARAM5 - PARAM2"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NA"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TBHL"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "PARAM13 * -0.5"
        aPlinItem.Py = "PARAM5 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TBHR"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "PARAM13 * 0.5"
        aPlinItem.Py = "PARAM5 - PARAM4"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.SetCurrentItem(aPtssItem)

        PipeCad.CreateItem("GMSS", aCateName + "-GMSS")
        aGmssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SPRO")
        aSproItem = PipeCad.CurrentItem()
        aSproItem.Plaxis = "Y"

        # 1
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM1"
        aSpveItem.Py = "PARAM5"

        # 2
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM1"
        aSpveItem.Py = "PARAM5"

        # 3
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM1"
        aSpveItem.Py = "PARAM5 - PARAM4"

        # 4
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM3"
        aSpveItem.Py = "PARAM5 - PARAM4"
        aSpveItem.Pradius = "PARAM7"

        # 5
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "0.5 * PARAM3"
        aSpveItem.Py = "PARAM5 - PARAM2"

        # 6
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM3"
        aSpveItem.Py = "PARAM5 - PARAM2"

        # 7
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM3"
        aSpveItem.Py = "PARAM5 - PARAM4"
        aSpveItem.Pradius = "PARAM7"

        # 8
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-0.5 * PARAM1"
        aSpveItem.Py = "PARAM5 - PARAM4"

        PipeCad.SetCurrentItem(aGmssItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aParam = []
            for i in range (3, aRecord.count()):
                aValue = aRecord.field(i).value()
                aParam.append(str(aValue))

            PipeCad.CreateItem("SPRF", aField.value())
            aSprfItem = PipeCad.CurrentItem()
            aSprfItem.Param = " ".join(aParam)
            aSprfItem.Gtype = "JIST"

    # buildJist

    def buildJisb(self):
        # print("build JISB")
        aCateName = self.treeWidget.currentItem().text(0)
        aSectItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("STCA", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "JIST"
        aCateItem.Description = "Bulb Profiles"

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Leg Length"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Bulb Thickness"

        PipeCad.CreateItem("TEXT", aCateName + "-PA3")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Bulb Width"

        PipeCad.CreateItem("TEXT", aCateName + "-PA4")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Root Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA5")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Bulb Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA6")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Toe Radius"

        PipeCad.CreateItem("TEXT", aCateName + "-PA7")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "X Axis Offset"

        PipeCad.CreateItem("TEXT", aCateName + "-PA8")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Y Axis Offset"

        PipeCad.CreateItem("TEXT", aCateName + "-PA9")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "Taper Angle"

        PipeCad.CreateItem("PTSS", aCateName + "-PTSS")
        aPtssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "CGEO"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "(PARAM2 + PARAM3 + PARAM5) * 0.5 - math.tan(PARAM8 * math.pi / 180)"
        aPlinItem.Py = "PARAM7 - PARAM1 * 0.5"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NA"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LOA"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "PARAM2 - PARAM8"
        aPlinItem.Py = "PARAM7 - (PARAM3 + PARAM5 * (1 / math.tan(PARAM9 * 0.5 * math.pi / 180) - 1) * math.tan(PARAM9 * math.pi / 180))"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAT"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "0"
        aPlinItem.Py = "PARAM7"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAL"
        aPlinItem.Plaxis = "-X"
        aPlinItem.Px = "-PARAM8"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "NAR"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "PARAM2 - PARAM8"
        aPlinItem.Py = "0"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TOAY"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-PARAM8"
        aPlinItem.Py = "PARAM7"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "TOAX"
        aPlinItem.Plaxis = "X"
        aPlinItem.Px = "-PARAM8"
        aPlinItem.Py = "PARAM7"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "LBOA"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "-PARAM8"
        aPlinItem.Py = "PARAM7 - PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RBOA"
        aPlinItem.Plaxis = "-Y"
        aPlinItem.Px = "PARAM2 - PARAM8"
        aPlinItem.Py = "PARAM7 - PARAM1"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.CreateItem("PLIN")
        aPlinItem = PipeCad.CurrentItem()
        aPlinItem.Pkey = "RTTA"
        aPlinItem.Plaxis = "Y"
        aPlinItem.Px = "PARAM2 + PARAM3 + PARAM5 * (1 / math.tan(PARAM9 * 0.5 * math.pi / 180) - 1) - PARAM8"
        aPlinItem.Py = "PARAM7"
        aPlinItem.Dx = "0"
        aPlinItem.Dy = "0"

        PipeCad.SetCurrentItem(aPtssItem)

        PipeCad.CreateItem("GMSS", aCateName + "-GMSS")
        aGmssItem = PipeCad.CurrentItem()

        PipeCad.CreateItem("SPRO")
        aSproItem = PipeCad.CurrentItem()
        aSproItem.Plaxis = "Y"

        # 1
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-PARAM8"
        aSpveItem.Py = "PARAM7 - PARAM1"

        # 2
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "PARAM2 - PARAM8"
        aSpveItem.Py = "PARAM7 - PARAM1"

        # 3
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "PARAM2 - PARAM8"
        aSpveItem.Py = "PARAM7 - (PARAM3 + PARAM5 * (1 / math.tan(PARAM9 * 0.5 * math.pi / 180) - 1) * math.tan(PARAM9 * math.pi / 180))"
        aSpveItem.Pradius = "PARAM4"

        # 4
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "PARAM2 + PARAM3 + PARAM5 * (1 / math.tan(PARAM9 * 0.5 * math.pi / 180) - 1) - PARAM8"
        aSpveItem.Py = "PARAM7"
        aSpveItem.Pradius = "PARAM5"

        # 5
        PipeCad.CreateItem("SPVE")
        aSpveItem = PipeCad.CurrentItem()
        aSpveItem.Px = "-PARAM8"
        aSpveItem.Py = "PARAM7"
        aSpveItem.Pradius = "PARAM6"

        PipeCad.SetCurrentItem(aGmssItem)

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aParam = []
            for i in range (3, aRecord.count()):
                aValue = aRecord.field(i).value()
                aParam.append(str(aValue))

            PipeCad.CreateItem("SPRF", aField.value())
            aSprfItem = PipeCad.CurrentItem()
            aSprfItem.Param = " ".join(aParam)
            aSprfItem.Gtype = "JISB"

    # buildJisb

    def buildBulb(self):
        print("build bulb")
    # buildBulb

    def buildBolt(self):
        # print("Build BOLT")

        aCateName = self.treeWidget.currentItem().text(0)
        aToolTip = self.treeWidget.currentItem().toolTip(0)

        PipeCad.StartTransaction("Build Standard Bolt")

        PipeCad.CreateItem("CATE", aCateName)
        aCateItem = PipeCad.CurrentItem()
        aCateItem.Gtype = "BOLT"
        aCateItem.Description = aToolTip

        PipeCad.CreateItem("SDTE", aCateName + "-D")
        aSdteItem = PipeCad.CurrentItem()
        aSdteItem.Skey = "BOLT"
        aSdteItem.Rtext = aToolTip

        PipeCad.CreateItem("TEXT", aCateName + "-PA1")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "NOM BORE"

        PipeCad.CreateItem("TEXT", aCateName + "-PA2")
        aTextItem = PipeCad.CurrentItem()
        aTextItem.Stext = "UNIT"

        for r in range(self.tableModel.rowCount()):
            aRecord = self.tableModel.record(r)
            aField = aRecord.field("ItemCode")

            aDiameter = aRecord.field("Diameter").value()
            aParam = str(aDiameter) + " MM"

            PipeCad.CreateItem("SCOM", aField.value())
            aScomItem = PipeCad.CurrentItem()
            aScomItem.Gtype = "BOLT"
            aScomItem.Param = aParam

        PipeCad.CommitTransaction()
    # buildBolt
# StandardDialog

# Singleton Instance.
aStdDlg = StandardDialog(PipeCad)

def Show():
    aStdDlg.show()
# Show