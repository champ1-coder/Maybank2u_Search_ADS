#pragma once
#include <string>
#include <iostream>

struct Transaction {
    std::string txn_id;
    std::string date;      // ISO format "YYYY-MM-DD" so string comparison == chronological order
    std::string merchant;
    std::string category;
    double amount;

    Transaction() = default;

    Transaction(std::string id, std::string d, std::string m, std::string c, double a)
        : txn_id(std::move(id)), date(std::move(d)), merchant(std::move(m)),
          category(std::move(c)), amount(a) {}
};

inline std::ostream& operator<<(std::ostream& os, const Transaction& t) {
    os << "Transaction(" << t.txn_id << ", " << t.date << ", " << t.merchant
       << ", " << t.category << ", RM" << t.amount << ")";
    return os;
}

inline std::string to_lower(const std::string& s) {
    std::string out = s;
    for (auto& c : out) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return out;
}
