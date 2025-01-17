from lab1.liuvacuum import *

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3


def direction_to_string(cdr):
    cdr %= 4
    return "NORTH" if cdr == AGENT_DIRECTION_NORTH else \
        "EAST" if cdr == AGENT_DIRECTION_EAST else \
            "SOUTH" if cdr == AGENT_DIRECTION_SOUTH else \
                "WEST"  # if dir == AGENT_DIRECTION_WEST


"""
Internal state of a vacuum agent
"""


class MyAgentState:

    def __init__(self, width, height):

        # Initialize perceived world state
        self.world = [[AGENT_STATE_UNKNOWN for _ in range(height)] for _ in range(width)]
        self.world[1][1] = AGENT_STATE_HOME

        # Agent internal state
        self.last_action = ACTION_NOP
        self.direction = AGENT_DIRECTION_EAST
        self.pos_x = 1
        self.pos_y = 1

        # Metadata
        self.world_width = width
        self.world_height = height

    """
    Update perceived agent location
    """

    def update_position(self, bump):
        if not bump and self.last_action == ACTION_FORWARD:
            if self.direction == AGENT_DIRECTION_EAST:
                self.pos_x += 1
            elif self.direction == AGENT_DIRECTION_SOUTH:
                self.pos_y += 1
            elif self.direction == AGENT_DIRECTION_WEST:
                self.pos_x -= 1
            elif self.direction == AGENT_DIRECTION_NORTH:
                self.pos_y -= 1

    """
    Update perceived or inferred information about a part of the world
    """

    def update_world(self, x, y, info):
        self.world[x][y] = info

    """
    Dumps a map of the world as the agent knows it
    """

    def print_world_debug(self):
        for y in range(self.world_height):
            for x in range(self.world_width):
                if self.world[x][y] == AGENT_STATE_UNKNOWN:
                    print("?" if DEBUG_OPT_DENSEWORLDMAP else " ? ", end="")
                elif self.world[x][y] == AGENT_STATE_WALL:
                    print("#" if DEBUG_OPT_DENSEWORLDMAP else " # ", end="")
                elif self.world[x][y] == AGENT_STATE_CLEAR:
                    print("." if DEBUG_OPT_DENSEWORLDMAP else " . ", end="")
                elif self.world[x][y] == AGENT_STATE_DIRT:
                    print("D" if DEBUG_OPT_DENSEWORLDMAP else " D ", end="")
                elif self.world[x][y] == AGENT_STATE_HOME:
                    print("H" if DEBUG_OPT_DENSEWORLDMAP else " H ", end="")

            print()  # Newline
        print()  # Delimiter post-print


"""
Vacuum agent
"""


