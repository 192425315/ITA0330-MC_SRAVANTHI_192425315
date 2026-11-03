"""Task 9: Cellular Network Strategy - performance implementation.

This reproduces the Task 9 modelled results for Macrocell, Small-cell and
HetNet strategies. Values are illustrative assumptions, not field measurements.
Run: python task09_implementation.py
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------- 1. INPUT PARAMETERS -----------------------
USER_LOADS = [1_000, 10_000, 25_000, 50_000]
AVERAGE_RATE_MBPS = 0.25

STRATEGIES = {
    "Macrocell": {"capacity_gbps": 12.0, "handovers_per_user_hour": 0.5},
    "Small cell": {"capacity_gbps": 16.0, "handovers_per_user_hour": 3.0},
    "HetNet": {"capacity_gbps": 24.0, "handovers_per_user_hour": 1.5},
}

OUTPUT_DIR = Path(__file__).resolve().parent / "task09_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------- 2. CALCULATE RESULTS -----------------------
rows = []
for users in USER_LOADS:
    demand_gbps = users * AVERAGE_RATE_MBPS / 1000

    for strategy, config in STRATEGIES.items():
        capacity = config["capacity_gbps"]
        utilization = demand_gbps / capacity
        throughput = min(demand_gbps, capacity)

        # Illustrative delay formula used in the assignment model.
        # It is NOT a validated 5G latency formula.
        if utilization >= 0.95:
            delay_ms = 200.0
        else:
            delay_ms = 20 + (50 * utilization**2 / (1 - utilization))

        handovers = round(users * config["handovers_per_user_hour"])

        rows.append({
            "Users": users,
            "Strategy": strategy,
            "Demand_Gbps": demand_gbps,
            "Throughput_Gbps": throughput,
            "Utilization_Percent": utilization * 100,
            "Estimated_Delay_ms": delay_ms,
            "Handoffs_Per_Hour": handovers,
        })

df = pd.DataFrame(rows)

# Save complete experiment data.
df.to_csv(OUTPUT_DIR / "task09_all_results.csv", index=False)

# Create wide-format tables similar to the Task 9 tables in the report.
for metric, filename in [
    ("Throughput_Gbps", "throughput_table.csv"),
    ("Utilization_Percent", "utilization_table.csv"),
    ("Estimated_Delay_ms", "delay_table.csv"),
]:
    table = df.pivot(index="Users", columns="Strategy", values=metric)
    table.to_csv(OUTPUT_DIR / filename)

handoff_table = pd.DataFrame([
    {
        "Strategy": name,
        "Assumed handovers/user/hour": cfg["handovers_per_user_hour"],
        "Estimated events/hour at 50,000 users": round(
            50_000 * cfg["handovers_per_user_hour"]
        ),
    }
    for name, cfg in STRATEGIES.items()
])
handoff_table.to_csv(OUTPUT_DIR / "handoff_table.csv", index=False)

# ----------------------- 3. PRINT TABLES -----------------------
print("\nTASK 9 - CELLULAR NETWORK PERFORMANCE RESULTS")
print("All results below are modelled estimates based on stated assumptions.\n")
print("COMPLETE RESULTS")
print(df.round(2).to_string(index=False))

for metric, heading in [
    ("Throughput_Gbps", "THROUGHPUT (Gbps)"),
    ("Utilization_Percent", "CAPACITY UTILIZATION (%)"),
    ("Estimated_Delay_ms", "ILLUSTRATIVE DELAY (ms)"),
]:
    print(f"\n{heading}")
    print(df.pivot(index="Users", columns="Strategy", values=metric).round(2))

print("\nHANDOFF ACTIVITY AT 50,000 USERS")
print(handoff_table.to_string(index=False))

# ----------------------- 4. GENERATE GRAPHS -----------------------
chart_specs = [
    ("Throughput_Gbps", "Throughput (Gbps)",
     "Throughput by User Load", "throughput_comparison.png"),
    ("Utilization_Percent", "Capacity utilization (%)",
     "Capacity Utilization by User Load", "utilization_comparison.png"),
    ("Estimated_Delay_ms", "Estimated delay (ms)",
     "Illustrative Delay by User Load", "delay_comparison.png"),
    ("Handoffs_Per_Hour", "Estimated handoffs per hour",
     "Handoff Activity by User Load", "handoff_comparison.png"),
]

for metric, y_label, title, filename in chart_specs:
    plt.figure(figsize=(9, 5.5))
    for strategy in STRATEGIES:
        subset = df[df["Strategy"] == strategy]
        plt.plot(
            subset["Users"], subset[metric],
            marker="o", linewidth=2, label=strategy
        )
    plt.xlabel("Number of active users")
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(USER_LOADS, [f"{x:,}" for x in USER_LOADS])
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=200)
    plt.close()

print(f"\nDone. Tables and graphs are saved in: {OUTPUT_DIR.resolve()}")
print("Note: handoff counts are assumed-rate estimates, not measured handover events.")
