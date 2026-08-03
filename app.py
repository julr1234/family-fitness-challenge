from google_sheets import load_sheet, save_sheet

import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo


# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="Raich Family Fitness Challenge",
    page_icon="🏆",
    layout="wide"
)
if "checkin_person" not in st.session_state:
    st.session_state.checkin_person = "Julia"

st.title("🏆 Raich Family Fitness Challenge")
st.caption("July 27, 2026 – October 18, 2026")


# =====================================================
# CHALLENGE SETTINGS
# =====================================================

CHALLENGE_START = pd.Timestamp("2026-07-27")
CHALLENGE_WEEKS = 12
FAMILY_GOAL = 5_000_000

DATA_FILE = "data.csv"

# Use Eastern Time so the challenge does not roll over to the next day
# early when the app is running on a server in a different timezone.
APP_TIMEZONE = ZoneInfo("America/New_York")

def app_today():
    return datetime.now(APP_TIMEZONE).date()


# =====================================================
# FAMILY
# =====================================================

family = {
    "Julia": "👩",
    "Dad": "👨",
    "Mom": "👩",
    "Emma": "👧",
    "Grace": "👧",
    "Larry": "👨",
    "Uncle Buck": "🧑",
    "Uncle Matt": "👨",
    "Aunt Melissa": "👩",
    "Aunt Amanda": "👩",
    "Seraphina": "👧",
    "Baba": "👵"
}


# =====================================================
# DATA FUNCTIONS
# =====================================================

def load_data():

    columns = [
        "Date",
        "Person",
        "Type",
        "Amount",
        "Week"
    ]

    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        df = pd.read_csv(DATA_FILE)

    else:
        df = pd.DataFrame(columns=columns)


    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    df = df.dropna(
        subset=["Date"]
    )


    if len(df) > 0:

        df["Week"] = (
            (
                df["Date"] - CHALLENGE_START
            ).dt.days // 7
        ) + 1

        df["Week"] = (
            df["Week"]
            .clip(1, CHALLENGE_WEEKS)
            .astype(int)
        )

    else:

        df["Week"] = pd.Series(
            dtype="int"
        )


    return df



# =====================================================
# CALCULATION FUNCTIONS
# =====================================================

def get_steps(df):

    return df[
        df["Type"] == "Steps"
    ]



def get_exercise(df):

    return df[
        df["Type"] == "Exercise Minutes"
    ]



def family_total_steps(df):

    return int(
        get_steps(df)["Amount"].sum()
    )



def current_week():

    week = (
        (
            pd.Timestamp(app_today())
            - CHALLENGE_START
        ).days // 7
    ) + 1

    return min(
        max(week, 1),
        CHALLENGE_WEEKS
    )



def today_checkins(df):

    today = pd.Timestamp(
        app_today()
    )

    return df[
        df["Date"] == today
    ]["Person"].nunique()



def calculate_current_streak(person_df):

    if len(person_df) == 0:
        return 0

    dates = sorted(
        person_df["Date"]
        .dt.date
        .unique()
    )

    if len(dates) == 0:
        return 0


    streak = 1

    for i in range(
        len(dates)-1,
        0,
        -1
    ):

        if (
            dates[i]
            -
            dates[i-1]
        ).days == 1:

            streak += 1

        else:
            break


    if (
        dates[-1] != app_today()
        and
        dates[-1] != app_today() - timedelta(days=1)
    ):
        return 0


    return streak



def calculate_longest_streak(person_df):

    if len(person_df) == 0:
        return 0

    dates = sorted(
        person_df["Date"]
        .dt.date
        .unique()
    )

    longest = 1
    current = 1


    for i in range(1, len(dates)):

        if (
            dates[i]
            -
            dates[i-1]
        ).days == 1:

            current += 1
            longest = max(
                longest,
                current
            )

        else:

            current = 1


    return longest



# =====================================================
# LOAD DATA
# =====================================================

df = load_sheet()

week = current_week()

steps_df = get_steps(df)

exercise_df = get_exercise(df)


# =====================================================
# TABS
# =====================================================

