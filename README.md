# MAE Transaction Optimization

TEB1113: Algorithm and Data Structure — Semester Jan 2026 Group Assignment

## Overview

This project improves the Maybank2u (MAE) transaction history feature with:

1. **Faster Filters** — the existing filter chips (Debit Card History, M2U History,
   Bill Payment, Fund Transfer, WU Transfer Status) go from a ~3 second scan-and-sort
   to an instant lookup.
2. **New Search Bar** — a brand new feature letting users type a merchant name,
   amount, or reference number to jump straight to matching transactions.

## How it works

| Structure | Role |
|---|---|
| **Array / List** (baseline) | Current MAE behaviour: scan every transaction, then sort. `O(n log n)`. |
| **HashMap (inverted index)** | Maps a keyword (type, channel, merchant, amount, reference) straight to the matching transaction ids. `O(1)` average lookup. Powers both the filters and the search bar. |
| **AVL Tree** | Keeps transactions balanced and sorted by date so results are already newest-to-oldest — no separate sort step needed. `O(log n)` insert/traverse. |

## Repository structure

```
MAE-Transaction-Optimization/
├── baseline/
│   └── linear_filter.py       # Current MAE behaviour (linear scan + sort)
├── optimized/
│   ├── inverted_index.py      # HashMap for filters + search
│   ├── avl_tree.py            # Sorted by date (no sorting needed)
│   └── search_engine.py       # Combined solution
├── tests/
│   └── test_comparison.py     # Correctness checks + performance benchmark
├── mock_app/
│   └── index.html             # Side-by-side visual mock: baseline vs optimized
└── README.md
```

## Example

- Before: tap "Debit Card" → wait ~3 seconds → scroll through 2,000 transactions to find one from Shopee.
- After: type "Shopee" → instantly see only the ~5 matching transactions, already sorted newest-first.

## Setup

1. Clone the repository.
2. No external dependencies are required — everything uses the Python standard library.
3. Run the correctness checks and benchmark:
   ```bash
   cd MAE-Transaction-Optimization
   python3 -m tests.test_comparison
   ```
4. Open `mock_app/index.html` directly in a browser (no server needed) to see the
   side-by-side baseline vs optimized mock app.

## Results

- Filters resolve via `O(1)` HashMap lookup + `O(log n + k)` AVL traversal instead of
  `O(n log n)` linear scan and sort.
- Brand new search feature with no baseline equivalent.
- Dramatically less scrolling: results are narrowed to only what the user is looking
  for instead of the entire filtered category.

## Contributors

- Qaseeh Dania Aisyah binti Ahmad Shahrel — 24006482
- Nur Amalia Izzati binti Mohamad Azni — 24005350
- Husna binti Shahar — 24005806
- Humaira Rayyan binti Haslah — 24005364
