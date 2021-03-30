import src.agent
import src.states
import src.my_utils
import http_framework.worldLoader
import time
import random
import numpy as np

class Simulation:

    # with names? Let's look after ensembles and other's data scructure for max flexibility
    def __init__(self, XZXZ, run_start=True, phase=0, maNum=5, miNum=400, byNum= 2000, brNum=1000, buNum=400, pDecay=0.75, tDecay=0.25, corNum=5, times=1, is_rendering_each_step=True, rendering_step_duration=1.0):
        self.agents = set()
        self.world_slice = http_framework.worldLoader.WorldSlice(XZXZ)
        self.state = src.states.State(self.world_slice)
        self.maNum = maNum
        self.miNum = miNum
        self.byNum = byNum
        self.brNum = brNum
        self.buNum = buNum
        self.pDecay = pDecay
        self.tDecay = tDecay
        self.corNum = corNum
        self.times = times
        self.is_rendering_each_step = is_rendering_each_step
        self.rendering_step_duration = rendering_step_duration
        self.phase = phase

        if run_start:
            self.start()

    def start(self):
        print("started")
        for i in range(1):
            a = False
            while a is False:
                a = self.state.init_main_st()

    def step(self, times=1):
        ##########
        for i in range(times):
            self.handle_nodes()
            self.update_agents()
            self.state.render()
            time.sleep(self.rendering_step_duration)


    def handle_nodes(self):
        self.state.prosperity *= self.pDecay
        self.state.traffic *= self.tDecay

        xInd, yInd = np.where(self.state.updateFlags > 0)  # to update these nodes
        indices = list(zip(xInd, yInd))  # list of tuples
        random.shuffle(indices)  # shuffle coordinates to update
        for (i, j) in indices:  # update a specific random numbor of tiles
            self.state.updateFlags[i][j] = 0
            node_pos = self.state.node_pointers[(i,j)]  # possible optimization here
            node = self.state.nodes[(node_pos)]

            # calculate roads
            if not (src.my_utils.TYPE.GREEN.name in node.get_type() or src.my_utils.TYPE.TREE.name in node.type or src.my_utils.TYPE.BUILDING.name in node.type):
                print("returnung")
                return


            node.local_prosperity = sum([n.prosperity() for n in node.local])
            print("going because local prosp is "+str(node.local_prosperity))
            node.local_traffic = sum([n.traffic() for n in node.range])

            road_found_far = len(set(node.range) & set(self.state.roads))
            print("road found far is "+str(road_found_far))
            road_found_near = len(set(node.local) & set(self.state.roads))
            print("road found near is "+str(road_found_far))

            # major roads
            if node.local_prosperity > self.maNum and not road_found_far:  # if node's local prosperity is high
                print("prosperity fulfilled; creating road")
                if node.local_prosperity > self.brNum:  # bridge/new lot minimum
                    self.state.create_road((i, j), src.my_utils.TYPE.MAJOR_ROAD.name, leave_lot=True, correction=self.corNum)
                else:
                    self.state.create_road((i, j), src.my_utils.TYPE.MAJOR_ROAD.name, correction=self.corNum)
            if node.local_prosperity > self.buNum and road_found_near:
                print("prosperity fulfilled; creating building")
                self.state.set_type_building(node.local) # wait, the local is a building?

            # if self.phase >= 2:
            #     # bypasses
            #     if node.local_traffic > self.byNum and not road_found_far:
            #         # self.state.set_new_bypass(i, j, self.corNum)
            #         self.state.set_new_bypass(i, j, self.corNum)

            # minor roads
            if self.phase >= 3:
                # find closest road node, connect to it
                if node.local_prosperity > self.miNum and not road_found_near:
                    # if not len([n for n in node.plot() if Type.BUILDING not in n.type]):
                    self.state.append_road((i, j), src.my_utils.TYPE.MINOR_ROAD.name, correction=self.corNum)

                # calculate reservations of greenery
                elif src.my_utils.TYPE.TREE.name in node.get_type() or src.my_utils.TYPE.GREEN.name in node.get_type():
                    if len(node.neighbors & self.state.built):
                        lot = node.get_lot()
                        if lot is not None:
                            # if random.random() < 0.5:
                            #     self.state.set_type_city_garden(lot)
                            # else:
                            #     self.state.set_type_building(lot)
                            self.state.set_type_building(lot)


    def add_agent(self, agent : src.agent.Agent):
        self.agents.add(agent)


    def update_agents(self):
        for agent in self.agents:
            agent.follow_path(state=self.state, walkable_heightmap=self.state.rel_ground_hm)
            # agent.move_in_state()
            agent.render()