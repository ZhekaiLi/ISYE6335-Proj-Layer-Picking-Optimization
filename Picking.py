import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from itertools import combinations
from itertools import permutations
from Tools import Tools



class Picking:
    def __init__(self, pko, df):
        self.df = df   # data of items to be picked as (pd.DataFrame)
        self.df_cls = None

        self.pko = pko # object created from (Class: PickingLogic), 
                       # which store and organize some useful infos

        self.Routes = []
        self.routes = None
        self.travelDistance = 0

    # main function
    def picking(self):
        df = self.df
        pko = self.pko
        for cls in range(int(max(pko.posCls)+1)):
            # (1) Filter positions in the same cls(class or section)
            self.df_cls = df[df['Class']==cls]

            # (2) Take away positions that contains more than 5 layers
            # e.g. position 'LAY414' has 8 layers to be picked, then this step will take away 5 layers from 'LAY414'
            self.routes = self._pickLayersMoreThan5()

            # (3) Delete positions that all have been picked
            # and use a dictionary to store the leftover items
            # {'Position': number of layers}
            self.df_cls = self.df_cls[self.df_cls['layers']>0]
            self.dict_cls = {}
            for idx, row in self.df_cls.iterrows():
                self.dict_cls[row['Location']] = row['layers']

            # (4) Pair picking
            # (4.1) Filter pairs(from pko.posPairs) that contains positions having layers to be picked
            usefulPosPairs = []
            for p in list(permutations(self.dict_cls.keys(), 2)):
                for pair in self.pko.posPairs[cls]:
                    if list(p) in pair:
                        usefulPosPairs.append(pair)

            # (4.2) Sort pairs by distance
            if len(usefulPosPairs) > 0:
                df_pairs = pd.DataFrame(np.array(usefulPosPairs), columns=['pairs', 'route type', 'distance'])
                df_pairs.sort_values(by=['distance'], ascending=True, inplace=True)
                df_pairs['l1'] = np.array(df_pairs['pairs'].to_list())[:,0]
                df_pairs['l2'] = np.array(df_pairs['pairs'].to_list())[:,1]
                self.df_pairs = df_pairs

            # (4.3) Start pair picking
            # until there is at most one position that has not been picked
            while sum(np.array(list(self.dict_cls.values())) > 0) > 1:
                # (4.3.1) Picing the first pair with shortest distance
                totalLayers, lastRouteType = self._pickFirstPair()
                if totalLayers == 0:
                    break
                # (4.3.2) If the total layers picked <= 5, continue picking
                self._continuePicking(totalLayers, lastRouteType)

            # (4.4) Finally, pick the left layers if exists
            for key in self.dict_cls.keys():
                if self.dict_cls[key] > 0:
                    self.routes.append([[key]])
                    self.dict_cls[key] = 0
            self.Routes.append(self.routes)

        # Finally, calculate the total travel distance
        for i in sum(sum(sum(self.Routes, []), []), []):
            try:
                if i > 1: self.travelDistance += i
            except:
                pass
        

    def _pickLayersMoreThan5(self):
        df_cls = self.df_cls

        routes = []
        for i in df_cls.index:
            layers = df_cls.loc[i,'layers']
            times = layers // 5
            for t in range(times):
                routes.append([[df_cls.loc[i,'Location']]])
            self.df_cls.loc[i,'layers'] = layers % 5
        return routes

    def _pickFirstPair(self):
        df_pairs = self.df_pairs
        dict_cls = self.dict_cls

        ifPick = False
        idx = 0
        totalLayers = 0
        lastRouteType = -1
        for idx in range(len(df_pairs)):
            loc1, loc2 = df_pairs.loc[df_pairs.index[idx], 'pairs']
            lastRouteType = df_pairs.loc[df_pairs.index[idx], 'route type']
            distance = df_pairs.loc[df_pairs.index[idx], 'distance']
            lyr1 = dict_cls[loc1]
            lyr2 = dict_cls[loc2]
            totalLayers = lyr1 + lyr2
            if (lyr1>0) and (lyr2>0) and (totalLayers<=5):
                self.dict_cls[loc1] = 0
                self.dict_cls[loc2] = 0
                self.locs = [loc1, loc2]
                self.route = [[loc1,loc2,lastRouteType,distance]]
                return totalLayers, lastRouteType    
        return 0,0

    def _continuePicking(self, totalLayers, lastRouteType):
        df_pairs = self.df_pairs
        dict_cls = self.dict_cls
        locs     = self.locs
        route    = self.route

        iters = 0
        while totalLayers < 5 and iters < len(df_pairs):
            iters += 1
            for idx in df_pairs.index:
                # Try a pair of positions: (loc3, loc4)
                loc3, loc4 = df_pairs.loc[idx, 'pairs']
                distance = df_pairs.loc[idx, 'distance']
                # (1) First exclude pairs that don't need any pick
                if dict_cls[loc3] == 0 and dict_cls[loc4] == 0: 
                    continue

                # (2) Then test that list(locs) could only contain exactly one of loc3 and loc4
                # which could make sure to build a 'route'
                if3In = loc3 in locs
                if4In = loc4 in locs
                if not Tools.xor(if3In, if4In):
                    continue
                loc = loc4 if if3In else loc3

                # (3) Finally exclude pairs that no on the same side(if applicable)
                count = 0
                for r in route:
                    if loc in r:
                        count += 1
                if count >= 2:
                    continue
                
                for r in route:
                    if loc in r:
                        lastRouteType = r[-1]
                routeType = df_pairs.loc[idx, 'route type']
                if lastRouteType == 0 and routeType == 1: continue
                if lastRouteType == 1 and routeType == 0: continue
                
                if totalLayers + dict_cls[loc] <= 5:
                    totalLayers += dict_cls[loc]
                    dict_cls[loc] = 0
                    locs.append(loc)
                    lastRouteType = routeType
                    route.append([loc3, loc4, lastRouteType, distance])
                    break
        self.routes.append(route)