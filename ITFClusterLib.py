# Copyright Stefan Ralser, Johannes Postler, Arntraud Bacher
# Institut für Ionenphysik und Angewandte Physik
# Universitaet Innsbruck

# Lib for Cluster calculations

import string
import numpy as np
import os

def parseFormula(mol):
    #parses the molecule string (mol) and returns
    #a dictionary with each element as key and the
    #number of each element as value
    i = 0
    l = len(mol)
    elements = {}
    charge = '-1'
    while i<l:
        if mol[i] in string.digits: # i is digit? -> charge
            startpos = i
            i = i+1
            while i<l and (mol[i] in string.digits):
                i = i+1
            charge = mol[startpos:i]
        elif mol[i] in string.ascii_uppercase: #i is uppercase?
            startpos = i
            i = i+1
            while i<l and (mol[i] in string.ascii_lowercase):
                i = i+1
            molName = mol[startpos:i]
            startpos = i
            while i<l and (mol[i] in string.digits):
                i = i+1
            if startpos == i: # no number found
                n = 1
            else:
                n = int(mol[startpos:i])
            if molName in elements.keys():
                # element already in dictionary
                temp = elements[molName]
                elements[molName] = temp + n
            else:
                elements[molName] = n
        elif mol[i] == '(': # starts with a bracket
            #print('Index of brackets')
            ix = mol.find(')',i+1) # find closing bracket
            #print(ix)
            ix2 = mol.find('(',i+1) # find next opening bracket
            #print(ix2)
            while (ix2 > 0) and (ix2 < ix): # Doppelklammer
                ix = mol.find(')',ix+1) #search for next closing bracket
                #print(ix)
                ix2 = mol.find('(',ix2+1) #search for next opening bracket
                #print(ix2)
            #i index of first opening bracket
            molName = mol[i+1:ix]
            i = ix+1
            startpos = i
            while i<l and (mol[i] in string.digits): # if digit is after molName
                i = i+1
            if startpos == i: # no number found
                n = 1
            else:
                n = int(mol[startpos:i])
            #print(n)
            temp, notused = parseFormula(molName)
            #compare temp with elements
            for temp1 in temp.keys():
                if temp1 in elements.keys():
                    valTemp = temp[temp1]
                    valElem = elements[temp1] + valTemp * n
                else:
                    valTemp = temp[temp1]
                    elements[temp1] = valTemp * n
        elif mol[i] == '[': # starts with [
            ix = mol.find(']',i+1) # find closing bracket
            molName = mol[i+1:ix] # no nested [ ]
            i = ix+1
            startpos = i
            while i<l and (mol[i] in string.digits): # if digit is after [molName]
                i = i+1
            if startpos == i: # no number found
                n = 1
            else:
                n = int(mol[startpos:i])
            temp, notused = parseFormula(molName)
            #compare temp with elements
            for temp1 in temp.keys():
                if temp1 in elements.keys():
                    valTemp = temp[temp1]
                    valElem = elements[temp1] + valTemp * n
                else:
                    valTemp = temp[temp1]
                    elements[temp1] = valTemp * n                    
    #print(elements)
    return elements, charge

def oneString(elements,charge):
    #print elements as one string
    oneStr=charge
    for atom in sorted(elements):
        oneStr = oneStr+atom+str(elements[atom])
    return oneStr