page = st.radio(
    "Navigation",
    [
        "🏠 Home",
        "✍️ Check-In",
        "📋 My Dashboard",
        "🏆 Leaderboards",
        "📊 Insights"
    ],
    horizontal=True
)


# =====================================================
# TAB 1 - HOME
# =====================================================

if page == "🏠 Home":

    st.header(
        f"Week {week} of {CHALLENGE_WEEKS}"
    )

    st.subheader(
        "🏁 Family Goal"
    )

    total_steps = family_total_steps(df)

    progress = (
        total_steps
        /
        FAMILY_GOAL
    )

    st.progress(
        min(progress, 1.0)
    )

    st.write(
        f"**{total_steps:,} / {FAMILY_GOAL:,} steps**"
    )

    remaining = max(
        FAMILY_GOAL - total_steps,
        0
    )

    st.write(
        f"**{remaining:,} steps remaining**"
    )

    st.write(
        f"👣 Today's Check-ins: "
        f"{today_checkins(df)} / {len(family)}"
    )


    st.divider()


    if len(steps_df) > 0:

        weekly = (
            steps_df[
                steps_df["Week"] == week
            ]
            .groupby("Person")["Amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if len(weekly):

            st.subheader(
                "👑 Current Weekly Leader"
            )

            st.success(
                weekly.index[0]
            )

    else:

        st.info(
            "Start logging steps tomorrow!"
        )


# =====================================================
# TAB 2 - CHECK-IN
# =====================================================

elif page == "✍️ Check-In":

    st.header(
        "✍️ Daily Check-In"
    )

    person = st.selectbox(
    "Who are you?",
    list(family.keys()),
    key="checkin_person"
    )

    st.write(
        f"{family[person]} {person}"
    )


    entry_date = st.date_input(
        "Date",
        value=app_today()
    )


    activity_type = st.radio(
        "Tracking Type",
        [
            "Steps",
            "Exercise Minutes"
        ],
        horizontal=True
    )


    if activity_type == "Steps":

        amount = st.number_input(
            "Steps",
            min_value=0,
            step=100
        )

    else:

        amount = st.number_input(
            "Exercise Minutes",
            min_value=0,
            step=5
        )


    existing = df[
        (
            df["Person"]
            ==
            person
        )
        &
        (
            df["Date"]
            ==
            pd.Timestamp(entry_date)
        )
        &
        (
            df["Type"]
            ==
            activity_type
        )
    ]


    if len(existing) > 0:

        st.warning(
            "You already entered this activity for this date."
        )


        if st.button(
            "Update Existing Entry"
        ):

            index = existing.index[0]

            df.loc[
                index,
                "Amount"
            ] = amount

            save_sheet(df)

            st.success(
                "Updated!"
            )

        


    else:


        if st.button(
            "Submit 🚀"
        ):
            st.write("BUTTON WORKED")
            new_row = pd.DataFrame(
                [
                    {
                        "Date":
                            pd.Timestamp(entry_date),

                        "Person":
                            person,

                        "Type":
                            activity_type,

                        "Amount":
                            amount,

                        "Week":
                            (
                                (
                                    pd.Timestamp(entry_date)
                                    -
                                    CHALLENGE_START
                                ).days // 7
                            ) + 1
                    }
                ]
            )


            df = pd.concat(
                [
                    df,
                    new_row
                ],
                ignore_index=True
            )


            save_sheet(df)


            st.success(
                "Saved!"
            )

            



# =====================================================
# TAB 3 - DASHBOARD
# =====================================================

elif page == "📋 My Dashboard":

    st.header(
        "📋 My Dashboard"
    )


    selected_person = st.selectbox(
        "Select Person",
        list(family.keys()),
        key="dashboard_person"
    )


    person_df = df[
        df["Person"]
        ==
        selected_person
    ]


    person_steps = person_df[
        person_df["Type"]
        ==
        "Steps"
    ]


    person_minutes = person_df[
        person_df["Type"]
        ==
        "Exercise Minutes"
    ]


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "👣 Total Steps",
        f"{int(person_steps['Amount'].sum()):,}"
    )


    col2.metric(
        "💪 Exercise Minutes",
        int(person_minutes["Amount"].sum())
    )


    col3.metric(
        "🔥 Current Streak",
        calculate_current_streak(
            person_df
        )
    )


    col4, col5 = st.columns(2)


    col4.metric(
        "🏆 Longest Streak",
        calculate_longest_streak(
            person_df
        )
    )


    if len(person_steps):

        daily = (
            person_steps
            .groupby("Date")["Amount"]
            .sum()
        )

        col5.metric(
            "🥇 Best Day",
            f"{int(daily.max()):,}"
        )


    st.divider()


    st.subheader(
        "✏️ Edit My Entries"
    )


    editable = person_df.copy()


    if len(editable):

        editable["Date"] = (
            editable["Date"]
            .dt.date
        )


        edited = st.data_editor(
            editable,
            use_container_width=True,
            hide_index=True
        )


        if st.button(
            "💾 Save Changes"
        ):

            edited["Date"] = pd.to_datetime(
                edited["Date"]
            )

            df = df[
                df["Person"]
                !=
                selected_person
            ]

            df = pd.concat(
                [
                    df,
                    edited
                ],
                ignore_index=True
            )

            save_sheet(df)

            st.success(
                "Changes saved!"
            )




    else:

        st.info(
            "No entries yet."
        )
# =====================================================
# TAB 4 - LEADERBOARDS
# =====================================================

elif page == "🏆 Leaderboards":

    st.header(
        "🏆 Leaderboards"
    )


    # -----------------------------
    # Overall Steps
    # -----------------------------

    st.subheader(
        "👣 Overall Steps"
    )


    if len(steps_df):

        overall = (
            steps_df
            .groupby("Person")["Amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        st.bar_chart(
            overall
        )


        st.dataframe(
            overall.rename(
                "Total Steps"
            ),
            use_container_width=True
        )

    else:

        st.info(
            "No step data yet."
        )


    st.divider()


    # -----------------------------
    # Weekly Top 5 Average
    # -----------------------------

    st.subheader(
        "⭐ Weekly Top 5 Average"
    )

    # Let the family move backward through completed weeks.
    week_options = list(range(1, week + 1))

    selected_week = st.selectbox(
        "View Week",
        week_options,
        index=len(week_options) - 1,
        format_func=lambda w: (
            f"Week {w}" + (" (Current)" if w == week else "")
        )
    )

    selected_week_steps = steps_df[
        steps_df["Week"] == selected_week
    ]

    # Start with every family member so people with no entries
    # still appear in the selected week's table.
    weekly_averages = pd.Series(
        0.0,
        index=list(family.keys()),
        name="Top 5 Average"
    )

    if len(selected_week_steps):

        daily_week = (
            selected_week_steps
            .groupby(
                [
                    "Person",
                    "Date"
                ]
            )["Amount"]
            .sum()
            .reset_index()
        )

        calculated = (
            daily_week
            .groupby("Person")["Amount"]
            .apply(
                lambda x: x.nlargest(5).mean()
            )
        )

        weekly_averages.update(calculated)

        weekly_averages = weekly_averages.sort_values(
            ascending=False
        )

        champion = weekly_averages.index[0]

        # Only call someone champion if they actually logged steps.
        if weekly_averages[champion] > 0:
            st.success(
                f"🥇 Week {selected_week} Champion: {champion}"
            )

        st.bar_chart(
            weekly_averages
        )

        display_averages = weekly_averages.round().astype(int)

        st.dataframe(
            display_averages.rename(
                "Top 5 Average Steps"
            ).to_frame(),
            use_container_width=True
        )

        st.caption(
            "Everyone is shown. The average is based on each person's "
            "five highest step days during that week."
        )

    else:

        st.info(
            f"No step data logged for Week {selected_week} yet."
        )

        st.dataframe(
            weekly_averages.astype(int).rename(
                "Top 5 Average Steps"
            ).to_frame(),
            use_container_width=True
        )

    st.divider()


    # -----------------------------
    # Exercise Minutes
    # ----------------------------


    st.subheader(
        "💪 Exercise Minutes"
    )


    if len(exercise_df):

        exercise_board = (
            exercise_df
            .groupby("Person")
            ["Amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        st.bar_chart(
            exercise_board
        )


        st.dataframe(
            exercise_board.rename(
                "Minutes"
            ),
            use_container_width=True
        )


    else:

        st.info(
            "No exercise data yet."
        )



# =====================================================
# TAB 5 - INSIGHTS
# =====================================================

elif page == "📊 Insights":

    st.header(
        "📊 Insights"
    )


    # -----------------------------
    # Weekly Comparison
    # -----------------------------

    st.subheader(
        "📈 Weekly Family Progress"
    )


    if len(steps_df):

        weekly_family = (
            steps_df
            .groupby(
                [
                    "Week",
                    "Person"
                ]
            )["Amount"]
            .sum()
            .unstack(
                fill_value=0
            )
        )


        st.line_chart(
            weekly_family
        )


    else:

        st.info(
            "No data yet."
        )


    st.divider()


    # -----------------------------
    # Hall of Fame
    # -----------------------------

    st.subheader(
        "🏆 Hall of Fame"
    )


    if len(steps_df):

        daily_records = (
            steps_df
            .groupby(
                [
                    "Person",
                    "Date"
                ]
            )["Amount"]
            .sum()
        )


        best_day = (
            daily_records
            .idxmax()
        )


        best_value = (
            daily_records
            .max()
        )


        st.success(
            f"🥇 Highest Day: "
            f"{best_day[0]} "
            f"({best_day[1].date()}) "
            f"- {int(best_value):,} steps"
        )


    # Longest streak

    streaks = {}


    for member in family:

        member_data = df[
            df["Person"]
            ==
            member
        ]

        streaks[member] = (
            calculate_longest_streak(
                member_data
            )
        )


    streak_holder = max(
        streaks,
        key=streaks.get
    )


    st.success(
        f"🔥 Longest Streak: "
        f"{streak_holder} "
        f"({streaks[streak_holder]} days)"
    )


    st.divider()


    # -----------------------------
    # Badges
    # -----------------------------

    st.subheader(
        "🏅 Challenge Badges"
    )


    total_steps = family_total_steps(df)


    badges = []


    if total_steps >= 100000:

        badges.append(
            "👟 Family 100K Club"
        )


    if total_steps >= 500000:

        badges.append(
            "🔥 Family Half Million Club"
        )


    if total_steps >= 1000000:

        badges.append(
            "🚀 One Million Steps"
        )


    if len(steps_df):

        if steps_df["Amount"].max() >= 20000:

            badges.append(
                "💥 20K Step Day"
            )


    if badges:

        for badge in badges:

            st.write(
                badge
            )

    else:

        st.info(
            "Badges coming soon!"
        )


    st.divider()


    # -----------------------------
    # Pace Tracker
    # -----------------------------

    st.subheader(
        "🏁 5 Million Step Pace"
    )


    days_elapsed = max(
        (
            pd.Timestamp(app_today())
            -
            CHALLENGE_START
        ).days,
        1
    )


    average_daily = (
        total_steps
        /
        days_elapsed
    )


    total_days = (
        CHALLENGE_WEEKS
        *
        7
    )


    remaining_days = max(
        total_days - days_elapsed,
        1
    )


    needed_daily = (
        max(
            FAMILY_GOAL - total_steps,
            0
        )
        /
        remaining_days
    )


    col1, col2 = st.columns(2)


    col1.metric(
        "Current Daily Average",
        f"{average_daily:,.0f}"
    )


    col2.metric(
        "Needed Daily Average",
        f"{needed_daily:,.0f}"
    )


    if average_daily >= needed_daily:

        st.success(
            "🎉 Family is on pace for 5 million steps!"
        )

    else:

        st.warning(
            "🚶 Family needs a little more movement to stay on pace."
        )


st.divider()

st.caption(
    "❤️ Built for the Raich Family 12-Week Fitness Challenge"
)