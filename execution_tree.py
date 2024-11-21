
import dataclasses
import struct
from typing import Optional
from graphviz import Digraph
import tkinter as tk


# Define the BranchData class
class BranchData:
    #define B_TAKEN 0x1     // Branch Taken
    #define B_FACT  0x10    // Is Factual
    #define B_VALID 0x100
    def __init__(self, flags, loc=None, dst=None, **kwargs):
        self.taken = bool(flags & 0x1)
        self.full_fact = bool(flags & (0x1 << 3))
        self.loc = loc
        self.dst = dst
        self.fact = bool(flags & (0x1 << 1))
        self.valid = bool(flags & (0x1 << 2))

    def __eq__(self, other):
        # Check if the other object is of the same class and has the same attributes
        if not isinstance(other, BranchData):
            return False
        return (self.taken == other.taken and
                self.full_fact == other.full_fact and
                self.loc == other.loc and
                self.dst == other.dst and
                self.fact == other.fact and
                self.valid == other.valid)

    def __hash__(self):
        # Combine the hash of all relevant attributes
        return hash((self.taken, self.full_fact, self.loc, self.dst, self.fact, self.valid))

    def __repr__(self) -> str:
        return f"Branch(loc={self.loc}, dst={self.dst}, valid={self.valid},taken={self.taken}, full_fact={self.full_fact} fact={self.fact})"

    @classmethod
    def from_binary(cls, data):
        # Unpack the data (1 byte)
        assert len(data) == 16
        print(data)
        return cls(int.from_bytes(data[0:4], 'big'), int.from_bytes(data[4:8], 'big'), int.from_bytes(data[8:12], 'big'))

    @property
    def data_binary(self):
        return struct.pack('B', self.data)

@dataclasses.dataclass(slots=True)
class BranchNode:
    fact: bool
    full_fact: bool
    loc: int | None = None
    left: Optional['BranchEdge'] = None  # Left child for `taken=False`
    right: Optional['BranchEdge'] = None # Right child for `taken=True`

@dataclasses.dataclass(slots=True)
class BranchEdge:
    node: BranchNode
    count: int = 1


class BranchTree:
    def __init__(self):
        self.root = BranchNode(fact=True, full_fact=True)  # Start with the root as a valid branch

    def add_path(self, branches: list[BranchData]):
        curr = self.root

        for b in branches:
            next = curr.left if b.taken else curr.right
            if next:
                next.count += 1
            else:
                if b.taken:
                    next = curr.left = BranchEdge(BranchNode(fact=b.fact, full_fact=b.full_fact,loc=b.loc))
                else:
                    next = curr.right = BranchEdge(BranchNode(fact=b.fact, full_fact=b.full_fact,loc=b.loc))
            curr = next.node

    def add_branch(self, path, branch:'BranchData'):
        # Traverse the tree based on the execution path to find the insertion point
        current = self.root
        for taken in path:
            if taken:
                if current.right is None:
                    current.right = BranchNode()  # Create node if it does not exist
                current = current.right
            else:
                if current.left is None:
                    current.left = BranchNode()
                current = current.left
        # Set the current node with the branch details
        current.valid = branch.valid
        current.taken = branch.taken
        current.factual = branch.factual

    def visualize_tree(self, tree_file, branch_dict: dict[BranchData, int], normal_connection: list[tuple[int,int]], jmp_list, ret_list):
        dot = Digraph(comment='Branch Tree')
        NODE_COLOR = "blue"
        for b, i in branch_dict.items(): 
            # Define node color based on factual status
            label = f"{b.loc or ''}"
            dot.node(str(b.loc), label=label, color='black', style="filled", fillcolor=NODE_COLOR)
            
            label = f"{b.dst or ''}"
            dot.node(str(b.dst), label=label, color='black', style="filled", fillcolor=NODE_COLOR)
            
            if not b.fact:
                color = "red"
            else:
                color = "yellow" if not b.full_fact else "green"
            
            dot.edge(str(b.loc), str(b.dst), color=color, label=f"{i}")
        for x in ret_list:
            dot.node(str(x), label=f"Ret@{x}", color='black', style="filled", fillcolor=NODE_COLOR)
        for c in normal_connection:
            dot.edge(str(c[0]), str(c[1]), color="black")
        for x in jmp_list:
            dot.node(str(x[0]), label=str(x[0]), color='black', style="filled", fillcolor=NODE_COLOR)
            dot.node(str(x[1]), label=str(x[1]), color='black', style="filled", fillcolor=NODE_COLOR)
            dot.edge(str(x[0]), str(x[1]), color="blue")
        

        # Render the graph to a file (e.g., PNG or PDF)
        dot.render(filename=tree_file, format='png', cleanup=True)