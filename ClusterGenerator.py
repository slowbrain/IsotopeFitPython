# Copyright Stefan Ralser, Johannes Postler, Arntraud Bacher
# Institut für Ionenphysik und Angewandte Physik
# Universitaet Innsbruck

from tkinter import ttk
import tkinter as tk
import ITFTree
import ITFClusterLib
import os
import itertools
import numpy as np
import json
from collections import defaultdict

# ----------------------------------------
# IFC Class
# ----------------------------------------
class IFC():
    def __init__(self):
        self.molecule = {'dist':[], 'name':[]}
        self.names = []

    def addMolecule(self,dist,name):
        self.molecule['dist'].append(dist.tolist())
        self.molecule['name'].append(name)
        self.names.append(name)

    def save(self,filename):
        file = open(filename, mode='w')
        json.dump(self.molecule,file)
        file.close()

# ----------------------------------------
# Class CGEntries für die Eingabefelder
# ----------------------------------------
class CGEntries:
    def __init__(self,frame,bezeichnung,ausrichtung,zeile,spalte,startwert='',status=tk.NORMAL, span=1):
        if bezeichnung != '':
            self.text = ttk.Label(frame, text=bezeichnung)
            if ausrichtung == 'h':
                self.text.grid(column=spalte-1, row=zeile, sticky=tk.W)
            else:
                self.text.grid(column=spalte, row=zeile-1, columnspan=span, sticky=tk.W)
        self.wert = tk.StringVar()
        self.edit = ttk.Entry(frame, textvariable=self.wert,
                              justify=tk.RIGHT, state=status)
        self.wert.set(startwert)
        #Event binding falls Eingabeüberprüfung gemacht wird
        #self.edit.bind('<Return>', self.changed)
        #self.edit.bind('<Tab>', self.changed)
        self.edit.grid(column=spalte, row=zeile, columnspan=span, sticky=tk.W)

    def enable(self):
        self.edit.configure(state=tk.NORMAL)

    def disable(self):
        self.edit.configure(state=tk.DISABLED)
# ----------------------------------------
# Definitionen zum Cluster
# ----------------------------------------
class Cluster():
    def __init__(self,nlist,name,clist,mmd,th,folder):
        if '[' in nlist:
            self.elements = list(map(int,nlist.strip('[]').split(',')))
        else:
            temp = list(map(int,nlist.split(':')))
            if len(temp) > 2: #step is given
                self.elements = range(temp.pop(0),temp.pop()+1,temp.pop(0))
            else:
                self.elements = range(temp.pop(0),temp.pop()+1)
        #print(self.elements)
        self.name = name
        self.sumformula = clist
        self.mindist = mmd
        self.thresh = th
        self.multiMers = []
        distribution, elements = ITFClusterLib.parseMolecule(clist,mmd,th)
        self.multiMers.append(distribution)
        self.createMultiMers()

    def createMultiMers(self):
        d = self.multiMers[0]
        dNeu = d
        for j in range(2,self.elements[-1]+1):
            #print(j)
            dNeu = ITFClusterLib.convolute(dNeu,d)
            dNeu = ITFClusterLib.combineMasses(dNeu, self.mindist)
            dNeu = ITFClusterLib.applyThresh(dNeu, self.thresh)
            #print(dNeu)
            self.multiMers.append(dNeu)
        #print(len(self.multiMers))

