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
        self.iteration_counter = 1000
        self.state = MyAgentState(world_width, world_height)
        self.log = log

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

        actionQueue = []
        toVisitQueue = []
        visited = []
        currentNode = (self.state.pos_x, self.state.pos_y)

        if (currentNode) not in visited:
            visited.append(currentNode)
            toVisitQueue.append(currentNode)
            startNode = currentNode

        # Decide action

        if dirt:
            self.log("DIRT -> choosing SUCK action!")
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK

        elif bump:

            self.state.last_action = ACTION_TURN_RIGHT
            self.update_direction()

            return ACTION_TURN_RIGHT

        else:
            if actionQueue:
                self.state.last_action = actionQueue[0]
                return actionQueue.pop(0)

            currentNode = toVisitQueue.pop(0)

            for node in self.adjacentNodes(currentNode):
                if node not in visited:
                    toVisitQueue.append(node)
                    visited.append(node)

    def pathFinder(self, goal, childParentDic):
        path = [goal]
        parent = childParentDic.get(goal)
        while parent is not None:
            path.append(parent)
            goal = parent
            parent = childParentDic.get(goal)
        path.pop(len(path) - 1)
        return path

    # Find unknown nodes
    def breadthFirstSearch(self):
        childParentDic = {}
        frontier = []
        currentNode = (self.state.pos_x, self.state.pos_y)
        frontier.add(currentNode)
        childParentDic.update(currentNode, None)
        while frontier is not None:
            parent = frontier.pop(0)
            if self.state.world[parent[0]][parent[1]]:
                return self.pathFinder(parent, childParentDic)
            adjacentNodes = self.adjacentNodes(currentNode)
            for node in adjacentNodes:
                childParentDic.update(node, parent)
                frontier.append(node)
        return None

    def moveNorth(self):
        actionQueue = []
        if self.state.direction == 0:
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_FORWARD)
        else:
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_FORWARD)
        return actionQueue

    def moveEast(self):
        actionQueue = []
        if self.state.direction == 0:
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_FORWARD)
        else:
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_FORWARD)
        return actionQueue

    def moveSouth(self):
        actionQueue = []
        if self.state.direction == 0:
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            actionQueue.append(ACTION_FORWARD)
        else:
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_FORWARD)
        return actionQueue

    def moveWest(self):
        actionQueue = []
        if self.state.direction == 0:
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 1:
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_TURN_LEFT)
            actionQueue.append(ACTION_FORWARD)
        elif self.state.direction == 2:
            actionQueue.append(ACTION_TURN_RIGHT)
            actionQueue.append(ACTION_FORWARD)
        else:
            actionQueue.append(ACTION_FORWARD)
        return actionQueue

    def adjacentNodes(self, currentNode):
        x = currentNode[0]
        y = currentNode[1]
        adjacentNodes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return adjacentNodes

    def update_direction(self):
        # Update Direction when turning
        if self.state.direction == 3:
            self.state.direction = 0
        else:
            self.state.direction += 1
