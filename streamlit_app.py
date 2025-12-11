import streamlit as st
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Japan Stay Days Calculator", page_icon="🗾", layout="centered")

st.title("🗾 Japan Stay Days Calculator (Streamlit Version)")
st.write(
    """
This tool helps you:

1. Calculate your total number of days stayed in Japan for a selected calendar year.
2. Find your **maximum stay within any rolling 365-day window**.
3. Automatically check against:
   - A **90-day limit per continuous stay** (short-term stay rule).
   - A **180-day limit within any 365 days** (rolling rule).
   
⚠️ This tool is for personal reference only and does **not** constitute legal or immigration advice.  
Always confirm the actual rules with official Japanese immigration sources.
"""
)

# ---------------------------------------------
# 1️⃣ Select year for annual calculation
# ---------------------------------------------
with st.sidebar:
    st.header("Settings")
    target_year = st.number_input("Target Year", min_value=2000, max_value=2100, value=date.today().year)
    st.write(f"Currently calculating: **{int(target_year)}**")

st.subheader("1️⃣ Enter your entry/exit date ranges")
st.caption(
    """
Note: If your stay overlaps multiple years (e.g., 2024-12-20 → 2025-01-10),  
enter it as-is. The calculator will only count the portion inside the selected year.
"""
)

num_trips = st.number_input("Number of date ranges", min_value=1, max_value=50, value=3)

trip_data = []
valid_intervals = []   # Valid for rolling 365-day calculations
longest_single_stay = 0  # For 90-day rule check

for i in range(int(num_trips)):
    st.markdown(f"#### Range {i + 1}")
    cols = st.columns(2)
    with cols[0]:
        start = st.date_input(
            "Entry Date (From)",
            key=f"start_{i}",
            value=date(date.today().year, 1, 1),
        )
    with cols[1]:
        end = st.date_input(
            "Exit Date (To)",
            key=f"end_{i}",
            value=date(date.today().year, 1, 5),
        )

    if end < start:
        st.error(f"❌ Range {i + 1}: Exit date cannot be earlier than entry date. This range will be ignored.")
        days_in_year = 0
        stay_length = 0
    else:
        # Continuous stay length for this range
        stay_length = (end - start).days + 1
        longest_single_stay = max(longest_single_stay, stay_length)

        # Store valid interval for rolling 365-day calculation
        valid_intervals.append((start, end))

        # Calculate annual days (intersection with selected year)
        year_start = date(int(target_year), 1, 1)
        year_end = date(int(target_year), 12, 31)

        effective_start = max(start, year_start)
        effective_end = min(end, year_end)

        if effective_start > effective_end:
            days_in_year = 0
        else:
            days_in_year = (effective_end - effective_start).days + 1

    trip_data.append(
        {
            "Range": f"{i + 1}",
            "Original Stay": f"{start} → {end}",
            "Stay Length (days)": stay_length,
            f"Days in {int(target_year)}": days_in_year,
        }
    )

# ---------------------------------------------
# 2️⃣ Show each range calculation
# ---------------------------------------------
st.markdown("---")
st.subheader("2️⃣ Calculation for Each Date Range")

total_days = sum(row[f"Days in {int(target_year)}"] for row in trip_data)

if trip_data:
    st.table(trip_data)

# ---------------------------------------------
# 3️⃣ Annual summary
# ---------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Annual Summary")

st.markdown(
    f"""
### 📌 Total days you stayed in Japan in **{int(target_year)}**:
## 🧮 **{total_days} days**
"""
)

# ---------------------------------------------
# 4️⃣ Annual threshold check (optional, custom)
# ---------------------------------------------
st.subheader("4️⃣ Annual Threshold Check (Optional)")

limit_enable = st.checkbox("Enable custom annual stay limit (e.g., 180 days)", value=False)

if limit_enable:
    limit_days = st.number_input("Set annual limit", min_value=1, max_value=365, value=180)
    if total_days > limit_days:
        st.error(f"⚠ Your stay of {total_days} days exceeds the annual limit of {limit_days}!")
    else:
        st.success(f"✅ Your stay of {total_days} days is within the annual limit of {limit_days}.")

