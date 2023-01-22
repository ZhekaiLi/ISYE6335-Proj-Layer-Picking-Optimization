import pandas as pd
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import seaborn
from Tools import Tools

class PalletPos:
    def __init__(self):
        self.locDict = {}    # locDict[PosName] = [x,y]
        self.freqDict = {}   # freqDict[PosName] = #freq
        self.SKULocDict = {} # SKULocDict[SKU] = PosName


    def ReadSKUPositionFromCSV(self, file=None):
        # The .csv file should contain the SKU(item) number and the name of the position where it stored
        # SKU | PosName
        # --------|--------
        # SKU1   | name1
        # SKU2   | name2
        df = pd.read_csv(file)
        for index, row in df.iterrows():
            self.SKULocDict[str(row[1])] = row[0]

    def ReadLocationFromCSV(self, file=None):
        # The .csv file should contain the name and location of each position in the following format
        # PosName | Loc_x | Loc_y
        # --------|-------|------
        # name1   | x1    | y1
        # name2   | x2    | y2

        df = pd.read_csv(file)
        for index, row in df.iterrows():
            self.locDict[str(row[0])] = (row[1], row[2])

    def ReadFrequencyFromCSV(self, file=None):
        # The .csv file should contain the name and frequency of each position in the following format
        # PosName | frequency(times)
        # --------|-----------------
        # name1   | # freq1
        # name2   | # freq2

        df = pd.read_csv(file)
        for index, row in df.iterrows():
            self.freqDict[Tools.correctPosName(str(row[0]))] = row[1]
        nanList = np.isnan(np.array(list(self.freqDict.values())))
        keyList = list(self.freqDict.keys())
        for i in range(len(nanList)):
            if nanList[i]:
                del self.freqDict[keyList[i]]


    def _divideIntoClasses(self,arr,n_classes):
        # Quantiles
        classes = np.array([0]*len(arr))
        Qs = [np.quantile(arr,(i+1)/n_classes) for i in range(n_classes)]
        for i in range(n_classes):
            index = n_classes-i-1
            classes[arr < Qs[index]] = int(index)
        return classes

    def PlotLayout(self):
        fig, ax = plt.subplots(figsize=(15, 1.763))
        ax.set_xlim(-0.5, 411.5)
        ax.set_ylim(-0.5, 42.5)
        ax.set_xticks([])
        ax.set_yticks([])
        w = 4.5
        h = 4.5

        # self.locDict = {"Name of position": [x,y]}
        Positions = self.locDict
        posValues = np.array(list(Positions.values()))
        ys = posValues[:,-1]
        ymid = (np.min(ys) + np.max(ys)) / 2

        for [x, y] in posValues:
            height = h
            # If in the middle line, height*2
            if y == ymid:
                height = 2*h
            ax.add_patch(patches.Rectangle(
                (x - 0.45*w, y - height/2),  # (x,y)
                0.9*w, # width
                height # height
            ))
        plt.show()

    def PlotHeatMap(self):
        fig, ax = plt.subplots(figsize=(15, 1.763))
        ax.set_xlim(-0.5, 411.5)
        ax.set_ylim(-0.5, 42.5)
        ax.set_xticks([])
        ax.set_yticks([])
        w = 4.5
        h = 4.5

        Positions = self.locDict
        Frequencies = self.freqDict

        ys = np.array(list(Positions.values()))[:,-1]
        ymid = (np.min(ys) + np.max(ys)) / 2

        freq = np.array(list(Frequencies.values()))

        n_classes = 7
        color_class = self._divideIntoClasses(freq, n_classes)
        colors = list(seaborn.color_palette("Reds", n_colors=n_classes))

        for pos in list(Positions.keys()):
            [x, y] = Positions[pos]
            color = 'grey'  # default
            if len(pos)==1:
                pos = '801-0' + str(pos) + '-A-01'
            if len(pos)==2 or len(pos)==3:
                pos = '801-' + str(pos) + '-A-01'

            try:
                index = list(Frequencies.keys()).index(pos)
                color = colors[color_class[index]]
            except:
                pass

            height = h
            # if middle row, h*2
            if y == ymid:
                height = 2 * h
            ax.add_patch(patches.Rectangle(
                (x - 0.45 * w, y - height / 2),  # (x,y)
                0.9 * w,  # width
                height,  # height
                color = color
            ))
        plt.show()


if __name__ == '__main__':
    palletPos = PalletPos()
    palletPos.ReadLocationFromCSV('layout.csv')
    palletPos.ReadFrequencyFromCSV('freq_post.csv')
    palletPos.ReadSKUPositionFromCSV('locationToSKU.csv')
    print(palletPos.SKULocDict)
    # print(palletPos.freqDict)
    # palletPos.DrawHeatMap()