class MyVacuumAgent(Agent):

    def __init__(self, world_width, world_height, log):
        super().__init__(self.execute)
        self.initial_random_actions = 10
        self.iteration_counter = 10000
        self.state = MyAgentState(world_width, world_height)
        self.log = log
        self.actionQueue = []
        self.path = []
        self.childParentDic = {}
        self.frontier = []


    def move_to_random_start_position(self, bump):
        action = random()

        self.initial_random_actions -= 1
        self.state.update_position(bump)

        if action < 0.1666666:  # 1/6 chance
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT
        elif action < 0.3333333:  # 1/6 chance
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT
        else:  # 4/6 chance
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD

    def execute(self, percept):

        ###########################
        # DO NOT MODIFY THIS CODE #
        ###########################

        bump = percept.attributes["bump"]
        dirt = percept.attributes["dirt"]
        home = percept.attributes["home"]

        # Move agent to a randomly chosen initial position
        if self.initial_random_actions > 0:
            self.log("Moving to random start position ({} steps left)".format(self.initial_random_actions))
            return self.move_to_random_start_position(bump)

        # Finalize randomization by properly updating position (without subsequently changing it)
        elif self.initial_random_actions == 0:
            self.initial_random_actions -= 1
            self.state.update_position(bump)
            self.state.last_action = ACTION_SUCK
            self.log("Processing percepts after position randomization")
            return ACTION_SUCK

        ########################
        # START MODIFYING HERE #
        ########################

        # Max iterations for the agent
        if self.iteration_counter < 1:
            if self.iteration_counter == 0:
                self.iteration_counter -= 1
                self.log("Iteration counter is now 0. Halting!")
                self.log("Performance: {}".format(self.performance))
            return ACTION_NOP

        self.log("Position: ({}, {})\t\tDirection: {}".format(self.state.pos_x, self.state.pos_y,
                                                              direction_to_string(self.state.direction)))
        self.iteration_counter -= 1

        # Track position of agent
        self.state.update_position(bump)

        if bump:
            # Get an xy-offset pair based on where the agent is facing
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]

            # Mark the tile at the offset from the agent as a wall (since the agent bumped into it)
            self.state.update_world(self.state.pos_x + offset[0], self.state.pos_y + offset[1], AGENT_STATE_WALL)

        # Update perceived state of current tile
        if dirt:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT)
        else:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR)

        # Debug
        self.state.print_world_debug()


        if dirt:
            self.log("DIRT -> choosing SUCK action!")
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK

        if not self.actionQueue and not self.path:
            self.breadthFirstSearch()

        if self.path and not self.actionQueue:
            step = self.path.pop(0)
            if step == AGENT_DIRECTION_NORTH:
                self.moveNorth()
            elif step == AGENT_DIRECTION_EAST:
                self.moveEast()
            elif step == AGENT_DIRECTION_SOUTH:
                self.moveSouth()
            else:
                self.moveWest()

        if self.actionQueue:
            self.state.last_action = self.actionQueue[0]
            if self.actionQueue[0] is ACTION_TURN_LEFT:
                self.state.direction = (self.state.direction + 3) % 4
            elif self.actionQueue[0] is ACTION_TURN_RIGHT:
                self.state.direction = (self.state.direction + 1) % 4
            return self.actionQueue.pop(0)

        else:
            return ACTION_NOP

    def pathFinder(self, goal, current):
        goalFind = self.childParentDic[goal]
        homeFind = self.childParentDic[current]
        goalList = []
        counter = 0
        while True:
            if goalFind is not None:
                self.path.insert(len(self.path)-counter, self.getDir(goalFind, goal))
                goal = goalFind
                goalList.append(goalFind)
                goalFind = self.childParentDic[goal]
            if homeFind in goalList or homeFind == goalFind:
                return
            if homeFind is not None:
                self.path.insert(counter, self.getDir(current, homeFind))
                current = homeFind
                homeFind = self.childParentDic[current]
            if homeFind == goal or homeFind in goalList:
                return
            counter += 1

    # Find unknown nodes
    def breadthFirstSearch(self):
        currentNode = (self.state.pos_x, self.state.pos_y)
        if not self.frontier:
            self.frontier.append(currentNode)
            self.childParentDic[currentNode] = None
        self.adjacentNodes(currentNode)
        while self.frontier:
            parent = self.frontier.pop()
            if self.state.world[parent[0]][parent[1]] is AGENT_STATE_UNKNOWN:
                self.pathFinder(parent, currentNode)
                return

        return

    def moveNorth(self):
        if self.state.direction == 0:
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_FORWARD)
        else:
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_FORWARD)

    def moveEast(self):
        if self.state.direction == 0:
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_FORWARD)
        else:
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_FORWARD)

    def moveSouth(self):

        if self.state.direction == 0:
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            self.actionQueue.append(ACTION_FORWARD)
        else:
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_FORWARD)

    def moveWest(self):
        if self.state.direction == 0:
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_TURN_LEFT)
            self.actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            self.actionQueue.append(ACTION_TURN_RIGHT)
            self.actionQueue.append(ACTION_FORWARD)
        else:
            self.actionQueue.append(ACTION_FORWARD)

    def adjacentNodes(self, currentNode):
        x = currentNode[0]
        y = currentNode[1]
        adjacentNodes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for node in adjacentNodes:
            if node not in self.childParentDic.keys() and node not in self.childParentDic.values() and self.state.world[node[0]][node[1]] is not AGENT_STATE_WALL:
                self.childParentDic[node] = currentNode
                self.frontier.append(node)

    def update_direction(self):
        # Update Direction when turning
        if self.state.direction == 3:
            self.state.direction = 0
        else:
            self.state.direction += 1

    def getDir(self, nFrom, nTo):

        deltaX = nTo[0] - nFrom[0]
        deltay = nTo[1] - nFrom[1]

        if (deltay == -1):
            return AGENT_DIRECTION_NORTH
        elif (deltaX == 1):
            return AGENT_DIRECTION_EAST
        elif(deltay == 1):
            return AGENT_DIRECTION_SOUTH
        elif(deltaX == -1):
            return AGENT_DIRECTION_WEST
        else:
            return -1


