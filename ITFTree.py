# Copyright Stefan Ralser, Johannes Postler, Arntraud Bacher
# Institut für Ionenphysik und Angewandte Physik
# Universitaet Innsbruck

# Class for treeview

from tkinter import ttk
import tkinter as tk
import ITFClusterLib

# ----------------------------------------
# Class ITFTree.Tree() für den Baum
# ----------------------------------------
class Tree:
    def __init__(self,frame,bezeichnung,zeile,spalte,span=1):
        self.parent = frame
        self.baum = ttk.Treeview(frame,selectmode='browse',show='tree')
        self.baum.insert('',0,iid='Cluster',text=bezeichnung,tags='cNode',open=True)
        self.iidSel = self.baum.identify_row(1) #get iid of selected node, 0..header, 1..root
        self.root = self.iidSel
        self.baum.selection_set(self.iidSel)
        # nur für Programmierzwecke - BEGINN
        self.baum.insert('Cluster',0,iid='I001',text='C60{1:10}{}',open=True,tags='cNode')
        self.baum.insert('I001',0,iid='I002',text='H2{0:2:10}{}',open=True,tags='cNode')
        self.baum.insert('Cluster',1,iid='I003',text='(CO2)3O2{1:2}{}',open=True,tags='cNode')
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
        self.cMenu.add_command(label='Edit', command=self.editNode)
        self.cMenu.add_separator()
        self.cMenu.add_command(label='Remove', command=self.removeNode)
        self.cMenu.add_command(label='Copy node', command=self.copyNode)
        self.cMenu.add_command(label='Copy subtree', command=self.copySubtree)
        self.cMenu.add_command(label='Paste', command=self.pasteNode)
        # variables of class and initialize to empty list   
        self.clipboard = [] # should be a sequence of iids
        #self.minDist = float(self.parent.mindist.wert.get()) (?)
        #thresh (?)
        #charge (?)
        

    def nodeSelected(self,event):
        if self.parent.addTree.cget('text')=='Update Node':
            #tree in update mode
            tk.messagebox.showwarning('Updating node!','Please finish updating thenode!')
            return
        self.iidSel = self.baum.identify_row(event.y) # get iid of selected node
        #print(self.iidSel)
        if self.iidSel:
            self.baum.selection_set(self.iidSel)
            if self.iidSel == 'Cluster': # if root
                self.parent.charge.enable()
                self.parent.thresh.enable()
                self.parent.mindist.enable()
            else:
                self.parent.charge.disable()
                self.parent.thresh.disable()
                self.parent.mindist.disable()
            if event.num == 3: # only on right-click
                # if clipboard is empty -> can't copy
                if self.clipboard == []:
                    self.cMenu.entryconfigure(5,state=tk.DISABLED)
                else:
                    self.cMenu.entryconfigure(5,state=tk.NORMAL)
                #select and display context menu
                if self.iidSel == 'Cluster': # if root
                    self.cMenu.entryconfigure(0,state=tk.DISABLED)
                    self.cMenu.entryconfigure(2,state=tk.DISABLED)
                    self.cMenu.entryconfigure(3,state=tk.DISABLED)
                else:
                    self.cMenu.entryconfigure(0,state=tk.NORMAL)
                    self.cMenu.entryconfigure(2,state=tk.NORMAL)
                    self.cMenu.entryconfigure(3,state=tk.NORMAL)
                self.cMenu.post(event.x_root, event.y_root)

    def addNode(self,werte):
        #print(self.iidSel)
        if self.iidSel:
            clist = werte.clusterlist.wert.get().strip('\r\n')
            nlist = werte.nlist.wert.get().strip('\r\n')
            alt = werte.alt.wert.get().strip('\r\n')
            self.baum.insert(self.iidSel,0,text=clist+'{'+nlist+'}'+'{'+alt+'}',
            open=True,tags='cNode')
        else:
            # no node selected
            tk.messagebox.showwarning('No node/root selected','Please select a node!')

    def updateNode(self,werte):
        clist = werte.clusterlist.wert.get().strip('\r\n')
        nlist = werte.nlist.wert.get().strip('\r\n')
        alt = werte.alt.wert.get().strip('\r\n')
        self.baum.item(self.iidSel,text=clist+'{'+nlist+'}'+'{'+alt+'}')
        self.parent.addTree.configure(text='Add --> Tree')
        
    def editNode(self):
        # paste clist, nlist and alt
        # text = clist{nlist}{alt}
        temp = self.baum.item(self.iidSel,'text')
        temp = temp.split('{')
        self.parent.clusterlist.wert.set(temp[0])
        self.parent.nlist.wert.set(temp[1].strip('}'))
        self.parent.alt.wert.set(temp[2].strip('}'))
        self.parent.addTree.configure(text='Update Node')
    
    def removeNode(self):
        self.baum.delete(self.iidSel)

    def copyNode(self):
        #self.clipboard = self.baum.item(self.iidSel)
        pass

    def copySubtree(self):
        if self.iidSel == 'Cluster':
            #root selected
            tk.messagebox.showwarning('Root selected','Please select a node!')
        else:
            #self.clipboard = self.baum.get_children(self.iidSel)
            pass

    def pasteNode(self):
        #self.baum.set_children(self.iidSel, self.clipboard)
        pass

    def saveTree(self):
        #save tree as .icg-file
        #menu needed!
        pass

    def openTree(self):
        #open tree from .icg-file
        #menu needed!
        pass

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

        #        #multiply charged ions: divide masses by charge
        #        dCombi[:,0] = dCombi[:,0]/float(self.charge.wert.get())
        #        # speichern
        #        folder = self.ordner.wert.get()
        #        fname = os.path.join(folder,filename+'.txt')
        #        np.savetxt(fname, dCombi, delimiter='\t', newline='\r\n')
        #print('Done')

