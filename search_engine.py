"""
optimized/search_engine.py

Combines the HashMap inverted index (optimized/inverted_index.py) with the
AVL tree (optimized/avl_tree.py) into the single "Query" algorithm described
in report section 3.2, step 2:

    ALGORITHM Query(searchIndex, avlTree, query)
        matchingTransactions <- searchIndex[LOWERCASE(query)]   # O(1)
        results <- GetFromAVLTree(avlTree, matchingTransactions) # O(log n + k)
        RETURN results

One query powers BOTH the filter chips (Debit Card / M2U / Bill Payment...)
and the new search bar (merchant / amount / reference number), because both
are just different keys in the same index.
"""

from typing import List, Optional
import time

from optimized.inverted_index import InvertedIndex
from optimized.avl_tree import AVLTree
from baseline.linear_filter import Transaction


class OptimizedTransactionSystem:
    """The proposed MAE system: build once, query instantly forever after."""

    def __init__(self, transactions: List[Transaction]):
        self.index = InvertedIndex()
        self.tree = AVLTree()
        self._build(transactions)

    def _build(self, transactions: List[Transaction]) -> None:
        """Build both structures once - this is the only O(n) work we ever
        do. Every later filter/search is O(1) + O(log n + k)."""
        self.index.build(transactions)
        for txn in transactions:
            self.tree.insert(txn.date, txn.txn_id)

    def add_transaction(self, txn: Transaction) -> None:
        """New transactions (e.g. a fresh QRPay payment) are indexed
        incrementally - no full rebuild needed."""
        self.index.add(txn)
        self.tree.insert(txn.date, txn.txn_id)

    def query(self, query_text: Optional[str]) -> List[Transaction]:
        """
        query_text is either:
          - a filter key, e.g. "debit_card", "m2u", "bill_payment" (from a
            filter chip tap), or
          - a free-typed search term, e.g. "shopee", "45.90" (from the
            search bar).
        Both go through the exact same code path.
        """
        if not query_text:
            # "Transaction History" (no filter) - AVL tree already has
            # everything in order, no HashMap lookup needed.
            ordered_ids = self.tree.get_ordered()
        else:
            matching_ids = set(self.index.lookup(query_text))
            if not matching_ids:
                return []
            ordered_ids = self.tree.get_ordered(allowed_ids=matching_ids)

        return self.index.get_transactions(ordered_ids)

    def query_with_timing(self, query_text: Optional[str]):
        start = time.perf_counter()
        results = self.query(query_text)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return results, elapsed_ms


if __name__ == "__main__":
    sample = [
        Transaction("T1", "2026-07-24", "m2u", "qrpay", "Afifah Syakirah", 18.00, "483712114Q"),
        Transaction("T2", "2026-07-24", "debit_card", "qrpay", "Mr DIY", 10.10, "MBBQR081904221"),
        Transaction("T3", "2026-04-11", "m2u", "qrpay", "Shopee", 45.90, "TXN998877"),
        Transaction("T4", "2026-07-24", "m2u", "duitnow", "Nur Amalia Izzati", 30.00, "0058030930"),
    ]
    engine = OptimizedTransactionSystem(sample)

    results, ms = engine.query_with_timing("shopee")
    print(f"Search 'shopee' -> {len(results)} result(s) in {ms:.4f} ms")
    for r in results:
        print(f"  {r.date}  {r.merchant}  RM {r.amount:.2f}")
