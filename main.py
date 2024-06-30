import random
import math

class GridEnvironment:
    def __init__(self, grid_size, start, goal):
        self.grid_size = grid_size
        self.start = start
        self.goal = goal

    def get_possible_moves(self, state):
        moves = []
        x, y = state
        if x > 0 and x< self.grid_size-1:
            moves.append('left')
            moves.append("right")
        elif x==0:
            moves.append("right")
        elif x==self.grid_size:
            moves.append("left")
        if y > 0 and y< self.grid_size-1:
            moves.append('down')
            moves.append("up")
        elif y==0:
            moves.append("up")
        elif x==self.grid_size:
            moves.append("down")
        return moves

    def apply_move(self, state, move):
        x, y = state
        if move == 'up':
            return (x, y+1)
        elif move == 'down':
            return (x , y-1)
        elif move == 'left':
            return (x-1, y)
        elif move == 'right':
            return (x+1 , y)

    def is_terminal(self, state):
        return state == self.goal

    def distance_to_goal(self, state):
        x, y = state
        goal_x, goal_y = self.goal
        return abs(x - goal_x) + abs(y - goal_y)

class Node:
    def __init__(self, state):
        self.state = state
        self.children = []
        self.visits = 0
        self.value = 0
        self.parent = None

class MCTSr:
    def __init__(self, initial_state, refinement_frequency, evaluation_function, environment):
        self.root = Node(state=initial_state)
        self.refinement_frequency = refinement_frequency
        self.evaluation_function = evaluation_function
        self.environment = environment
        self.iteration_count = 0

    def selection(self, node):
        """ Select the best child node based on UCT """
        print("Selection")
        while node.children:
            print("Parent is",node.state)
            node = max(node.children, key=lambda n: self.uct_value(node, n))
            print("Max node",node.state)
        print(f"End of selection\n")
        return node

    def uct_value(self, parent, child):
        # Calculate the UCT value for a child node
        if child.visits == 0:
            return float('inf')  # If child has not been visited, prioritize it
        exploration_factor = math.sqrt(2)
        return (child.value / child.visits) + exploration_factor * math.sqrt(math.log(parent.visits) / child.visits)

    def expansion(self, node):
        """ Expand the node by adding new children using environment """
        moves = self.environment.get_possible_moves(node.state)
        for move in moves:
            new_state = self.environment.apply_move(node.state, move)
            print(f"parent node {node.state} new state {new_state}")
            new_node = Node(state=new_state)
            new_node.parent = node
            node.children.append(new_node)
        for child in node.children:
            print(f"parent node is {node.state}",child.state)
        return node.children

    def simulation(self, node):
        """ Simulate a random play to get a value """
        state = node.state
        # Simulate random steps until a terminal state is reached
        while not self.environment.is_terminal(state):
            moves = self.environment.get_possible_moves(state)
            if not moves:
                break
            state = self.environment.apply_move(state, random.choice(moves))
            print(f"simulated move for {node.state}, applied is {state}")
        return self.evaluation_function(state)

    def backpropagation(self, node, value):
        """ Backpropagate the value through the tree """
        print(f"backpropagated value {value} for",node.state)
        while node:
            node.visits += 1
            node.value += value
            node = node.parent
            print(node.state if node else "Root's parent so none")

    def self_refinement(self):
        """ Refine the search tree by re-evaluating nodes using the evaluation function """
        nodes_to_refine = [self.root]
        while nodes_to_refine:
            node = nodes_to_refine.pop()
            node.value = self.evaluation_function(node.state)
            nodes_to_refine.extend(node.children)

    def search(self):
        """ Perform MCTSr search """
        while not self.search_finished():
            selected_node = self.selection(self.root)
            print("selected node is",selected_node.state)
            expanded_nodes = self.expansion(selected_node)
            print("Expanded nodes are")
            print(expanded_node.state  for expanded_node in expanded_nodes)
            for node in expanded_nodes:
                value = self.simulation(node)
                self.backpropagation(node, value)
            self.iteration_count += 1
            if self.iteration_count % self.refinement_frequency == 0:
                self.self_refinement()
        return self.best_action()

    def search_finished(self):
        return self.iteration_count >= 1000

    def best_action(self):
        #  Return the best action from the root node 
        best_child = max(self.root.children, key=lambda n: n.visits)
        return best_child.state

    def is_terminal(self, state):
        # Check if the state is a terminal state 
        return self.environment.is_terminal(state)

if __name__ == "__main__":
    grid_size = 5
    start = (0, 0)
    goal = (4, 0)
    environment = GridEnvironment(grid_size, start, goal)

    refinement_frequency = 100
    evaluation_function = lambda state: -environment.distance_to_goal(state)
    mctsr = MCTSr(initial_state=start, refinement_frequency=refinement_frequency, evaluation_function=evaluation_function, environment=environment)

    best_state = mctsr.search()
    print(f"Best state: {best_state}")
