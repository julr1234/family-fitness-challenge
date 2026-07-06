import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Family Fitness Challenge", layout="wide")

st.title("🏆 Raich Family Fitness Challenge")

# ---------------- FAMILY ----------------
family = {
    "Julia": "👩",
    "Dad": "👨",
    "Mom": "👩",
    "Emma": "👧",
    "Grace": "👧",
    "Larry": "👨",
    "Aunt Melissa": "🧑",
    "Uncle Buck": "🧑",
    "Baba": "👩"
}

# ---------------- INPUT ----------------
st.header("Daily Check-In")

person = st.selectbox("Who are you?", list(family.keys()))
st.write("Hello,", person, family[person])

today = st.date_input("Today's Date", value=date.today())

activity_type = st.radio("Tracking Type", ["Steps", "Exercise Minutes"])

activity = st.number_input(
    "Amount",
    min_value=0,
    step=100 if activity_type == "Steps" else 5
)

filename = "data.csv"

# ---------------- LOAD DATA ----------------
def load_data(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=["Date", "Person", "Type", "Amount"])

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df = load_data(filename)

# ---------------- SUBMIT ----------------
if st.button("Submit 🚀"):
    new_row = pd.DataFrame([{
        "Date": pd.to_datetime(today),
        "Person": person,
        "Type": activity_type,
        "Amount": activity
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(filename, index=False)

    st.success("Saved!")
    st.rerun()

# =========================================================
# 🔒 PERSON FILTER (CORE OF APP)
# =========================================================
person_df = df[df["Person"] == person].copy()
person_steps = person_df[person_df["Type"] == "Steps"].copy()

# =========================================================
# 📊 TABS (REAL APP STRUCTURE)
# =========================================================
tab1, tab2, tab3 = st.tabs(["📋 My Dashboard", "🏆 Leaderboard", "📊 Insights"])

# =========================================================
# 📋 TAB 1 — PERSONAL DASHBOARD
# =========================================================
with tab1:
    st.header(f"📋 {person}'s Dashboard")

    st.dataframe(person_df.sort_values("Date", ascending=False))

    total_steps = person_steps["Amount"].sum()
    total_minutes = person_df[person_df["Type"] == "Exercise Minutes"]["Amount"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Steps", int(total_steps))
    col2.metric("Exercise Minutes", int(total_minutes))

    # ⭐ TOP 5 AVERAGE
    st.subheader("⭐ Top 5 Day Average (Steps)")

    if len(person_steps) > 0:
        daily = person_steps.groupby("Date")["Amount"].sum()
        top5_avg = daily.sort_values(ascending=False).head(5).mean()
    else:
        top5_avg = 0

    st.metric("Top 5 Avg Steps", int(top5_avg))

    # 🥇 PERSONAL BEST DAY
    st.subheader("🥇 Personal Best Day")

    if len(person_steps) > 0:
        daily = person_steps.groupby("Date")["Amount"].sum()
        best_day = daily.idxmax()
        best_value = daily.max()
        st.success(f"{best_day.date()} — {int(best_value)} steps")
    else:
        st.info("No step data yet.")

    # 🏅 BADGES
    st.subheader("🏅 Badges")

    badges = []

    if total_steps >= 100000:
        badges.append("🔥 100K Club")
    if total_steps >= 50000:
        badges.append("🏃 50K Club")
    if total_steps >= 20000:
        badges.append("🚶 Active Walker")

    active_days = person_df["Date"].dt.date.nunique()
    if active_days >= 5:
        badges.append("📅 Consistent Tracker")

    if badges:
        for b in badges:
            st.write("🏅", b)
    else:
        st.write("No badges yet 💪")

    # 🔥 STREAK
    st.subheader("🔥 Streak")

    if len(person_df) > 0:
        dates = sorted(person_df["Date"].dropna().dt.date.unique())

        longest = current = 0
        last = None

        for d in dates:
            if last and (d - last).days == 1:
                current += 1
            else:
                current = 1

            longest = max(longest, current)
            last = d

        st.metric("Longest Streak", longest)
    else:
        st.metric("Longest Streak", 0)

    # 📈 CHART
    st.subheader("📈 Steps Over Time")

    if len(person_steps) > 0:
        chart = person_steps.groupby("Date")["Amount"].sum().sort_index()
        st.line_chart(chart)
    else:
        st.info("No step data yet.")

# =========================================================
# 🏆 TAB 2 — LEADERBOARD
# =========================================================
with tab2:
    st.header("🏆 Family Leaderboard (Steps Only)")

    steps_df = df[df["Type"] == "Steps"]

    if len(steps_df) > 0:
        leaderboard = steps_df.groupby("Person")["Amount"].sum().sort_values(ascending=False)

        st.success(f"👑 Leader: {leaderboard.idxmax()}")

        st.dataframe(leaderboard.rename("Total Steps"))

        st.bar_chart(leaderboard)
    else:
        st.info("No step data yet.")

# =========================================================
# 📊 TAB 3 — INSIGHTS
# =========================================================
with tab3:
    st.header("📊 Insights")

    if len(df) > 0:
        steps_df = df[df["Type"] == "Steps"]

        top = steps_df.groupby("Person")["Amount"].sum().idxmax()
        st.info(f"🔥 Most Steps Overall: {top}")

        st.write("Average steps per person:")
        st.dataframe(steps_df.groupby("Person")["Amount"].mean())

    else:
        st.info("No data yet.")