# ----------------------------------------
# Definitionen zur Oberfläche CGFrame
# ----------------------------------------
class CGFrame(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        #self.geometry('600x400+20+20')
        self.protocol('WM_DELETE_WINDOW', self.close)
        # Create Menu
        mBar = tk.Menu(self)
        # Menu File
        mTree = tk.Menu(mBar, tearoff=0)
        mTree.add_command(label='Open', command=self.openIFC)
        mTree.add_command(label='Save', command=self.saveIFC)
        mBar.add_cascade(label='Tree', menu=mTree)
        mInput = tk.Menu(mBar, tearoff=0)
        mInput.add_command(label='Select Folder', command=self.selectFolder)
        mInput.add_command(label='Generate IFC', command=self.genIFCInput)
        mInput.add_command(label='Generate folder', command=self.genFolInput)
        mBar.add_cascade(label='Input', menu=mInput)
        self.config(menu=mBar)
        # Folder: row=0 col=0-1
        self.ordner=CGEntries(self,'','h',0,0,
            os.path.join(os.path.abspath(os.curdir),'molecules'),
            tk.DISABLED,span=4)
        self.ordner.edit.grid(sticky=tk.W+tk.E)
        # Cluster information: column=1-2
        self.clusterlist=CGEntries(self,'Sum Formula (e.g. C60 H2O or (C60)3(H5)','v',
            2,0,'C60 H2O CO2',tk.NORMAL,span=2)
        self.clusterlist.edit.grid(sticky=tk.W+tk.E)
        self.nlist=CGEntries(self,'n (e.g. 1:10 [0,1,5] [0,10]','v',
            4,0,'1:10 [0,2] [0,2,4]',tk.NORMAL,span=2)
        self.nlist.edit.grid(sticky=tk.W+tk.E)
        self.alt=CGEntries(self,'Alias','v',6,0)
        #self.alt.edit.grid(sticky=tk.W+tk.E)
        self.charge=CGEntries(self,'Charge','v',6,1,'1')
        #self.charge.edit.grid(sticky=tk.W+tk.E)
        self.thresh=CGEntries(self,'Threshold','v',8,0,'1e-6')
        self.mindist=CGEntries(self,'Mass accuracy','v',8,1,'1e-2')
        # TreeView
        self.clusterTree = ITFTree.Tree(self,'Cluster',1,3,8)
        self.addTree=ttk.Button(self, text='Add --> Tree',
            command=self.addToTree)
        self.addTree.grid(column=1, row=9, sticky=tk.W+tk.E)
        
    def genFolInput(self):
        Clusters, numClusters = self.genInputCommon()
        folder = self.ordner.wert.get() 
        for combi in numClusters:
            dCombi = np.zeros((1,2))
            dCombi[0,1] = 1
            filename = ''
            for j in range(len(combi)):
                mmn = Clusters[j].elements[combi[j]]
                if mmn > 0:
                    filename = filename+'['+Clusters[j].sumformula+']'
                if mmn > 1:
                    filename = filename+str(mmn)
            fname = os.path.join(folder,filename+'.txt')
            if filename == '':
                return
            if os.path.isfile(fname):
                continue
            for j in range(len(combi)):
                mmn = Clusters[j].elements[combi[j]]
                if mmn > 0:
                    dCombi = convolute(dCombi,Clusters[j].multiMers[mmn-1])
                    dCombi = combineMasses(dCombi, Clusters[j].mindist)
                    dCombi = applyThresh(dCombi, Clusters[j].thresh)                   
            #multiply charged ions: divide masses by charge
            dCombi[:,0] = dCombi[:,0]/float(self.charge.wert.get())
            # speichern
            np.savetxt(fname, dCombi, delimiter='\t', newline='\r\n')
        print('Done')

    def genIFCInput(self):
        # define options for selecting IFC-File
        # initial directory is folder displayed on screen
        selectFileOptions = dict(initialdir=self.ordner.wert.get(),
            defaultextension='.ifc',title='Save cluster data',
            filetypes=[('IsotopeFit cluster data','*.ifc')],
            initialfile='cluster.ifc')
        ifcFilename = tk.filedialog.asksaveasfilename(**selectFileOptions)
        if ifcFilename == '': # Cancel is clicked
            return
        # Loading of existing IFC-file omitted as file was deleted
        Clusters, numClusters = self.genInputCommon()
        dataIFC = IFC()
        for combi in numClusters:
            dCombi = np.zeros((1,2))
            dCombi[0,1] = 1
            molname = ''
            for j in range(len(combi)):
                mmn = Clusters[j].elements[combi[j]]
                if mmn > 0:
                    molname = molname+'['+Clusters[j].sumformula+']'
                if mmn > 1:
                    molname = molname+str(mmn)
            for j in range(len(combi)):
                mmn = Clusters[j].elements[combi[j]]
                if mmn > 0:
                    dCombi = ITFClusterLib.convolute(dCombi,Clusters[j].multiMers[mmn-1])
                    dCombi = ITFClusterLib.combineMasses(dCombi, Clusters[j].mindist)
                    dCombi = ITFClusterLib.applyThresh(dCombi, Clusters[j].thresh)                   
            #multiply charged ions: divide masses by charge
            dCombi[:,0] = dCombi[:,0]/float(self.charge.wert.get())
            # speichern in IFC
            dataIFC.addMolecule(dCombi,molname)
        # speichern der IFC Datei
        dataIFC.save(ifcFilename)
        print('Done')

    def genInputCommon(self):
        print('Generating from Input')        
        alternativ = self.alt.wert.get()
        if alternativ == '':
            alternativ = self.clusterlist.wert.get().strip('\r\n')
        clist = self.clusterlist.wert.get().strip('\r\n').split(' ')
        #print(clist)
        nlist = self.nlist.wert.get().strip('\r\n').split(' ')
        #print(nlist)
        mmd = float(self.mindist.wert.get())
        th = float(self.thresh.wert.get())
        Clusters = []
        for i in range(len(clist)):
            temp = Cluster(nlist[i],alternativ,clist[i],mmd,th,self.ordner.wert.get())
            Clusters.append(temp)
        # combine Clusters
        temp1 = []
        for c in Clusters:
            temp1.append(len(c.elements)) # z.B. 3, wenn c.elements=[0,2,4]
        #print(temp1)
        temp2 = []
        for c in temp1:
            temp2.append(list(range(c))) # z.B. [0,1,2], wenn c.elemens=[0,2,4]
        #print(temp2)
        numClusters = list(itertools.product(*temp2)) # cartesian product
        #print(numClusters)
        return Clusters, numClusters

    def saveIFC(self):
        print('Generating from Tree')
        mmd = float(self.mindist.wert.get())
        th = float(self.thresh.wert.get())
        self.nodes = defaultdict(list) # dictionary, key=iid of node
        self.goThroughNodes(mmd,th)
        self.combinedClusters = defaultdict(list) # dictionary, key=sumFormula, value = distribution
        self.combineClusters()
        print(self.combinedClusters)

    def goThroughNodes(self,mmd,th,node='Cluster'):
        root = self.clusterTree.root
        for child in self.clusterTree.baum.get_children(node): # child is an iid
            parent = self.clusterTree.baum.parent(child)
            temp = self.clusterTree.baum.item(child,'text')
            temp = temp.split('{')
            sumFormula = temp[0]
            cSize = temp[1].strip('}')
            alt = temp[2].strip('}')
            #self.simpFormula = ITFClusterLib.parseFormula(sumFormula)
            #print(self.simpFormula)
            knoten = ITFTree.Node(root,parent,child,sumFormula,
                cSize,mmd,th,alt)
            self.nodes[child] = knoten            
            self.goThroughNodes(mmd,th,child)
        
    def combineClusters(self,startwert='',node='Cluster'):
        #combine clusters
        #create lists for cartesian product
        if self.clusterTree.baum.get_children(node) == ():
            #am Ende eines Astes
            #print(startwert)
            elements = ITFClusterLib.parseFormula(startwert)
            #print(elements)
            oneString = ITFClusterLib.oneString(elements)
            #print(oneString)
            if oneString in self.combinedClusters.keys():
                print('Cluster already in list')
            else:
                #create cluster
                knoten = self.nodes[node]
                temp = knoten.createClusters(elements)
                self.combinedClusters[oneString] = temp
            return
        for child in self.clusterTree.baum.get_children(node):
            knoten = self.nodes[child]
            #startwert = 
            for j in knoten.elements:
                #print(j)
                if j > 1:
                    self.combineClusters(startwert+'['+
                        knoten.sumFormula+']'+str(j),child)
                elif j == 1:
                    self.combineClusters(startwert+'['+knoten.sumFormula+']',child)
                else:
                    self.combineClusters(startwert,child)
        

    def addToTree(self):
        #print(self.addTree.cget('text'))
        if self.addTree.cget('text') == 'Update Node':
            self.clusterTree.updateNode(self)
        else:
            self.clusterTree.addNode(self)


    # Schließen des Fenster
    def close(self):
        print('Window closed')
        self.destroy()

    def openIFC(self):
        pass
        #function open_file(hObject,~)
        #%%
        #handles=guidata(Parent);
        # 
        #[filename, pathname, ~] = uigetfile( ...
        #        {'*.icg','IsotopeFit molecule data (*.icg)'},...
        #        'Load IsotopeFit cluster generator file','');
        # 
        #if ~(isequal(filename,0) || isequal(pathname,0))
        #    handles.roothandle.removeAllChildren()
        #    data=[];
        #    load(fullfile(pathname,filename),'-mat');
        #    struct2tree(handles.roothandle,data);
        #    mtree.reloadNode(handles.roothandle);
        #    drawnow;
        #end
        #guidata(Parent,handles); 
        #end

    def selectFolder(self):
        # define options for selecting folder
        # initial directory is current directory
        selectFolderOptions = dict(initialdir=os.path.abspath(os.curdir),
            parent=self,title='Choose directory')
        folder = tk.filedialog.askdirectory(**selectFolderOptions)
        self.ordner.wert.set(folder)

# ----------------------------------------
# Hauptroutine
# ----------------------------------------
if __name__ == '__main__':
    # Endlosschleife
    mainf = CGFrame()
    mainf.title('Cluster Generator')
    mainf.mainloop()