# ---------------------------------------------
# 5️⃣ Rolling 12-month / 365-day window calculation
# ---------------------------------------------
st.markdown("---")
st.subheader("5️⃣ Rolling 365-Day Maximum Stay")

st.caption(
    """
This section finds the **maximum number of days you were in Japan within any continuous 365-day period**.  
This is often used for “12-month stay limit” style rules.
"""
)

max_days_365 = 0
window_start = None
window_end = None

if valid_intervals:
    # Collect all dates you were in Japan
    all_days = []
    for s, e in valid_intervals:
        delta = (e - s).days
        for d in range(delta + 1):
            all_days.append(s + timedelta(days=d))

    all_days = sorted(set(all_days))  # Remove duplicates & sort

    if all_days:
        # Sliding window calculation for any 365-day period
        i = 0
        j = 0
        n = len(all_days)
        max_i = 0
        max_j = 0

        while i < n:
            while j < n and (all_days[j] - all_days[i]) <= timedelta(days=364):
                j += 1
            window_size = j - i
            if window_size > max_days_365:
                max_days_365 = window_size
                max_i = i
                max_j = j - 1
            i += 1

        window_start = all_days[max_i]
        window_end = all_days[max_j]

        st.markdown(
            f"""
### 🔍 Rolling 365-day Result

- Maximum days stayed in any 365-day period:  
  👉 **{max_days_365} days**

- This maximum occurred roughly between:  
  👉 **{window_start} → {window_end}**

(These dates mark the "densest" 365-day period of your Japan stay.)
"""
        )

        # Optional custom rolling limit check
        rolling_limit_enable = st.checkbox("Enable custom rolling 365-day limit check", value=False)
        if rolling_limit_enable:
            rolling_limit_days = st.number_input("Set rolling 365-day limit", min_value=1, max_value=365, value=180)
            if max_days_365 > rolling_limit_days:
                st.error(
                    f"⚠ You exceeded the custom rolling limit: {max_days_365} days > allowed {rolling_limit_days} days."
                )
            else:
                st.success(
                    f"✅ Maximum 365-day stay is {max_days_365} days, within the limit of {rolling_limit_days} days."
                )
    else:
        st.info("No valid stay dates available for rolling calculation.")
else:
    st.info("No valid entry/exit ranges entered.")

# ---------------------------------------------
# 6️⃣ Auto-check against Japan-style 90-day & 180-day rules
# ---------------------------------------------
st.markdown("---")
st.subheader("6️⃣ Auto Check: 90-day Short Stay & 180-day Rolling Rule")

st.caption(
    """
This section automatically evaluates your input against two common constraints:
- **90-day limit per continuous stay** (each single visit should not exceed 90 days).
- **180-day limit within any 365 days** (total days in Japan in any 12-month window).
These are modeled as generic rules for your convenience; real legal rules may differ.
"""
)

# 90-day rule: per continuous stay
if longest_single_stay == 0:
    st.info("No valid stays to check for the 90-day rule.")
else:
    st.markdown(f"- Longest single continuous stay: **{longest_single_stay} days**")
    if longest_single_stay > 90:
        st.error("⚠ This exceeds a 90-day short-stay limit per visit.")
    else:
        st.success("✅ All continuous stays are within a 90-day per-visit limit.")

# 180-day rule: within any rolling 365 days
if max_days_365 == 0:
    st.info("Rolling 365-day data is not available yet (no valid stays).")
else:
    st.markdown(f"- Maximum days in any 365-day period: **{max_days_365} days**")
    if max_days_365 > 180:
        st.error("⚠ This exceeds a 180-day limit within a 365-day rolling window.")
    else:
        st.success("✅ Your maximum 365-day stay is within a 180-day rolling limit.")

st.info(
    """
💡 Notes & future ideas:  
- Actual immigration rules may depend on nationality, visa type, and latest laws.  
- You could extend this app with:
  - CSV import from your travel records or calendar
  - A visual timeline / calendar heatmap
  - Different pre-set profiles for various visa types
"""
)

)
