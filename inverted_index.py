"""
optimized/inverted_index.py

The HashMap (inverted index) at the heart of our optimization (report 2.2.2).

Think of it like the index at the back of a textbook: instead of reading
every page to find a topic, you look the topic up once and it tells you
exactly which pages (transactions) to go to.

We build ONE index that serves two purposes:
    1. FASTER FILTERS  - key on transaction.type / transaction.channel
                          e.g. index["debit_card"] -> [txn ids...]
    2. SEARCH BAR       - key on merchant / amount / reference number
                          e.g. index["shopee"]     -> [txn ids...]

Building the index costs O(n) and is done ONCE (or incrementally whenever a
new transaction arrives). After that, every filter click or search keystroke
is an O(1) average-case dictionary lookup - no re-scanning the account.
"""

from collections import defaultdict
from typing import Dict, List, Set
import sys

sys.path.append("..")
from baseline.linear_filter import Transaction  # reuse the same data model


class InvertedIndex:
    """Maps lowercase keywords -> the set of transaction ids that match."""

    def __init__(self):
        # searchIndex = {
        #   "debit_card" -> {"T1", "T3", ...},   # filter key
        #   "shopee"     -> {"T1", "T3", ...},   # search key
        #   "45.90"      -> {"T3"},              # amount key
        #   "txn123"     -> {"T1"},              # reference key
        # }
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.by_id: Dict[str, Transaction] = {}

    def build(self, transactions: List[Transaction]) -> None:
        """
        ALGORITHM BuildSearchIndex(transactionList)
            FOR EACH transaction IN transactionList
                index[type]      += transaction
                index[channel]   += transaction
                index[merchant]  += transaction
                index[amount]    += transaction
                index[reference] += transaction
        """
        for txn in transactions:
            self.add(txn)

    def add(self, txn: Transaction) -> None:
        """Index a single transaction. O(1) - lets new transactions stream in
        without ever rebuilding the whole index from scratch."""
        self.by_id[txn.txn_id] = txn

        self.index[txn.type.lower()].add(txn.txn_id)
        self.index[txn.channel.lower()].add(txn.txn_id)

        for word in txn.merchant.lower().split():
            self.index[word.strip(".,")].add(txn.txn_id)

        self.index[str(txn.amount)].add(txn.txn_id)
        self.index[txn.reference.lower()].add(txn.txn_id)

    def lookup(self, query: str) -> List[str]:
        """
        ALGORITHM Query(searchIndex, query)
            RETURN searchIndex[LOWERCASE(query)]

        O(1) average case - straight to the matching transaction ids.
        Falls back to a prefix scan over index KEYS ONLY (never the full
        transaction list) so partial merchant names like "shop" still work.
        """
        query = query.strip().lower()
        if not query:
            return []

        if query in self.index:
            return list(self.index[query])

        # Partial / prefix match - still only touches index keys, not txns.
        matches: Set[str] = set()
        for key, txn_ids in self.index.items():
            if key.startswith(query):
                matches |= txn_ids
        return list(matches)

    def get_transactions(self, txn_ids: List[str]) -> List[Transaction]:
        return [self.by_id[tid] for tid in txn_ids if tid in self.by_id]


if __name__ == "__main__":
    sample = [
        Transaction("T1", "2026-07-24", "m2u", "qrpay", "Afifah Syakirah", 18.00, "483712114Q"),
        Transaction("T2", "2026-07-24", "debit_card", "qrpay", "Mr DIY", 10.10, "MBBQR081904221"),
        Transaction("T3", "2026-04-11", "m2u", "qrpay", "Shopee", 45.90, "TXN998877"),
    ]
    idx = InvertedIndex()
    idx.build(sample)

    print("Filter 'debit_card':", [t.merchant for t in idx.get_transactions(idx.lookup("debit_card"))])
    print("Search 'shopee'    :", [t.merchant for t in idx.get_transactions(idx.lookup("shopee"))])
