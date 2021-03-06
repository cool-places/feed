## Data structure for what I call weight trees.
##
## Used to randomly sample posts w/ relative weights (hot_factors)
## without replacement.

from collections import deque
import random

def print_tree(tree):
    def print_h(node, prefix):
        if node is None:
            return
        
        print(prefix + str(node))
        print_h(node.l, prefix + '-')
        print_h(node.r, prefix + '-')

    print_h(tree.root, '')

class Node:
    def __init__(self, id=None, hot_factor=None, parent=None, type='LEAF'):
        # we are going to treat id itself as the data that Node holds
        self.id = id
        self.parent = parent
        self.l, self.r = None, None

        self.lsum = 0
        self.hot_factor = hot_factor
        self.type = type # enum('PATH', 'LEAF')
        self.sum = hot_factor if type == 'LEAF' else 0

    def shed(self):
        assert(self.type == 'LEAF')

        node = Node(self.id, self.hot_factor)
        self.id, self.hot_factor = None, None
        self.type = 'PATH'
        return node

    def __str__(self):
        return f'({self.id}, lsum: {self.lsum}, sum: {self.sum})'
        # return str(self.id)

class WTree:
    def __init__(self):
        # entry dummy node
        self.root = Node(type='PATH')
        # map: id -> leaf node
        self.nodes = dict()

        # holes represent queue of places to add to
        self.holes = deque([(self.root, 'l'), (self.root, 'r')])

    def add(self, id, hot_factor):
        if id not in self.nodes:
            parent, c = self.holes.popleft()
            node = Node(id, hot_factor)
            self.nodes[id] = node

            if c == 'l':
                parent.l = node
            else:
                parent.r = node
            node.parent = parent
            
            if (parent.type == 'LEAF'):
                # push leaf down to right
                parent.r = parent.shed()
                parent.r.parent = parent
                self.nodes[parent.r.id] = parent.r
                # add more holes that data can be added to
                self.holes.extend([(node, 'l'), (parent.r, 'l')])
            else:
                self.holes.append((node, 'l'))

            parent.lsum = (0 if parent.l is None else parent.l.sum)
            parent.sum = parent.lsum + (0 if parent.r is None else parent.r.sum)

            child = parent
            parent = parent.parent
        else:
            node = self.nodes[id]
            node.hot_factor = hot_factor
            node.sum = hot_factor

            child = node
            parent = node.parent

        # update hot_factor up the tree
        while (parent is not None):
            if (child is parent.l):
                parent.lsum = child.sum
                parent.sum = parent.lsum + (0 if parent.r is None else parent.r.sum)
            else:
                parent.sum = parent.lsum + child.sum 

            child = parent
            parent = parent.parent

    # sample from tree w/ weights without replacement
    def pop(self):
        def pop_h(node, num):
            if node.type == 'LEAF':
                # actual removal happens here
                if node is node.parent.l:
                    node.parent.l = None
                    self.holes.appendleft((node.parent, 'l'))
                else:
                    node.parent.r = None
                    self.holes.appendleft((node.parent, 'r'))
                self.nodes.pop(node.id)
                return node
            
            if num <= node.lsum:
                ans = pop_h(node.l, num)
                node.lsum = 0 if node.l is None else node.l.sum
                node.sum = node.lsum + (0 if node.r is None else node.r.sum)
            else:
                ans = pop_h(node.r, num - node.lsum)
                node.sum = node.lsum + (0 if node.r is None else node.r.sum)

            return ans

        if len(self.nodes) == 0:
            return None

        num = random.randint(1, self.root.sum)
        ans = pop_h(self.root, num)
        return ans.id

    def size(self):
        return len(self.nodes)

    def pop_multi(self, n):
        return [self.pop() for i in range(min(n, len(self.nodes)))]


# simple test
# tree = WTree()

# tree.add(0, 33)
# tree.add(1, 1)
# tree.add(2, 55)
# tree.add(3, 70)
# tree.add(4, 15)
# tree.add(5, 20)
# tree.add(6, 100)
# tree.add(7, 20)
# tree.add(8, 2)

# print_tree(tree)

# tree.update(1, 50)

# print_tree(tree)

# for i in range(5):
#     print(tree.pop())

# print_tree(tree)

# tree.add(9, 1)
# tree.add(10, 12)

# print_tree(tree)




