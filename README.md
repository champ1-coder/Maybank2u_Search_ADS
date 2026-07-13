# Maybank2u Transaction Search Optimizer

# Overview
Simulates transaction history search for a banking platform, comparing a baseline linear scan against an optimized hybrid indexing system (AVL Tree + Hash Map).

- **Baseline:** `std::vector` / Linear Scan — strict sequential search. Demonstrates the inefficiency of full-table scans (O(n)), where a single search must examine every single record leading to severe bottlenecks as transaction volumes grow to millions.
- **Optimized:** Hybrid Indexing (Hash Map + AVL Tree) — transactions are indexed by Merchant/Category (Hash Map) and Date (AVL Tree), allowing the system to jump directly to relevant records instead of scanning everything.
