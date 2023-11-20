# AVL tree implementation
import sys
from typing import Union


# Create a tree node
class TreeNode(object):
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.left = None
        self.right = None
        self.height = 1


class AVLTree(object):
    def __init__(self):
        self.root = None

    def insert_or_update_node(self, key: Union[int, str], value: list) -> None:
        self.root = self._insert_or_update_node(self.root, key, value)

    # Function to insert a node or update data of a node
    def _insert_or_update_node(self, node: TreeNode, key: Union[int, str], value: list) -> TreeNode:

        # Find the correct location and insert the node
        if not node:
            return TreeNode(key, [value])

        if key == node.key:
            node.data.append(value)
            return node

        if key < node.key:
            node.left = self._insert_or_update_node(node.left, key, value)
        else:
            node.right = self._insert_or_update_node(node.right, key, value)

        self.update_height(node)

        # Update the balance factor and balance the tree
        balanceFactor = self.get_balance(node)
        if balanceFactor > 1:
            if key < node.left.key:
                return self.right_rotate(node)
            else:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)

        if balanceFactor < -1:
            if key > node.right.key:
                return self.left_rotate(node)
            else:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

        return node

    # Function to perform left rotation
    def left_rotate(self, z: TreeNode) -> TreeNode:
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        self.update_height(z)
        self.update_height(y)
        return y

    # Function to perform right rotation
    def right_rotate(self, z: TreeNode) -> TreeNode:
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        self.update_height(z)
        self.update_height(y)
        return y

    # Update height of the node
    def update_height(self, node: TreeNode) -> None:
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    # Get the height of the node
    @staticmethod
    def get_height(node: TreeNode) -> int:
        return 0 if not node else node.height

    # Get balance factor of the node
    def get_balance(self, node: TreeNode) -> int:
        return 0 if not node else self.get_height(node.left) - self.get_height(node.right)

    # Print the tree
    def print_helper(self, currPtr: TreeNode, indent: str, last: bool):
        if currPtr is not None:
            sys.stdout.write(indent)
            if last:
                sys.stdout.write("R----")
                indent += "     "
            else:
                sys.stdout.write("L----")
                indent += "|    "
            print(currPtr.key, currPtr.data)
            self.print_helper(currPtr.left, indent, False)
            self.print_helper(currPtr.right, indent, True)

    def collect_values_from_subtree(self, node: TreeNode, result: list):
        if node is None:
            return
        self.collect_values_from_subtree(node.left, result)
        result.extend(node.data)
        self.collect_values_from_subtree(node.right, result)

    def get_values_less_than(self, target: Union[int, str]):
        result = []
        self._get_values_less_than(self.root, target, result)
        return result

    def _get_values_less_than(self, node: TreeNode, target: Union[int, str], result: list):
        if node is None:
            return

        if node.key < target:
            self.collect_values_from_subtree(node.left, result)
            # Node value is less than target value => add it to result
            result.extend(node.data)
            # Check right subtree
            self._get_values_less_than(node.right, target, result)
        else:
            # Check left subtree
            self._get_values_less_than(node.left, target, result)

    def get_values_greater_than(self, target: Union[int, str]):
        result = []
        self._get_values_greater_than(self.root, target, result)
        return result

    def _get_values_greater_than(self, node: TreeNode, target: Union[int, str], result: list):
        if node is None:
            return

        if node.key > target:
            self.collect_values_from_subtree(node.right, result)
            # Node value is greater than target value => add it to result
            result.extend(node.data)
            # Check left subtree
            self._get_values_greater_than(node.left, target, result)
        else:
            # Check right subtree
            self._get_values_greater_than(node.right, target, result)

    def get_equal(self, target: Union[int, str]):
        result = []
        self._get_equal(self.root, target, result)
        return result

    def _get_equal(self, node: TreeNode, target: Union[int, str], result):
        if node is None:
            return

        if node.key == target:
            # Node value is equal to target value => add it to result
            result.extend(node.data)

        elif node.key < target:
            # Check right subtree
            self._get_equal(node.right, target, result)
        else:
            # Check left subtree
            self._get_equal(node.left, target, result)


# tests
if __name__ == '__main__':
    myTree = AVLTree()

    myTree.insert_or_update_node(13, 20)
    myTree.insert_or_update_node(4, 100)
    myTree.insert_or_update_node(10, 110)
    myTree.insert_or_update_node(10, 120)
    myTree.print_helper(myTree.root, "", True)

    key = 14
    result = myTree.get_values_less_than(myTree.root, key)
    print(result)
    result = myTree.get_values_greater_than(myTree.root, key)
    print(result)
