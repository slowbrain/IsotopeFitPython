# Copyright Stefan Ralser, Johannes Postler, Arntraud Bacher
# Institut für Ionenphysik und Angewandte Physik
# Universitaet Innsbruck

# Class for treeview

from tkinter import ttk
import tkinter as tk
import ITFClusterLib
import ITFEntries

# ----------------------------------------
# Class ITFTree.Tree() für den Baum
# ----------------------------------------
class Tree:
    def __init__(self,frame,bezeichnung,zeile,spalte,span=1):
        self.parentFrame = frame
        self.baum = ttk.Treeview(frame,selectmode='browse',show='tree')
        self.baum.insert('',0,iid='Cluster',text=bezeichnung+'{1e-6}{1e-2}',tags='cNode',open=True)
        self.iidSel = self.baum.identify_row(1) #get iid of selected node, 0..header, 1..root
        self.root = self.iidSel
        self.baum.selection_set(self.iidSel)
        # nur für Programmierzwecke - BEGINN
        self.baum.insert('Cluster',0,iid='I001',text='C60{1:10}{}{1}',open=True,tags='cNode')
        self.baum.insert('I001',0,iid='I002',text='H2{0:2:10}{}',open=True,tags='cNode')
        self.baum.insert('Cluster',1,iid='I003',text='(CO2)3O2{1:2}{}{1}',open=True,tags='cNode')
        # nur für Programmierzwecke - ENDE
        self.baum.tag_bind('cNode',sequence='<Button-1>',callback=self.nodeSelected)
        self.baum.tag_bind('cNode',sequence='<Button-3>',callback=self.nodeSelected)
        ysb = ttk.Scrollbar(frame,orient=tk.VERTICAL, command=self.baum.yview)
        xsb = ttk.Scrollbar(frame,orient=tk.HORIZONTAL, command=self.baum.xview)
        self.baum['yscroll']=ysb.set
        self.baum['xscroll']=xsb.set
        self.baum.grid(column=spalte, row=zeile, rowspan=span,
            sticky=tk.N+tk.S+tk.E+tk.W)
        ysb.grid(row=zeile, column=spalte+1, rowspan=span, sticky=tk.N+tk.S)
        xsb.grid(row=zeile+span, column=spalte, sticky=tk.W+tk.E)
        # create a popup menu
        self.cMenu = tk.Menu(frame,tearoff=0)
        self.cMenu.add_command(label='Add child', command=self.addNode)
        self.cMenu.add_command(label='Edit', command=self.editNode)
        self.cMenu.add_separator()
        self.cMenu.add_command(label='Remove', command=self.removeNode)
        self.cMenu.add_command(label='Copy node', command=self.copyNode)
        #self.cMenu.add_command(label='Copy subtree', command=self.copySubtree)
        self.cMenu.add_command(label='Paste', command=self.pasteNode)
        self.clipboard = [] # text of copied node
        
    def nodeSelected(self,event):
        self.iidSel = self.baum.identify_row(event.y) # get iid of selected node
        #print(self.iidSel)
        if self.iidSel:
            self.baum.selection_set(self.iidSel)
            if event.num == 3: # only on right-click
                #select and display context menu
                # if clipboard is empty -> can't copy
                if self.clipboard == []:
                    self.cMenu.entryconfigure(5,state=tk.DISABLED)
                else:
                    self.cMenu.entryconfigure(5,state=tk.NORMAL)
                if self.iidSel == 'Cluster': # if root
                    self.cMenu.entryconfigure(3,state=tk.DISABLED)
                    self.cMenu.entryconfigure(4,state=tk.DISABLED)
                else:
                    self.cMenu.entryconfigure(3,state=tk.NORMAL)
                    self.cMenu.entryconfigure(4,state=tk.NORMAL)
                self.cMenu.post(event.x_root, event.y_root)

    def addNode(self):
        #print(self.iidSel)
        NodeDialog(self.parentFrame,self.baum,self.iidSel,'ADD')

    def editNode(self):
        #print(self.iidSel)
        NodeDialog(self.parentFrame,self.baum,self.iidSel,'EDIT')

    def removeNode(self):
        self.baum.delete(self.iidSel)        

    def copyNode(self):
        self.clipboard = self.baum.item(self.iidSel,'text')
        
    def pasteNode(self):
        self.baum.insert(self.iidSel,'end',text=self.clipboard)

