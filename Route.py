import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from WarehouseObj import PalletPos

class Route:
    def __init__(self, aisles_x, layoutFileDir='layout.csv'):
        self.palletPos = PalletPos()
        
        # Read location info(name, x_coor, y_coor)
        # which will update palletPos.locDict
        self.palletPos.ReadLocationFromCSV(layoutFileDir)

        # x-coordinates of vertical aisles
        self.aisles_x = aisles_x

    def PlotLayout(self):
        """
        Plot and save the initial layout into file "layout_init.png"
        :return: None
        """
        fig, ax = plt.subplots(figsize=(15, 1.763))
        ax.set_xlim(-0.5, 411.5)
        ax.set_ylim(-0.5, 42.5)
        ax.set_xticks([])
        ax.set_yticks([])
        w = 4.5
        h = 4.5

        # 读取 dictionary 类型的数据 ({"Name of position": [x,y]})
        Positions = self.palletPos.locDict
        Positions_values = np.array(list(Positions.values()))
        ybot = np.min(Positions_values[:,-1])
        ytop = np.max(Positions_values[:,-1])
        ymid = (ybot+ytop)/2

        for [x, y] in Positions_values:
            height = h
            # 如果在中间行，高度*2
            if y == ymid:
                height = 2*h
            ax.add_patch(patches.Rectangle(
                (x - 0.45*w, y - height/2),  # (x,y)
                0.9*w, # width
                height # height
            ))
        fig.savefig('layout_init.png', bbox_inches='tight')

    def PlotLayoutAndRoute(self, p1, p2, forkLoc=0)->float:
        """
        Plot the route from p1 to p2 (p2 could be a list of points) and calculate the total distance
        :param p1: name of source point e.g. "point1"
        :param p2: name of destination point(when p2 does not contain comma) e.g. "point2"
                   names of visit and destination points(when p2 contains comma) e.g. "point2,point3"
        :param forkLoc: when travelling from the middle line, it's optional to indicate whether travel from upper side or bottom side
            forkLoc = 0(default): travel from bottom
            forkloc = 1: travel from upper side
        :return: distance of route
        """
        fig, ax = plt.subplots(figsize=(15, 1.763))
        ax.set_xlim(-0.5, 411.5)
        ax.set_ylim(-0.5, 42.5)
        ax.set_xticks([])
        ax.set_yticks([])
        w = 4.5
        h = 4.5

        # 读取 dictionary 类型的数据 ({"Name of position": [x,y]})
        Positions = self.palletPos.locDict
        Positions_values = np.array(list(Positions.values()))
        ybot = np.min(Positions_values[:,-1])
        ytop = np.max(Positions_values[:,-1])
        ymid = (ybot+ytop)/2

        #
        # Plot layout
        #
        for [x, y] in Positions_values:
            height = h
            # 如果在中间行，高度*2
            if y == ymid:
                height = 2*h
            ax.add_patch(patches.Rectangle(
                (x - 0.45*w, y - height/2),  # (x,y)
                0.9*w, # width
                height # height
            ))

        #
        # Plot route
        #
        p2s = p2.split(",")
        distance_sum = 0
        # 目前最多支持四条子路径
        colors = ['black','red','orange','green']
        linestyles = ['solid', (0, (5, 3)), (0, (5, 6)), 'dotted']
        for i in range(len(p2s)):
            if i == 0:
                p2 = p2s[i]
                route, nextForkLoc = self.getRoute(Positions[p1], Positions[p2], ybot, ytop, forkLoc)
            else:
                p1, p2 = p2s[i-1], p2s[i]
                route, nextForkLoc = self.getRoute(Positions[p1], Positions[p2], ybot, ytop, nextForkLoc)
            route = np.array(route)
            ax.plot(route[:, 0], route[:, 1], color=colors[i], linestyle=linestyles[i], linewidth=2.5, label="route {}".format(i))
            distance_sum += self.calculateRoute(route)
        ax.legend()
        fig.savefig('layout_update.png', bbox_inches='tight')
        return distance_sum

    def calculateRoute(self, route):
        dist_sum = 0
        for p in range(1, len(route)):
            distance = np.linalg.norm(route[p]-route[p-1])
            dist_sum += distance
        return dist_sum

    def getRoute(self, pos1, pos2, ymin, ymax, forkLoc=0)->list:
        """
        Get the points along the route
        :param pos1: (x1, y1) central location of pallet 1
        :param pos2: (x2, y2) central location of pallet 2
        :param ymin: y value of bottom line
        :param ymax: y value of top line
        :param forkLoc: layers in middle line could be picked from two sides
            forkLoc = 0 indicates lower side, = 1 upper side
        :return:
            route: [[p1x,p1y], [p2x,p2y],...]
            forkLoc: 0 or 1 it's on the upper middle row or bottom middle row
        """
        x1, y1 = pos1
        x2, y2 = pos2

        w = 4.5 # width of pallet position
        h = 4.5 # height of pallet position
        a = 12  # width of aisle

        # 如果p1,p2在同一行: 构造四个点
        if y1 == y2:
            if y1 == ymin:
                p1 = [x1,     y1+h/2]
                p2 = [x1, y1+h/2+a/2]
                p3 = [x2, y2+h/2+a/2]
                p4 = [x2,     y2+h/2]
            elif y1 == ymax:
                p1 = [x1,     y1-h/2]
                p2 = [x1, y1-h/2-a/2]
                p3 = [x2, y2-h/2-a/2]
                p4 = [x2,     y2-h/2]
            else: # 两个都在中间行
                if not forkLoc:
                    p1 = [x1, y1 - h]
                    p2 = [x1, y1 - h - a / 2]
                    p3 = [x2, y2 - h - a / 2]
                    p4 = [x2, y2 - h]
                else:
                    p1 = [x1, y1 + h]
                    p2 = [x1, y1 + h + a / 2]
                    p3 = [x2, y2 + h + a / 2]
                    p4 = [x2, y2 + h]
            return [p1, p2, p3, p4], forkLoc
        else:
            # 不在同一行, 构造路径 pos1->pos2
            # 有六种情况 行1->行2, 行1->行3, 行2->行3 (反之三种)
            # 因为只有从 行2 出发时需要考虑从上方还是下方出发，因此可以将这六种情况分为两类
            # (1) 出发点不在中间行, 不用考虑叉车的起始位置
            nextforkLoc = 0
            if y1 != (ymin+ymax)/2:
                # 默认 y1 < y2
                sign1, sign2 = 1, -1
                if y1 > y2:
                    sign1, sign2 = -1, 1
                p1 = [x1, y1 + sign1*h/2]
                p2 = [x1, y1 + sign1*(h/2+a/2)]
                # 如果到达点不在中间行
                if y2 != (ymin + ymax) / 2:
                    pm1 = [x2, y2 + sign2*h/2] # pm1: points_minus_1 表示倒数第一个节点
                    pm2 = [x2, y2 + sign2*(h/2+a/2)]
                # 如果到达点在中间行
                else:
                    pm1 = [x2, y2 + sign2*h]
                    pm2 = [x2, y2 + sign2*(h+a/2)]
                # 如果到达点在中间行，而且是从上行拿到中间行的，这说明下个路径得从中间行的上侧出发
                if (y1 > y2) and (y2 == (ymin+ymax)/2):
                    nextforkLoc = 1
            # (2) 出发点在中间行, 通过 forkLoc 来决定从下面出发还是从上面出发
            else:
                if not forkLoc: # 从下方拿
                    p1 = [x1,     y1-h]
                    p2 = [x1, y1-h-a/2]
                else:           # 从上方拿
                    p1 = [x1,     y1+h]
                    p2 = [x1, y1+h+a/2]
                if y2 > y1: # 中间行->上行
                    pm2 = [x2, y2 - h / 2 - a / 2]
                    pm1 = [x2, y2 - h / 2]
                else:       # 中间行->下行
                    pm2 = [x2, y2 + h / 2 + a / 2]
                    pm1 = [x2, y2 + h / 2]

            # 判断 p2, pm2 是否在同一行
            # (1) 在同一行, 四个点
            if p2[1] == pm2[1]:
                return [p1, p2, pm2, pm1], nextforkLoc
            # (2) 不在同一行, 六个点
            else:
                # 判断两点横坐标的均值距离哪个 aisle 更近
                min_dist = 1e10
                closest_ax = 1e10
                for ax in self.aisles_x:
                    if np.abs((x1+x2)/2-ax) <= min_dist:
                        min_dist = np.abs((x1+x2)/2-ax)
                        closest_ax = ax
                p3 = [closest_ax, p2[1]]
                pm3 = [closest_ax, pm2[1]]
                return [p1, p2, p3, pm3, pm2, pm1], nextforkLoc

# if __name__ == '__main__':
#     Route = Route()