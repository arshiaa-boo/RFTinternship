
#Project 17 -- Customer Segmentation Analysis


import random
import statistics

# ---------------------------------------------
# 1. GENERATE SAMPLE DATASET
# ---------------------------------------------
random.seed(42)

customers = []
for i in range(1, 51):
    customer = {
        "customer_id": i,
        "age":         random.randint(18, 65),
        "spending":    round(random.uniform(500, 10000), 2),
        "visits":      random.randint(1, 30),
    }
    customers.append(customer)


# ---------------------------------------------
# 2. SEGMENT CUSTOMERS BY SPENDING LEVEL
# ---------------------------------------------
def get_spending_segment(spending):
    if spending >= 7000:
        return "High"
    elif spending >= 3000:
        return "Medium"
    else:
        return "Low"


for c in customers:
    c["segment"] = get_spending_segment(c["spending"])


# ---------------------------------------------
# 3. IDENTIFY HIGH-VALUE & LOW-ENGAGEMENT USERS
# ---------------------------------------------
avg_spending = statistics.mean(c["spending"] for c in customers)
avg_visits   = statistics.mean(c["visits"]   for c in customers)

high_value_customers = [c for c in customers if c["spending"] >= avg_spending * 1.3]
low_engagement_users = [c for c in customers if c["visits"]   <= 3]


# ---------------------------------------------
# 4. HELPER -- simple bar chart in the terminal
# ---------------------------------------------
def bar(value, max_value, width=30, char="#"):
    filled = int((value / max_value) * width)
    return char * filled + "-" * (width - filled)


# ---------------------------------------------
# 5. VISUALIZE -- SPENDING DISTRIBUTION
# ---------------------------------------------
def visualize_spending_distribution(customers):
    buckets = {"500-2500": 0, "2500-5000": 0, "5000-7500": 0, "7500-10000": 0}
    for c in customers:
        s = c["spending"]
        if s < 2500:
            buckets["500-2500"] += 1
        elif s < 5000:
            buckets["2500-5000"] += 1
        elif s < 7500:
            buckets["5000-7500"] += 1
        else:
            buckets["7500-10000"] += 1

    max_count = max(buckets.values())
    print("\n" + "=" * 55)
    print("  SPENDING DISTRIBUTION")
    print("=" * 55)
    for label, count in buckets.items():
        print(f"  Rs.{label:<12} | {bar(count, max_count)} {count:>2} customers")
    print("=" * 55)


# ---------------------------------------------
# 6. VISUALIZE -- CUSTOMER CATEGORIES
# ---------------------------------------------
def visualize_customer_categories(customers):
    seg_counts = {"High": 0, "Medium": 0, "Low": 0}
    seg_totals = {"High": 0.0, "Medium": 0.0, "Low": 0.0}

    for c in customers:
        seg = c["segment"]
        seg_counts[seg] += 1
        seg_totals[seg] += c["spending"]

    total     = len(customers)
    max_count = max(seg_counts.values())

    print("\n" + "=" * 55)
    print("  CUSTOMER CATEGORY BREAKDOWN")
    print("=" * 55)
    for seg in ["High", "Medium", "Low"]:
        count  = seg_counts[seg]
        avg_sp = seg_totals[seg] / count if count else 0
        pct    = (count / total) * 100
        print(f"  [{seg:<6}] | {bar(count, max_count)} {count:>2} ({pct:.1f}%)")
        print(f"           | Avg Spending: Rs.{avg_sp:,.2f}")
    print("=" * 55)


# ---------------------------------------------
# 7. PRINT KEY FINDINGS
# ---------------------------------------------
def print_key_findings(customers, high_value, low_engagement):
    print("\n" + "=" * 55)
    print("  KEY FINDINGS")
    print("=" * 55)
    print(f"  Total Customers   : {len(customers)}")
    print(f"  Average Spending  : Rs.{avg_spending:,.2f}")
    print(f"  Average Visits    : {avg_visits:.1f}")
    print(f"  High-Value Users  : {len(high_value)} customers"
          f" (spending >= Rs.{avg_spending * 1.3:,.0f})")
    print(f"  Low-Engagement    : {len(low_engagement)} customers (visits <= 3)")

    print("\n  Top 5 High-Value Customers:")
    top5 = sorted(high_value, key=lambda x: x["spending"], reverse=True)[:5]
    for c in top5:
        print(f"     ID {c['customer_id']:>3} | Age {c['age']} | "
              f"Rs.{c['spending']:>8,.2f} | Visits: {c['visits']}")

    print("\n  Low-Engagement Sample (first 5):")
    for c in low_engagement[:5]:
        print(f"     ID {c['customer_id']:>3} | Age {c['age']} | "
              f"Rs.{c['spending']:>8,.2f} | Visits: {c['visits']}")
    print("=" * 55)


# ---------------------------------------------
# 8. BONUS -- BUSINESS STRATEGIES
# ---------------------------------------------
def suggest_business_strategies():
    print("\n" + "=" * 55)
    print("  BUSINESS STRATEGIES")
    print("=" * 55)
    strategies = {
        "[HIGH] Segment": [
            "Launch VIP / loyalty rewards programme",
            "Offer exclusive early-access to new products",
            "Assign dedicated account managers",
        ],
        "[MEDIUM] Segment": [
            "Send personalised upsell / cross-sell emails",
            "Introduce tiered membership to push them higher",
            "Provide bundle discounts to increase spend",
        ],
        "[LOW] Segment": [
            "Re-engagement campaigns with strong discounts",
            "Push notifications / SMS for flash sales",
            "Understand pain-points via feedback surveys",
        ],
        "[LOW-ENGAGEMENT] Users": [
            "Trigger win-back email sequence",
            "Offer a compelling incentive for next visit",
            "Simplify the purchase journey / UX review",
        ],
    }
    for segment, tips in strategies.items():
        print(f"\n  {segment}")
        for tip in tips:
            print(f"    - {tip}")
    print("\n" + "=" * 55)


# ---------------------------------------------
# 9. MAIN
# ---------------------------------------------
if __name__ == "__main__":
    print("\n" + "*" * 55)
    print("Day 17")
    print("  Customer Segmentation Analysis")
    print("*" * 55)

    visualize_spending_distribution(customers)
    visualize_customer_categories(customers)
    print_key_findings(customers, high_value_customers, low_engagement_users)
    suggest_business_strategies()

    print("\nAnalysis complete.\n")