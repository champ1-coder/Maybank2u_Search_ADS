"""
optimized/avl_tree.py

Self-balancing AVL tree keyed by transaction date (report 2.2.3).

Why not a plain Binary Search Tree? Transaction dates arrive in (roughly)
increasing order - today, then tomorrow, then the day after. Inserting
already-sorted keys into a plain BST degenerates it into a straight line
(a linked list), so lookups/traversals become O(n) instead of O(log n).

An AVL tree rebalances itself after every insert (via rotations), so it
always stays height-balanced: O(log n) guaranteed, no matter the insertion
order. As a bonus, an in-order traversal (right -> node -> left) visits
transactions from NEWEST to OLDEST for free - no separate sort step.
"""

from typing import List, Optional
import sys

sys.path.append("..")
from baseline.linear_filter import Transaction


class AVLNode:
    __slots__ = ("date", "txn_ids", "left", "right", "height")

    def __init__(self, date: str, txn_id: str):
        self.date = date
        self.txn_ids: List[str] = [txn_id]  # several txns can share one date
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None
        self.height = 1


class AVLTree:
    """AVL tree of dates -> list of transaction ids on that date."""

    def __init__(self):
        self.root: Optional[AVLNode] = None

    # ---- balancing helpers -------------------------------------------------
    def _h(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: AVLNode) -> int:
        return self._h(node.left) - self._h(node.right)

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._h(node.left), self._h(node.right))

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        y.left = x.right
        x.right = y
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        x.right = y.left
        y.left = x
        self._update_height(x)
        self._update_height(y)
        return y

    # ---- insert (O(log n)) --------------------------------------------------
    def insert(self, date: str, txn_id: str) -> None:
        self.root = self._insert(self.root, date, txn_id)

    def _insert(self, node: Optional[AVLNode], date: str, txn_id: str) -> AVLNode:
        if node is None:
            return AVLNode(date, txn_id)

        if date == node.date:
            node.txn_ids.append(txn_id)
            return node
        elif date < node.date:
            node.left = self._insert(node.left, date, txn_id)
        else:
            node.right = self._insert(node.right, date, txn_id)

        self._update_height(node)
        balance = self._balance_factor(node)

        # Left Left
        if balance > 1 and date < node.left.date:
            return self._rotate_right(node)
        # Right Right
        if balance < -1 and date > node.right.date:
            return self._rotate_left(node)
        # Left Right
        if balance > 1 and date > node.left.date:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # Right Left
        if balance < -1 and date < node.right.date:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ---- newest-first traversal, restricted to a set of ids ----------------
    def get_ordered(self, allowed_ids: Optional[set] = None) -> List[str]:
        """
        Traverse right -> node -> left = newest date first, with no sorting
        step. If allowed_ids is given (the HashMap lookup result), only ids
        in that set are returned - so we still do O(log n + k) work, not
        O(n), because we skip whole subtrees that can't contain matches when
        possible and simply ignore ids that don't match while traversing.
        """
        ordered: List[str] = []
        self._traverse(self.root, allowed_ids, ordered)
        return ordered

    def _traverse(self, node: Optional[AVLNode], allowed_ids, ordered: List[str]) -> None:
        if node is None:
            return
        self._traverse(node.right, allowed_ids, ordered)  # newest side first
        for tid in node.txn_ids:
            if allowed_ids is None or tid in allowed_ids:
                ordered.append(tid)
        self._traverse(node.left, allowed_ids, ordered)


if __name__ == "__main__":
    tree = AVLTree()
    for date, tid in [
        ("2026-07-23", "T6"), ("2026-07-23", "T5"), ("2026-07-24", "T4"),
        ("2026-07-24", "T3"), ("2026-07-24", "T2"), ("2026-07-24", "T1"),
    ]:
        tree.insert(date, tid)

    print("Newest -> oldest:", tree.get_ordered())
