"""
tests/test_comparison.py

Empirical testing script referenced in report section 4.2.

Generates synthetic transaction histories of different sizes (1,000 / 5,000
/ 10,000 - matching the report's test dataset sizes), then times:
  - Baseline:  filter_by_type("debit_card")   [linear scan + sort]
  - Optimized: query("debit_card")            [HashMap + AVL tree]
  - Optimized: query("shopee")                [new search feature -
               baseline has no equivalent, since it cannot search at all]

Run with:  python -m tests.test_comparison
(run from the repository root so the package imports resolve)
"""

import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baseline.linear_filter import Transaction, LinearFilterSystem
from optimized.search_engine import OptimizedTransactionSystem

TYPES = ["debit_card", "m2u", "bill_payment", "fund_transfer", "wu_transfer"]
CHANNELS = ["QRPay", "DuitNow", "FPX", "IBG"]
MERCHANTS = [
    "Shopee", "Mr DIY", "Rohana Laundry Enterprise", "Afifah Syakirah",
    "Nur Amalia Izzati", "Mohd Nazri Bin Mohd", "Grab", "Lazada",
    "TNB Electricity", "Astro Bill",
]


def generate_transactions(n: int, seed: int = 42) -> list:
    """
    Builds n synthetic transactions with roughly 20% "debit_card" type
    (matching the report's filter test) and roughly 5% "Shopee" merchant
    (matching the report's search test).
    """
    rng = random.Random(seed)
    transactions = []
    for i in range(n):
        txn_type = "debit_card" if rng.random() < 0.20 else rng.choice(TYPES)
        merchant = "Shopee" if rng.random() < 0.05 else rng.choice(MERCHANTS)
        date = f"2026-{rng.randint(1, 7):02d}-{rng.randint(1, 28):02d}"
        transactions.append(Transaction(
            txn_id=f"T{i}",
            date=date,
            type=txn_type,
            channel=rng.choice(CHANNELS),
            merchant=merchant,
            amount=round(rng.uniform(3, 500), 2),
            reference=f"TXN{rng.randint(100000, 999999)}",
        ))
    return transactions


def average_time_ms(fn, runs: int = 100) -> float:
    """Average a query's execution time over `runs` repeated calls, matching
    the report's methodology ('Average time over 100 queries')."""
    total = 0.0
    for _ in range(runs):
        _, ms = fn()
        total += ms
    return total / runs


def run_benchmark(sizes=(1000, 5000, 10000)):
    print(f"{'Records':>8} | {'Baseline filter (ms)':>20} | {'Optimized filter (ms)':>21} | "
          f"{'Optimized search (ms)':>21} | {'Speedup':>9}")
    print("-" * 95)

    for n in sizes:
        transactions = generate_transactions(n)

        baseline = LinearFilterSystem(transactions)
        optimized = OptimizedTransactionSystem(transactions)

        baseline_ms = average_time_ms(lambda: baseline.filter_with_timing("debit_card"))
        optimized_filter_ms = average_time_ms(lambda: optimized.query_with_timing("debit_card"))
        optimized_search_ms = average_time_ms(lambda: optimized.query_with_timing("shopee"))

        speedup = baseline_ms / optimized_filter_ms if optimized_filter_ms > 0 else float("inf")

        print(f"{n:>8} | {baseline_ms:>20.3f} | {optimized_filter_ms:>21.3f} | "
              f"{optimized_search_ms:>21.3f} | {speedup:>8.1f}x")


def test_results_match():
    """Sanity check: baseline and optimized must return the SAME set of
    transactions (same accuracy) for a filter - only speed should differ.
    Financial data must be 100% accurate (report constraint, section 1.2)."""
    transactions = generate_transactions(500)
    baseline = LinearFilterSystem(transactions)
    optimized = OptimizedTransactionSystem(transactions)

    baseline_ids = {t.txn_id for t in baseline.filter_by_type("debit_card")}
    optimized_ids = {t.txn_id for t in optimized.query("debit_card")}

    assert baseline_ids == optimized_ids, "Mismatch! Optimized results must match baseline exactly."
    print(f"PASS: baseline and optimized agree on {len(baseline_ids)} debit_card transactions.")


def test_ordering_is_newest_first():
    """Both systems must display newest -> oldest (report constraint)."""
    transactions = generate_transactions(500)
    optimized = OptimizedTransactionSystem(transactions)
    results = optimized.query("debit_card")
    dates = [t.date for t in results]
    assert dates == sorted(dates, reverse=True), "Optimized results are not newest-first!"
    print("PASS: optimized results are ordered newest -> oldest.")


if __name__ == "__main__":
    test_results_match()
    test_ordering_is_newest_first()
    print()
    run_benchmark()
