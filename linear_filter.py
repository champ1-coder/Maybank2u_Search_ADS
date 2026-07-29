"""
baseline/linear_filter.py

Simulates the CURRENT Maybank2u (MAE) transaction history behaviour.

How the real app works today (see report section 3.1):
    1. User taps a filter chip: "Transaction History", "Debit Card History",
       "M2U History", "Bill Payment", "Fund Transfer", "WU Transfer Status".
    2. The app scans EVERY transaction in the account, one by one, and keeps
       only the ones that match the filter type.        -> O(n)
    3. The matches are sorted newest -> oldest so the newest transaction is
       always on top.                                     -> O(n log n)
    4. There is NO date-range filter and NO keyword search, so to find an old
       transaction the user must scroll through all of the matches.

This module is intentionally "dumb" - it does not build any index ahead of
time. Every single query re-scans the full transaction list, which is why
the response time grows with the number of transactions a user has.
"""

from dataclasses import dataclass
from typing import List, Optional
import time


@dataclass
class Transaction:
    """One row in a user's transaction history."""
    txn_id: str
    date: str          # ISO format "YYYY-MM-DD" so string sort == date sort
    type: str          # e.g. "debit_card", "m2u", "bill_payment", "fund_transfer"
    channel: str        # e.g. "QRPay", "DuitNow", "FPX"
    merchant: str       # e.g. "Shopee", "Mr DIY", "Rohana Laundry Enterprise"
    amount: float
    reference: str      # e.g. "TXN123456"


class LinearFilterSystem:
    """The baseline (current MAE) system: one big list, scanned every time."""

    def __init__(self, transactions: List[Transaction]):
        # Just a flat list - exactly how the current app stores things.
        self.transactions = transactions

    def filter_by_type(self, filter_type: Optional[str] = None) -> List[Transaction]:
        """
        ALGORITHM LinearFilterByType(transactionList, filterType)
            results <- empty list
            FOR EACH transaction IN transactionList
                IF transaction.type == filterType THEN
                    APPEND transaction TO results
            SORT results BY date DESCENDING
            RETURN results

        filter_type=None means "Transaction History" (show everything).
        """
        results = []

        # Step 1: scan ALL transactions one by one -> O(n)
        for txn in self.transactions:
            if filter_type is None or txn.type == filter_type:
                results.append(txn)

        # Step 2: sort newest -> oldest every single time -> O(n log n)
        results.sort(key=lambda t: t.date, reverse=True)

        # Step 3: return - the user must scroll through ALL of these,
        # there is no way to narrow further (no search, no date range).
        return results

    def filter_with_timing(self, filter_type: Optional[str] = None):
        """Same as filter_by_type but also returns how long it took (ms)."""
        start = time.perf_counter()
        results = self.filter_by_type(filter_type)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return results, elapsed_ms


if __name__ == "__main__":
    # Tiny smoke test using the transactions visible in the screenshots.
    sample = [
        Transaction("T1", "2026-07-24", "m2u", "QRPay", "Afifah Syakirah", 18.00, "483712114Q"),
        Transaction("T2", "2026-07-24", "debit_card", "QRPay", "Mr DIY", 10.10, "MBBQR081904221"),
        Transaction("T3", "2026-07-24", "m2u", "QRPay", "Afifah Syakirah", 12.78, "463566914Q"),
        Transaction("T4", "2026-07-24", "m2u", "DuitNow", "Nur Amalia Izzati", 30.00, "0058030930"),
        Transaction("T5", "2026-07-23", "m2u", "QRPay", "Rohana Laundry Enterprise", 6.00, "0058030930"),
        Transaction("T6", "2026-07-23", "m2u", "QRPay", "Mohd Nazri Bin Mohd", 5.50, "0058107262"),
    ]
    system = LinearFilterSystem(sample)
    hits, ms = system.filter_with_timing("m2u")
    print(f"Found {len(hits)} M2U transactions in {ms:.3f} ms (n={len(sample)})")
    for t in hits:
        print(f"  {t.date}  {t.merchant:<28}  RM {t.amount:.2f}")