def parseMolecule(mol,mmd,th):
    #parses the molecule string (mol) and returns
    #the distribution, e.g. C60
    distributions = []
    i = 0
    l = len(mol)
    print(mol)
    elements = {}
    while i<l:
        #print('Molecule to parse:'+mol)
        if mol[i] in string.ascii_uppercase: #i is uppercase?
            startpos = i
            i = i+1
            while i<l and (mol[i] in string.ascii_lowercase):
                i = i+1
            molName = mol[startpos:i] # startpos <= molName < i
            startpos = i
            while i<l and (mol[i] in string.digits):
                i = i+1
            if startpos == i: # no number found
                n = 1
            else:
                n = int(mol[startpos:i])
            if molName in elements:
                # Element molName bereits vorhanden
                print(molName+' bereits vorhanden!')
            else:
                elements[molName] = n
            d = loadAtomicDist(molName)
            temp = selfConvolute(d,n,mmd,th)
            distributions.append(temp)
        elif mol[i] == '(': # starts with a bracket
            #print('Index of brackets')
            ix = mol.find(')') # find closing bracket
            #print(ix)
            ix2 = mol.find('(',i+1) # find next opening bracket
            #print(ix2)
            while (ix2 > 0) and (ix2 < ix): # Doppelklammer
                ix = mol.find(')',ix+1) #search for next closing bracket
                #print(ix)
                ix2 = mol.find('(',ix2+1) #search for next opening bracket
                #print(ix2)
            #i index of first opening bracket
            molName = mol[i+1:ix]
            i = ix+1
            startpos = i
            while i<l and (mol[i] in string.digits): # if digit is after molName
                i = i+1
            if startpos == i: # no number found
                n = 1
            else:
                n = int(mol[startpos:i])
            #print(n)
            temp = selfConvolute(parseMolecule(molName,mmd,th),n,mmd,th)
            distributions.append(temp)
            
        dFinal = distributions[0]
        for mols in range(len(distributions)-1):
            dFinal = convolute(dFinal,distributions[mols+1])
            dFinal = combineMasses(dFinal, mmd)
            dFinal = applyThresh(dFinal, th)
    #print(dFinal)            
    return dFinal, elements

def loadAtomicDist(molName):
    #Loads atomic distribution from file
    file = os.path.join(os.path.abspath(os.curdir),*['Atoms',molName+'.txt'])
    d = np.loadtxt(file)
    d[:,1] = d[:,1]/d.sum(axis=0)[1] # renorm
    return d

def selfConvolute(d,n,mmd,th):
    #d... Distribution 2D-array, e.g. of C
    #n... Cluster Size, e.g. 60
    #dFinal.. Distribution 2D-array, e.g. C60
    dFinal = d
    for i in range(1,n):
        dFinal = convolute(dFinal,d)
        dFinal = combineMasses(dFinal, mmd)
        dFinal = applyThresh(dFinal, th)
    return dFinal

def convolute(m1,m2):
    # Convolution of m1 and m2
    # e.g. m1 = [12, 1; 13, 2], m2 = [10, 3; 11, 4]
    # -> result = [12+10,1*3; 12+11,1*4; 13+10,2*3; 13+11, 2*4]
    a1 = np.repeat(m1[:,0],m2.shape[0])
    a2 = np.tile(m2[:,0],m1.shape[0])
    a3 = np.repeat(m1[:,1],m2.shape[0])
    a4 = np.tile(m2[:,1],m1.shape[0])
    return np.column_stack(((a1+a2),(a3*a4)))

def combineMasses(dFinal,minDist):
    ix = np.argsort(dFinal[:,0])
    dSorted = dFinal[ix,:]
    massDiff = np.diff(dSorted[:,0])
    ix = np.argmin(massDiff)
    minDiff = massDiff[ix]
    while minDiff <= minDist:
        # combine peaks
        # sum 2nd column
        pSum = dSorted[ix,1] + dSorted[ix+1,1]
        # weighted Mass
        pMassW = ((dSorted[ix,0]*dSorted[ix,1])+(dSorted[ix+1,0]*dSorted[ix+1,1]))/pSum
        dSorted[ix,:] = np.array([pMassW, pSum])
        dSorted = np.delete(dSorted,ix+1,0)
        massDiff = np.delete(massDiff,ix,0)
        ix = np.argmin(massDiff)
        minDiff = massDiff[ix]
    return dSorted

def applyThresh(dFinal,thresh):
    ix = (dFinal[:,1]>=thresh*np.max(dFinal[:,1])).nonzero()
    return dFinal[ix]