# ----------------------------------------
# Eigene Dialogbox
# ----------------------------------------            
class NodeDialog():
    def __init__(self, mainf, baum, iidSel, mode):
        self.baum = baum
        self.iidSel = iidSel
        self.mode = mode
        self.dialogBox = tk.Toplevel()
        if mode == 'ADD':
            titel = 'Add Node '+iidSel
        else:
            titel = 'Edit Node '+iidSel
        self.dialogBox.title(titel)
        temp = baum.item(iidSel,'text')
        temp = temp.split('{')
        self.entries = {}
        if iidSel == 'Cluster' and mode == 'EDIT': #root
            #Thresh
            #th = temp[1].strip('}')
            self.entries['thresh'] = ITFEntries.ITFEntries(self.dialogBox, 'Threshold', 'h', 0, 1,
                temp[1].strip('}'))
            #Mindist
            #mmd = temp[2].strip('}')
            self.entries['mmd'] = ITFEntries.ITFEntries(self.dialogBox, 'Min Mass Dist', 'h', 1, 1,
                temp[2].strip('}'))
        else:
            if mode == 'ADD':
                #Strukturformel
                self.entries['struct'] = ITFEntries.ITFEntries(self.dialogBox, 'Structure', 'h', 0, 1,
                    'C60')
                #Clustersize
                self.entries['cSize'] = ITFEntries.ITFEntries(self.dialogBox, 'ClusterSize', 'h', 1, 1,
                    'e.g.: 1:10 [0,2] [0,2,4]')
                #Alias
                self.entries['alt'] = ITFEntries.ITFEntries(self.dialogBox, 'Alias', 'h', 2, 1,
                    '')
            else:
                #Strukturformel
                #formel = temp[0]
                self.entries['struct'] = ITFEntries.ITFEntries(self.dialogBox, 'Structure', 'h', 0, 1,
                    temp[0])
                #Clustersize
                #cSize = temp[1].strip('}')
                self.entries['cSize'] = ITFEntries.ITFEntries(self.dialogBox, 'ClusterSize', 'h', 1, 1,
                    temp[1].strip('}'))
                #Alias
                #alt = temp[2].strip('}')
                self.entries['alt'] = ITFEntries.ITFEntries(self.dialogBox, 'Alias', 'h', 2, 1,
                    temp[2].strip('}'))               
            if iidSel == 'Cluster' and mode == 'ADD': #aeusserste Knoten
                #Charge
                self.entries['charge'] = ITFEntries.ITFEntries(self.dialogBox, 'Charge', 'h', 3, 1,
                    '1')
            if baum.parent(iidSel) == 'Cluster' and mode == 'EDIT': #aeusserste Knoten
                #Charge
                #charge = temp[3].strip('}')
                self.entries['charge'] = ITFEntries.ITFEntries(self.dialogBox, 'Charge', 'h', 3, 1,
                    temp[3].strip('}'))
        ttk.Button(self.dialogBox, text='OK', command=self.OkButton).grid(row=4, column=0)
        ttk.Button(self.dialogBox, text='Cancel', command=self.CancelButton).grid(row=4, column=1)
        # next three lines needed to make dialog box modal
        self.dialogBox.transient(mainf)
        self.dialogBox.grab_set()
        mainf.wait_window(self.dialogBox)             

    def OkButton(self):
        if self.baum.parent(self.iidSel) == '' and self.mode == 'EDIT': # root
            thresh = self.entries['thresh'].wert.get().strip('\r\n')
            mmd = self.entries['mmd'].wert.get().strip('\r\n')
            temp = 'Cluster{'+thresh+'}{'+mmd+'}'
        else:
            clist = self.entries['struct'].wert.get().strip('\r\n')
            nlist = self.entries['cSize'].wert.get().strip('\r\n')
            alt = self.entries['alt'].wert.get().strip('\r\n')
            if (self.baum.parent(self.iidSel) == '' and self.mode == 'ADD') or (self.baum.parent(self.iidSel) == 'Cluster' and self.mode == 'EDIT'): #aeusserste Knoten
                charge = self.entries['charge'].wert.get().strip('\r\n')
                temp = clist+'{'+nlist+'}{'+alt+'}{'+charge+'}'
            else:
                temp = clist+'{'+nlist+'}{'+alt+'}'
        if self.mode == 'ADD':
            self.baum.insert(self.iidSel,'end',text=temp,
                open=True,tags='cNode')
        else:
            self.baum.item(self.iidSel,text=temp)
        self.dialogBox.destroy()

    def CancelButton(self):
        self.dialogBox.destroy()

# ----------------------------------------
# Class ITFTree.Node() für einen Ast
# ----------------------------------------
class Node:
    def __init__(self,root,parent,iid,sumFormula,cSize,mmd,th,name=''):
        self.root = root
        self.parent = parent
        self.iid = iid
        self.sumFormula = sumFormula
        self.mmd = mmd
        self.th = th
        if '[' in cSize:
            self.elements = list(map(int,cSize.strip('[]').split(',')))
        else:
            temp = list(map(int,cSize.split(':')))
            if len(temp) > 2: #step is given
                self.elements = range(temp.pop(0),temp.pop()+1,temp.pop(0))
            else:
                self.elements = range(temp.pop(0),temp.pop()+1)
        #print(self.elements)        
        if name == '':
            self.name = sumFormula
        else:
            self.name = name

    def createClusters(self,elements):
        # create Cluster from elements dictionary
        distributions = []
        for key in elements.keys():
            d = ITFClusterLib.loadAtomicDist(key)
            n = elements[key]
            temp = ITFClusterLib.selfConvolute(d,n,self.mmd,self.th)
            distributions.append(temp)
        # combine distributions
        dFinal = distributions[0]
        for mols in range(len(distributions)-1):
            dFinal = ITFClusterLib.convolute(dFinal,distributions[mols+1])
            dFinal = ITFClusterLib.combineMasses(dFinal, self.mmd)
            dFinal = ITFClusterLib.applyThresh(dFinal, self.th)
        return dFinal


