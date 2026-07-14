#pragma once
/*
 * Baseline approach: sequential (linear) search over a list of transactions.
 * Mirrors the original Maybank2u-style approach: every query scans records
 * from the beginning until matches are found.
 */
#include <vector>
#include <algorithm>
#include "transaction.h"

class BaselineTransactionStore {
public:
    void add(const Transaction& txn) {
        transactions_.push_back(txn);
    }

    // O(n) - scans every record, compares merchant name
    std::vector<Transaction> searchByMerchant(const std::string& merchant) const {
        std::vector<Transaction> results;
        std::string target = to_lower(merchant);
        for (const auto& txn : transactions_) {
            if (to_lower(txn.merchant) == target) {
                results.push_back(txn);
            }
        }
        return results;
    }

    // O(n) scan + O(k log k) sort - list is unordered so results need sorting
    std::vector<Transaction> searchByDateRange(const std::string& start, const std::string& end) const {
        std::vector<Transaction> results;
        for (const auto& txn : transactions_) {
            if (txn.date >= start && txn.date <= end) {
                results.push_back(txn);
            }
        }
        std::sort(results.begin(), results.end(),
                  [](const Transaction& a, const Transaction& b) { return a.date < b.date; });
        return results;
    }

    // O(n) - scans every record, compares category
    std::vector<Transaction> searchByCategory(const std::string& category) const {
        std::vector<Transaction> results;
        std::string target = to_lower(category);
        for (const auto& txn : transactions_) {
            if (to_lower(txn.category) == target) {
                results.push_back(txn);
            }
        }
        return results;
    }

    size_t size() const { return transactions_.size(); }

private:
    std::vector<Transaction> transactions_;
};
