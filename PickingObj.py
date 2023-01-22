from Route import Route
import numpy as np
from itertools import combinations
from Tools import Tools
import pandas as pd
import openpyxl

class PickingObj:
    def __init__(self,
        aisles_x,
        layoutFileDir='layout.csv',
        bondAisles_x=[145.5, 265.5],
        ifCorrectPosKeys=True
    ):
        self.Route = Route(aisles_x, layoutFileDir)
        self.positions = self.Route.palletPos.locDict
        self.aisles_x = aisles_x
        self.bondAisles_x = bondAisles_x

        self.posKeys = np.array(list(self.positions.keys()))
        if ifCorrectPosKeys:
            self._correctPosKeys()
        self.posValues = np.array(list(self.positions.values()))

        # Update through self.getPosClass()
        self.posCls = np.zeros(len(self.posKeys))
        self.posClsDict = {}
        # Update through self.getPairDistance()
        self.posPairs = []
        # Update through self.getSKUPosDict()
        self.SKUPosDict = {}

    def _correctPosKeys(self):
        self.posKeys = self.posKeys.astype('U25') # Enlarge the dtype of array to make it long enough to store long names
        for i in range(len(self.posKeys)):
            self.posKeys[i] = Tools.correctPosName(self.posKeys[i])
        Pos_temp = self.positions.copy()
        self.positions = {}
        for key in Pos_temp:
            self.positions[Tools.correctPosName(key)] = Pos_temp[key]

    def getSKUPosDict(self, fileDir):
        '''
        Read from .csv file with the format:
        |Location   |New Item      |
        |-----------|--------------|
        |801-01-A-01|36241-77617-03|

        Create a dictionay as:
        SKUPosDict['New Item'] = 'Location'
        '''
        df = pd.read_csv(fileDir)
        for index, row in df.iterrows():
            self.SKUPosDict[str(row[1])] = Tools.correctPosName(row[0])

    def getPosClass(self):

        for cls in range(len(self.bondAisles_x)):
            self.posCls[self.posValues[:,0] > self.bondAisles_x[cls]] = cls + 1
        for i in range(len(self.posCls)):
            self.posClsDict[self.posKeys[i]] = int(self.posCls[i])

    def getPairDistance(self, if_saveToExcel=False, outputFileDir="Pair_Distance.xlsx"):
        """
        Calculate the route distance between each pair of pallet positions
        :return: create and save into a .xlsx file
        """
        ybot = np.min(self.posValues[:,-1])
        ytop = np.max(self.posValues[:,-1])
        ymid = (ybot+ytop)/2

        for cls in range(len(self.aisles_x) + 1):
            keys = self.posKeys[self.posCls == cls]
            combs = combinations(keys, 2)
            pairs = []
            for comb in combs:
                p1 = self.positions[comb[0]]
                p2 = self.positions[comb[1]]
                if (p1[1] == ymid or p2[1] == ymid) and (p1[1] != p2[1]):
                    if p2[1] == ymid:
                        p1, p2 = p2, p1
                    for forkLoc in [0,1]:
                        rt, id = self.Route.getRoute(p1,p2,ybot,ytop,forkLoc)
                        pairs.append([list(comb), forkLoc, self.Route.calculateRoute(np.array(rt))])
                else:
                    rt, id = self.Route.getRoute(p1,p2,ybot,ytop)
                    pairs.append([list(comb), -1, self.Route.calculateRoute(np.array(rt))])
            self.posPairs.append(pairs)

        if if_saveToExcel:
            writer = pd.ExcelWriter(outputFileDir)
            for i in range(len(self.posPairs)):
                df = pd.DataFrame(self.posPairs[i])
                df.to_excel(writer, "Region_"+str(i))
            writer.save()

if __name__ == '__main__':
    print(Tools.xor(1,0))
    # pkl = PickingLogic()
    # pkl.getPosClass()
    # pkl.getPairDistance()
    # print(pkl.posPairs)