
import streamlit as st
from supabase import create_client
from datetime import date
import pandas as pd
from receipt import generate_fee_receipt
from student_statement import generate_student_statement



# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Student Fee Management",
    page_icon="📚",
    layout="wide"
)



# =========================================================
# DASHBOARD THEME AND PAID / UNPAID BUTTON COLORS
# =========================================================



st.markdown(
    """
    <style>

    /* ---------- MAIN APP ---------- */
    .stApp {
        background-color: #FFF5EA !important;
        color: #17365D !important;
    }

    /* Main content spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ---------- HEADINGS ---------- */
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #17365D !important;
        font-weight: 700 !important;
    }

    /* Regular text */
    .stApp p,
    .stApp label,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stWidgetLabel"] {
        color: #17365D !important;
    }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #17365D !important;
    }

    /* Sidebar navigation spacing */
    section[data-testid="stSidebar"]
    div[role="radiogroup"] {
        gap: 8px !important;
    }

    /* Larger sidebar options */
    section[data-testid="stSidebar"]
    div[role="radiogroup"] label {
        background-color: #FFFFFF !important;
        border: 1px solid #E3E8EF !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        min-height: 44px !important;
        margin-bottom: 5px !important;
        transition: all 0.2s ease-in-out;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label p {
        color: #17365D !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }

    /* Sidebar hover */
    section[data-testid="stSidebar"]
    div[role="radiogroup"] label:hover {
        background-color: #FFF0DF !important;
        border-color: #E87524 !important;
    }

    /* Selected sidebar option */
    section[data-testid="stSidebar"]
    div[role="radiogroup"] label:has(input:checked) {
        background-color: #FFF0DF !important;
        border: 2px solid #E87524 !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label:has(input:checked) p {
        color: #17365D !important;
        font-weight: 700 !important;
    }

    /* ---------- METRIC CARDS ---------- */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E6D9CA !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 2px 8px rgba(23, 54, 93, 0.06);
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] * {
        color: #17365D !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        color: #17365D !important;
        font-weight: 700 !important;
    }

    /* ---------- GENERAL BUTTONS ---------- */
    .stApp div[data-testid="stButton"] button {
        border-radius: 9px !important;
        font-weight: 600 !important;
        min-height: 40px !important;
        transition: all 0.2s ease-in-out;
    }

    /* Primary buttons: navy */
    .stApp div[data-testid="stButton"]
    button[data-testid="stBaseButton-primary"],
    .stApp div[data-testid="stButton"]
    button[kind="primary"] {
        background-color: #17365D !important;
        border: 1px solid #17365D !important;
        color: #FFFFFF !important;
    }

    .stApp div[data-testid="stButton"]
    button[data-testid="stBaseButton-primary"] p,
    .stApp div[data-testid="stButton"]
    button[kind="primary"] p {
        color: #FFFFFF !important;
    }

    .stApp div[data-testid="stButton"]
    button[data-testid="stBaseButton-primary"]:hover,
    .stApp div[data-testid="stButton"]
    button[kind="primary"]:hover {
        background-color: #254A78 !important;
        border-color: #254A78 !important;
    }

    /* Secondary buttons: white with navy text */
    .stApp div[data-testid="stButton"]
    button[data-testid="stBaseButton-secondary"],
    .stApp div[data-testid="stButton"]
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #17365D !important;
        color: #17365D !important;
    }

    .stApp div[data-testid="stButton"]
    button[data-testid="stBaseButton-secondary"] p,
    .stApp div[data-testid="stButton"]
    button[kind="secondary"] p {
        color: #17365D !important;
    }


/* ---------- PAID / UNPAID STATUS ---------- */

/* Green fee-status button */
.stApp div[data-testid="stButton"]:has(button[kind="primary"]) button[kind="primary"] {
    background-color: #16A34A !important;
    border: 1px solid #16A34A !important;
    color: #FFFFFF !important;
}

.stApp div[data-testid="stButton"]:has(button[kind="primary"]) button[kind="primary"]:hover {
    background-color: #15803D !important;
    border-color: #15803D !important;
}

/* Red fee-status button */
.stApp div[data-testid="stButton"]:has(button[kind="secondary"]) button[kind="secondary"] {
    background-color: #DC2626 !important;
    border: 1px solid #DC2626 !important;
    color: #FFFFFF !important;
}

.stApp div[data-testid="stButton"]:has(button[kind="secondary"]) button[kind="secondary"]:hover {
    background-color: #B91C1C !important;
    border-color: #B91C1C !important;
}

/* Status button text */
.stApp div[data-testid="stButton"] button[kind="primary"] p,
.stApp div[data-testid="stButton"] button[kind="secondary"] p {
    color: #FFFFFF !important;
}


    /* ---------- INPUT FIELDS ---------- */
    .stApp input,
    .stApp textarea {
        border-radius: 8px !important;
    }

    /* ---------- TABLES ---------- */
    .stApp [data-testid="stDataFrame"],
    .stApp [data-testid="stTable"] {
        border: 1px solid #E6D9CA !important;
        border-radius: 10px !important;
        overflow: hidden;
    }

    /* ---------- CHART TEXT ---------- */
    .stApp svg text {
        fill: #17365D !important;
    }

    /* ---------- DIVIDERS ---------- */
    .stApp hr {
        border-color: #E6D9CA !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)



# =========================================================
# DATABASE - SUPABASE
# =========================================================

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


# =========================================================
# MONTHS / YEARS
# =========================================================

months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

current_year = date.today().year

years = list(range(current_year - 2, current_year + 5))


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📚 Student Fee System")

page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Student Profiles",
        "Monthly Report",
        "Add Student",
        "Edit Student",
        "Record Fee",
        "Fee Defaulter Report",
        "Payment Records",
        "Edit/Delete Payment"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("📊 Student Fee Dashboard")

    st.write(
        "Manage monthly student fees using the payment toggle."
    )

    st.divider()

    # -----------------------------------------------------
    # MONTH / YEAR
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        selected_month = st.selectbox(
            "📅 Select Month",
            months,
            index=date.today().month - 1,
            key="dashboard_month"
        )

    with col2:
        selected_year = st.selectbox(
            "📅 Select Year",
            years,
            index=years.index(current_year),
            key="dashboard_year"
        )

    st.divider()

    # -----------------------------------------------------
    # SEARCH STUDENT
    # -----------------------------------------------------

    st.subheader("🔍 Search Student")

    search_name = st.text_input(
        "Enter student name",
        placeholder="Example: Mehak",
        key="dashboard_search"
    )

    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_response = (
        supabase
        .table("students")
        .select("id, name, subject, monthly_fee")
        .order("name")
        .execute()
    )

    students_data = students_response.data or []
    total_students = len(students_data)

    # -----------------------------------------------------
    # GET SELECTED MONTH'S PAYMENTS
    # -----------------------------------------------------

    payments_response = (
        supabase
        .table("payments")
        .select("id, student_id, amount")
        .eq("month", selected_month)
        .eq("year", selected_year)
        .execute()
    )

    payments_data = payments_response.data or []

    payment_lookup = {}

    for payment in payments_data:
        student_id = payment["student_id"]

        payment_lookup[student_id] = {
            "id": payment["id"],
            "amount": float(payment.get("amount") or 0)
        }

    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

    total_expected = 0
    total_received = 0
    paid_students = 0
    unpaid_students = 0

    for student in students_data:
        monthly_fee = float(student.get("monthly_fee") or 0)
        total_expected += monthly_fee

        payment = payment_lookup.get(student["id"])

        if (
            payment
            and monthly_fee > 0
            and payment["amount"] >= monthly_fee
        ):
            total_received += monthly_fee
            paid_students += 1
        else:
            unpaid_students += 1

    # -----------------------------------------------------
    # DASHBOARD CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("👥 Students", total_students)
    col2.metric("💰 Expected", f"Rs. {total_expected:,.0f}")
    col3.metric("💵 Collected", f"Rs. {total_received:,.0f}")
    col4.metric("✅ Paid", paid_students)
    col5.metric("❌ Unpaid", unpaid_students)

    # -----------------------------------------------------
    # PAID STUDENT PROGRESS
    # -----------------------------------------------------

    st.subheader("📈 Monthly Fee Collection Progress")

    if total_students > 0:
        paid_percentage = paid_students / total_students

        st.progress(
            paid_percentage,
            text=(
                f"{paid_students} of {total_students} students paid "
                f"({paid_percentage:.0%}) for "
                f"{selected_month} {selected_year}"
            )
        )
    else:
        st.info("Add students to see fee collection progress.")

    st.divider()

    # -----------------------------------------------------
    # MONTHLY INCOME CHART
    # -----------------------------------------------------

    st.subheader(
        f"💰 Monthly Income Overview — {selected_year}"
    )

    chart_response = (
        supabase
        .table("payments")
        .select("month, amount")
        .eq("year", selected_year)
        .execute()
    )

    chart_payments = chart_response.data or []

    monthly_income = {
        month_name: 0.0 for month_name in months
    }

    for chart_payment in chart_payments:
        month_name = chart_payment.get("month")

        if month_name in monthly_income:
            monthly_income[month_name] += float(
                chart_payment.get("amount") or 0
            )

    income_df = pd.DataFrame({
        "Month": months,
        "Income (Rs.)": [
            monthly_income[month_name]
            for month_name in months
        ]
    })

    st.bar_chart(
        income_df.set_index("Month"),
        y="Income (Rs.)",
        color="#E87524"
    )

    st.caption(
        "Income is calculated from recorded payment amounts "
        "in Supabase. Months without payments show zero."
    )

    st.divider()

    # -----------------------------------------------------
    # SEARCH RESULTS
    # -----------------------------------------------------

    if search_name.strip():
        search_results = [
            student
            for student in students_data
            if search_name.strip().lower()
            in (student.get("name") or "").lower()
        ]

        if not search_results:
            st.warning(
                f"❌ No student found with name "
                f"'{search_name.strip()}'."
            )
        else:
            st.subheader(
                f"🔎 Search Results for '{search_name.strip()}'"
            )

            for student in search_results:
                student_id = student["id"]
                student_name = student.get("name") or ""
                subject = student.get("subject") or "-"
                monthly_fee = float(
                    student.get("monthly_fee") or 0
                )

                payment = payment_lookup.get(student_id)

                is_paid = (
                    payment is not None
                    and monthly_fee > 0
                    and payment["amount"] >= monthly_fee
                )

                st.markdown(f"### 👨‍🎓 {student_name}")

                info_col1, info_col2, info_col3 = st.columns(3)

                info_col1.write(f"🆔 **Student ID:** {student_id}")
                info_col2.write(f"📚 **Subject / Class:** {subject}")
                info_col3.write(
                    f"💰 **Monthly Fee:** Rs. {monthly_fee:,.0f}"
                )

                if is_paid:
                    st.success(
                        f"✅ Fee Paid — Rs. {monthly_fee:,.0f}"
                    )
                else:
                    st.error("❌ Fee Unpaid")

                st.divider()

    
   
    # -----------------------------------------------------
    # FEE STATUS TABLE - CLICKABLE PAID / UNPAID BUTTONS
    # -----------------------------------------------------

    st.subheader(
        f"📋 {selected_month} {selected_year} Fee Status"
    )

    header = st.columns([3, 2, 2, 2])
    header[0].write("**Student**")
    header[1].write("**Class / Subject**")
    header[2].write("**Monthly Fee**")
    header[3].write("**Fee Status**")

    st.divider()

    for student in students_data:
        student_id = student["id"]
        student_name = student.get("name") or ""
        subject = student.get("subject") or "-"
        monthly_fee = float(student.get("monthly_fee") or 0)

        payment = payment_lookup.get(student_id)

        is_paid = (
            payment is not None
            and monthly_fee > 0
            and payment["amount"] >= monthly_fee
        )

        # Apply the existing student search filter
        if (
            search_name.strip()
            and search_name.strip().lower() not in student_name.lower()
        ):
            continue

        row = st.columns([3, 2, 2, 2])

        row[0].write(student_name)
        row[1].write(subject)
        row[2].write(f"Rs. {monthly_fee:,.0f}")

        # Green button means paid; red button means unpaid
        with row[3]:
            if is_paid:
                clicked = st.button(
                    "✓ Fee Paid",
                    key=(
                        f"paid_button_{student_id}_"
                        f"{selected_month}_{selected_year}"
                    ),
                    type="primary",
                    use_container_width=True
                )
            else:
                clicked = st.button(
                    "✕ Unpaid",
                    key=(
                        f"unpaid_button_{student_id}_"
                        f"{selected_month}_{selected_year}"
                    ),
                    type="secondary",
                    use_container_width=True
                )

        if clicked:

            if is_paid:
                # PAID -> UNPAID: delete this month's payment
                if payment:
                    try:
                        (
                            supabase
                            .table("payments")
                            .delete()
                            .eq("id", payment["id"])
                            .eq("student_id", student_id)
                            .eq("month", selected_month)
                            .eq("year", selected_year)
                            .execute()
                        )

                        st.success(
                            f"Fee marked unpaid for {student_name}."
                        )
                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"Could not remove payment: {e}"
                        )

            else:
                # UNPAID -> PAID: record the full monthly fee
                if monthly_fee <= 0:
                    st.error(
                        "Set a monthly fee greater than zero first."
                    )
                else:
                    try:
                        # Recheck Supabase before inserting to avoid
                        # creating a duplicate payment.
                        existing_response = (
                            supabase
                            .table("payments")
                            .select("id, amount")
                            .eq("student_id", student_id)
                            .eq("month", selected_month)
                            .eq("year", selected_year)
                            .limit(1)
                            .execute()
                        )

                        existing_data = existing_response.data or []

                        if existing_data:
                            existing_payment = existing_data[0]
                            existing_amount = float(
                                existing_payment.get("amount") or 0
                            )

                            if existing_amount >= monthly_fee:
                                st.info(
                                    "A full payment already exists "
                                    "for this month."
                                )
                            else:
                                # Update an existing incomplete payment
                                (
                                    supabase
                                    .table("payments")
                                    .update({
                                        "amount": monthly_fee,
                                        "status": "Paid",
                                        "payment_date": (
                                            date.today().isoformat()
                                        )
                                    })
                                    .eq("id", existing_payment["id"])
                                    .execute()
                                )

                                st.success(
                                    f"Full fee recorded for {student_name}."
                                )

                        else:
                            # Insert a new full payment
                            (
                                supabase
                                .table("payments")
                                .insert({
                                    "student_id": student_id,
                                    "month": selected_month,
                                    "year": selected_year,
                                    "amount": monthly_fee,
                                    "status": "Paid",
                                    "payment_date": (
                                        date.today().isoformat()
                                    )
                                })
                                .execute()
                            )

                            st.success(
                                f"Full fee recorded for {student_name}."
                            )

                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"Could not record payment: {e}"
                        )

    st.divider()


# =========================================================
# STUDENT PROFILES
# =========================================================

elif page == "Student Profiles":

    st.title("👤 Student Profiles")
    st.write(
        "View student details, fee balances, and complete payment history."
    )

    st.divider()

    # -----------------------------------------------------
    # LOAD STUDENTS
    # -----------------------------------------------------

    profile_response = (
        supabase
        .table("students")
        .select(
            "id, name, subject, monthly_fee, "
            "admission_date, guardian_name, guardian_contact"
        )
        .order("name")
        .execute()
    )

    profile_students = profile_response.data or []

    if not profile_students:
        st.info("No students found. Add a student first.")

    else:
        selected_student = st.selectbox(
            "🔍 Select a student",
            profile_students,
            format_func=lambda s: (
                f"{s['name']} (ID: {s['id']})"
            ),
            key="profile_student_select"
        )

        student_id = selected_student["id"]
        monthly_fee = float(
            selected_student.get("monthly_fee") or 0
        )

        st.divider()

        # -------------------------------------------------
        # STUDENT DETAILS
        # -------------------------------------------------

        st.subheader("📋 Student Information")

        col1, col2 = st.columns(2)

        col1.metric("Student ID", student_id)
        col2.metric("Monthly Fee", f"Rs. {monthly_fee:,.0f}")

        st.write(
            f"**Student Name:** {selected_student.get('name') or '-'}"
        )
        st.write(
            f"**Class / Course:** {selected_student.get('subject') or '-'}"
        )

        # -------------------------------------------------
        # EDIT PROFILE DETAILS
        # -------------------------------------------------

        st.subheader("✏️ Edit Profile Details")

        existing_admission = selected_student.get(
            "admission_date"
        )

        admission_value = None

        if existing_admission:
            try:
                admission_value = date.fromisoformat(
                    str(existing_admission)[:10]
                )
            except (ValueError, TypeError):
                admission_value = None

        with st.form(
            key=f"profile_form_{student_id}"
        ):
            admission_date = st.date_input(
                "Admission Date",
                value=admission_value,
            )

            guardian_name = st.text_input(
                "Guardian Name",
                value=selected_student.get("guardian_name") or "",
            )

            guardian_contact = st.text_input(
                "Guardian Contact",
                value=selected_student.get("guardian_contact") or "",
                placeholder="Phone number"
            )

            save_profile = st.form_submit_button(
                "💾 Save Profile",
                type="primary",
                use_container_width=True
            )

            if save_profile:
                supabase.table("students").update({
                    "admission_date": (
                        admission_date.isoformat()
                        if admission_date else None
                    ),
                    "guardian_name": guardian_name.strip() or None,
                    "guardian_contact": guardian_contact.strip() or None,
                }).eq("id", student_id).execute()

                st.success("Student profile updated successfully!")
                st.rerun()

        st.divider()

        # -------------------------------------------------
        # LOAD ALL PAYMENTS FOR THIS STUDENT
        # -------------------------------------------------

        history_response = (
            supabase
            .table("payments")
            .select(
                "id, amount, month, year, payment_date"
            )
            .eq("student_id", student_id)
            .execute()
        )

        payment_history = history_response.data or []

        total_received = sum(
            float(payment.get("amount") or 0)
            for payment in payment_history
        )

        st.subheader("💰 Fee Summary")

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Fees Received",
            f"Rs. {total_received:,.0f}"
        )

        # -------------------------------------------------
        # CALCULATE DUE FEES FROM ADMISSION DATE
        # -------------------------------------------------

        if admission_date:
            today = date.today()

            start_index = (
                admission_date.year * 12
                + admission_date.month - 1
            )

            end_index = today.year * 12 + today.month - 1

            due_periods = []

            if start_index <= end_index:
                for period_index in range(
                    start_index, end_index + 1
                ):
                    year_value = period_index // 12
                    month_number = period_index % 12 + 1

                    due_periods.append((
                        months[month_number - 1],
                        year_value
                    ))

            payment_lookup = {}

            for payment in payment_history:
                key = (
                    payment.get("month"),
                    int(payment.get("year") or 0)
                )

                payment_lookup[key] = (
                    payment_lookup.get(key, 0)
                    + float(payment.get("amount") or 0)
                )

            expected_fees = monthly_fee * len(due_periods)

            received_for_due_periods = sum(
                payment_lookup.get(period, 0)
                for period in due_periods
            )

            outstanding_balance = max(
                expected_fees - received_for_due_periods,
                0
            )

            col2.metric(
                "Outstanding Balance",
                f"Rs. {outstanding_balance:,.0f}"
            )

            # ---------------------------------------------
            # PAID / UNPAID MONTHS
            # ---------------------------------------------

            st.divider()
            st.subheader("📅 Monthly Fee Status")

            paid_periods = []
            unpaid_periods = []

            for period in due_periods:
                paid_amount = payment_lookup.get(period, 0)

                if (
                    monthly_fee > 0
                    and paid_amount >= monthly_fee
                ):
                    paid_periods.append(period)
                else:
                    unpaid_periods.append(period)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### ✅ Paid Months")

                if paid_periods:
                    for month_name, year_value in reversed(
                        paid_periods
                    ):
                        st.write(f"🟢 {month_name} {year_value}")
                else:
                    st.info("No fully paid months found.")

            with col2:
                st.markdown("#### ❌ Unpaid Months")

                if unpaid_periods:
                    for month_name, year_value in reversed(
                        unpaid_periods
                    ):
                        st.write(f"🔴 {month_name} {year_value}")
                else:
                    st.success("All months are paid.")

        else:
            col2.metric(
                "Outstanding Balance",
                "Not calculated"
            )

            st.info(
                "Enter and save the admission date above to "
                "calculate the expected fees, outstanding balance, "
                "and paid/unpaid months."
            )

        # -------------------------------------------------
        # COMPLETE PAYMENT HISTORY
        # -------------------------------------------------

        st.divider()
        st.subheader("🧾 Complete Payment History")

        if payment_history:
            history_rows = []

            for payment in payment_history:
                amount = float(payment.get("amount") or 0)

                if monthly_fee > 0 and amount >= monthly_fee:
                    status = "Paid"
                elif amount > 0:
                    status = "Partial"
                else:
                    status = "Recorded"

                history_rows.append({
                    "Month": payment.get("month") or "-",
                    "Year": payment.get("year") or "-",
                    "Payment Date": (
                        payment.get("payment_date") or "-"
                    ),
                    "Amount (Rs.)": amount,
                    "Status": status,
                })

            history_df = pd.DataFrame(history_rows)

            history_df["_sort_year"] = pd.to_numeric(
                history_df["Year"], errors="coerce"
            )

            history_df["_sort_month"] = (
                history_df["Month"]
                .map({
                    month_name: index
                    for index, month_name in enumerate(
                        months, start=1
                    )
                })
                .fillna(0)
            )

            history_df = history_df.sort_values(
                ["_sort_year", "_sort_month"],
                ascending=False
            )

            history_df = history_df.drop(
                columns=["_sort_year", "_sort_month"]
            )

            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "No payment records are available for this student yet."
            )

        # -----------------------------------------------------
        # DOWNLOAD STUDENT FEE STATEMENT
        # -----------------------------------------------------

        st.divider()
        st.subheader("📄 Download Student Fee Statement")

        if admission_date:
            statement_pdf = generate_student_statement(
                institute_name="Skillciety",
                student=selected_student,
                payment_history=payment_history,
                expected_fees=expected_fees,
                total_received=total_received,
                outstanding_balance=outstanding_balance,
            )

            st.download_button(
                label="⬇️ Download Fee Statement (PDF)",
                data=statement_pdf,
                file_name=f"Student_Fee_Statement_{student_id}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"download_statement_{student_id}",
            )
        else:
            st.info(
                "Save the student's admission date before downloading "
                "the fee statement."
            )


# =========================================================
# MONTHLY REPORT
# =========================================================

elif page == "Monthly Report":

    st.title("📊 Monthly Fee Report")

    st.write(
        "View complete fee collection details "
        "for a selected month."
    )

    st.divider()

    # -----------------------------------------------------
    # MONTH / YEAR
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        report_month = st.selectbox(
            "📅 Select Month",
            months,
            index=date.today().month - 1,
            key="report_month"
        )

    with col2:
        report_year = st.selectbox(
            "📅 Select Year",
            years,
            index=years.index(current_year),
            key="report_year"
        )

    st.divider()

    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_response = (
        supabase
        .table("students")
        .select("id, name, subject, monthly_fee")
        .order("name")
        .execute()
    )

    students_data = students_response.data or []

    # -----------------------------------------------------
    # GET PAYMENTS
    # -----------------------------------------------------

    payments_response = (
        supabase
        .table("payments")
        .select("student_id, amount, payment_date")
        .eq("month", report_month)
        .eq("year", report_year)
        .execute()
    )

    payments_data = payments_response.data or []

    # -----------------------------------------------------
    # PAYMENT LOOKUP
    # -----------------------------------------------------

    payment_lookup = {}

    for payment in payments_data:
        student_id = payment["student_id"]

        payment_lookup[student_id] = {
            "amount": float(payment.get("amount") or 0),
            "payment_date": payment.get("payment_date") or "-"
        }

    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

    total_expected = 0
    total_received = 0
    total_pending = 0
    paid_count = 0
    unpaid_count = 0
    report_data = []

    for student in students_data:
        student_id = student["id"]
        student_name = student.get("name") or ""
        subject = student.get("subject") or "-"
        monthly_fee = float(student.get("monthly_fee") or 0)

        payment = payment_lookup.get(student_id)

        if payment:
            amount_received = payment["amount"]
            payment_date = payment["payment_date"]
        else:
            amount_received = 0
            payment_date = "-"

        # Full-payment system
        if monthly_fee > 0 and amount_received >= monthly_fee:
            status = "Paid"
            received_for_student = monthly_fee
            pending = 0
            paid_count += 1
        else:
            status = "Unpaid"
            received_for_student = 0
            pending = monthly_fee
            unpaid_count += 1

        total_expected += monthly_fee
        total_received += received_for_student
        total_pending += pending

        report_data.append([
            student_name,
            subject,
            monthly_fee,
            received_for_student,
            pending,
            status,
            payment_date
        ])

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    st.subheader(f"📌 {report_month} {report_year} Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Total Expected", f"Rs. {total_expected:,.0f}")
    col2.metric("💵 Total Received", f"Rs. {total_received:,.0f}")
    col3.metric("⏳ Total Pending", f"Rs. {total_pending:,.0f}")

    st.divider()

    col1, col2 = st.columns(2)

    col1.metric("✅ Paid Students", paid_count)
    col2.metric("❌ Unpaid Students", unpaid_count)

    st.divider()

    # -----------------------------------------------------
    # STUDENT FEE DETAILS
    # -----------------------------------------------------

    st.subheader("📋 Student Fee Details")

    report_df = pd.DataFrame(
        report_data,
        columns=[
            "Student Name",
            "Subject / Class",
            "Monthly Fee",
            "Amount Received",
            "Pending",
            "Status",
            "Payment Date"
        ]
    )

    if report_df.empty:
        st.info(
            f"No students found for {report_month} {report_year}."
        )
    else:
        display_report = report_df.copy()

        for column in ["Monthly Fee", "Amount Received", "Pending"]:
            display_report[column] = display_report[column].apply(
                lambda value: f"Rs. {value:,.0f}"
            )

        st.dataframe(
            display_report,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # -----------------------------------------------------
    # UNPAID STUDENTS
    # -----------------------------------------------------

    st.subheader("⏳ Unpaid Students")

    pending_data = [
        row for row in report_data if row[4] > 0
    ]

    if pending_data:
        pending_df = pd.DataFrame(
            pending_data,
            columns=[
                "Student Name",
                "Subject / Class",
                "Monthly Fee",
                "Amount Received",
                "Pending",
                "Status",
                "Payment Date"
            ]
        )

        display_pending = pending_df.copy()

        for column in ["Monthly Fee", "Amount Received", "Pending"]:
            display_pending[column] = display_pending[column].apply(
                lambda value: f"Rs. {value:,.0f}"
            )

        st.dataframe(
            display_pending,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("🎉 No pending fees for this month!")

    st.divider()

    # -----------------------------------------------------
    # DOWNLOAD REPORT
    # -----------------------------------------------------

    csv_report = report_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Monthly Report",
        data=csv_report,
        file_name=f"{report_month}_{report_year}_fee_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# ADD STUDENT
# =========================================================

elif page == "Add Student":

    st.title("👨‍🎓 Add New Student")

    name = st.text_input("Student Name")
    subject = st.text_input("Subject / Class")

    monthly_fee = st.number_input(
        "Monthly Fee",
        min_value=0.0,
        step=500.0
    )

    if st.button("➕ Add Student", use_container_width=True):

        if not name.strip():
            st.error("Please enter the student's name.")
        else:
            students_response = (
                supabase
                .table("students")
                .select("id, name, subject")
                .execute()
            )

            students_data = students_response.data or []
            duplicate_student = None

            for student in students_data:
                existing_name = (
                    student.get("name") or ""
                ).strip().lower()

                existing_subject = (
                    student.get("subject") or ""
                ).strip().lower()

                if (
                    existing_name == name.strip().lower()
                    and existing_subject == subject.strip().lower()
                ):
                    duplicate_student = student
                    break

            if duplicate_student:
                st.error(
                    f"❌ Student already exists with ID "
                    f"{duplicate_student['id']}."
                )
            else:
                (
                    supabase
                    .table("students")
                    .insert({
                        "name": name.strip(),
                        "subject": subject.strip(),
                        "monthly_fee": monthly_fee
                    })
                    .execute()
                )

                st.success(f"✅ {name} added successfully!")
                st.rerun()


# =========================================================
# EDIT STUDENT
# =========================================================

elif page == "Edit Student":

    st.title("✏️ Edit Student")

    students_response = (
        supabase
        .table("students")
        .select("id, name, subject, monthly_fee")
        .order("name")
        .execute()
    )

    students = students_response.data or []

    if not students:
        st.warning("No students found.")
    else:
        student_options = {
            (
                f"{student['name']} | "
                f"{student.get('subject') or '-'} | "
                f"ID {student['id']}"
            ): student["id"]
            for student in students
        }

        selected_label = st.selectbox(
            "Select Student",
            list(student_options.keys()),
            key="edit_student_select"
        )

        student_id = student_options[selected_label]

        selected_student = next(
            (
                student for student in students
                if student["id"] == student_id
            ),
            None
        )

        if selected_student:
            st.subheader("Edit Student Information")

            new_name = st.text_input(
                "Student Name",
                value=selected_student.get("name") or "",
                key="edit_name"
            )

            new_subject = st.text_input(
                "Subject / Class",
                value=selected_student.get("subject") or "",
                key="edit_subject"
            )

            new_monthly_fee = st.number_input(
                "Monthly Fee",
                min_value=0.0,
                value=float(selected_student.get("monthly_fee") or 0),
                step=500.0,
                key="edit_fee"
            )

            st.info(
                "Changing the fee updates the student's "
                "current monthly fee."
            )

            if st.button(
                "💾 Update Student",
                use_container_width=True,
                key="update_student_button"
            ):
                if not new_name.strip():
                    st.error("Student name cannot be empty.")
                else:
                    (
                        supabase
                        .table("students")
                        .update({
                            "name": new_name.strip(),
                            "subject": new_subject.strip(),
                            "monthly_fee": new_monthly_fee
                        })
                        .eq("id", student_id)
                        .execute()
                    )

                    st.success("Student updated successfully! ✅")
                    st.rerun()

            st.divider()
            st.subheader("🗑️ Delete Student")

            st.warning(
                "Deleting a student will also delete all "
                "payment records associated with this student."
            )

            confirm_delete = st.checkbox(
                "I understand that this action cannot be undone.",
                key="confirm_delete_student"
            )

            if st.button(
                "🗑️ Delete Student",
                use_container_width=True,
                key="delete_student_button"
            ):
                if not confirm_delete:
                    st.error("Please confirm the deletion first.")
                else:
                    (
                        supabase
                        .table("payments")
                        .delete()
                        .eq("student_id", student_id)
                        .execute()
                    )

                    (
                        supabase
                        .table("students")
                        .delete()
                        .eq("id", student_id)
                        .execute()
                    )

                    st.success(
                        "Student and associated payment records "
                        "deleted successfully! ✅"
                    )
                    st.rerun()


# =========================================================
# FEE DEFAULTER REPORT
# =========================================================

elif page == "Fee Defaulter Report":

    st.title("📋 Fee Defaulter Report")
    st.write("Find students with unpaid monthly fees.")
    st.divider()

    from datetime import date
    import pandas as pd

    month_names = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    today = date.today()

    col1, col2 = st.columns(2)

    with col1:
        selected_month = st.selectbox(
            "Select Month",
            month_names,
            index=today.month - 1,
            key="defaulter_report_month"
        )

    with col2:
        selected_year = st.selectbox(
            "Select Year",
            list(range(2024, today.year + 2)),
            index=list(range(2024, today.year + 2)).index(today.year),
            key="defaulter_report_year"
        )

    selected_month_number = month_names.index(selected_month) + 1

    students_response = (
        supabase.table("students")
        .select("id, name, subject, monthly_fee, admission_date")
        .order("name")
        .execute()
    )

    payments_response = (
        supabase.table("payments")
        .select("student_id, month, year, amount")
        .execute()
    )

    students_data = students_response.data or []
    payments_data = payments_response.data or []

    defaulter_rows = []

    for student in students_data:

        admission_date = student.get("admission_date")

        if not admission_date:
            continue

        try:
            admission_date = pd.to_datetime(admission_date).date()
        except (ValueError, TypeError):
            continue

        admission_period = (
            admission_date.year * 12 + admission_date.month
        )

        report_period = selected_year * 12 + selected_month_number

        if admission_period > report_period:
            continue

        monthly_fee = float(student.get("monthly_fee") or 0)

        if monthly_fee <= 0:
            continue

        expected_fees = 0.0
        received_amount = 0.0
        unpaid_months = []

        for year in range(admission_date.year, selected_year + 1):

            first_month = (
                admission_date.month
                if year == admission_date.year else 1
            )

            last_month = (
                selected_month_number if year == selected_year else 12
            )

            for month_number in range(first_month, last_month + 1):

                expected_fees += monthly_fee
                month_received = 0.0

                for payment in payments_data:

                    if str(payment.get("student_id")) != str(student.get("id")):
                        continue

                    try:
                        payment_year = int(payment.get("year"))
                    except (ValueError, TypeError):
                        continue

                    payment_month = str(payment.get("month") or "").strip()

                    if payment_month.isdigit():
                        payment_month_number = int(payment_month)
                    else:
                        try:
                            payment_month_number = (
                                month_names.index(payment_month.title()) + 1
                            )
                        except ValueError:
                            continue

                    if (
                        payment_year == year
                        and payment_month_number == month_number
                    ):
                        month_received += float(payment.get("amount") or 0)

                received_amount += month_received

                if month_received < monthly_fee:
                    unpaid_months.append(
                        f"{month_names[month_number - 1]} {year}"
                    )

        outstanding = max(0.0, expected_fees - received_amount)

        if outstanding > 0:
            defaulter_rows.append({
                "Student Name": student.get("name") or "",
                "Class / Subject": student.get("subject") or "-",
                "Monthly Fee (Rs.)": monthly_fee,
                "Expected Fees (Rs.)": expected_fees,
                "Received (Rs.)": received_amount,
                "Outstanding (Rs.)": outstanding,
                "Unpaid Months": ", ".join(unpaid_months)
            })

    total_outstanding = sum(
        row["Outstanding (Rs.)"] for row in defaulter_rows
    )

    col1, col2 = st.columns(2)

    col1.metric("Students with Dues", len(defaulter_rows))
    col2.metric("Total Outstanding", f"Rs. {total_outstanding:,.0f}")

    st.divider()

    if defaulter_rows:

        report_df = pd.DataFrame(defaulter_rows)

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Defaulter Report (CSV)",
            data=report_df.to_csv(index=False).encode("utf-8"),
            file_name=f"Fee_Defaulters_{selected_month}_{selected_year}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_fee_defaulters"
        )

    else:
        st.success(
            "No outstanding fees found for this reporting period."
        )


# =========================================================
# RECORD FEE
# =========================================================

elif page == "Record Fee":

    st.title("💰 Record Fee Payment")

    st.write("Record the complete monthly fee for a student.")
    st.divider()

    students_response = (
        supabase
        .table("students")
        .select("id, name, subject, monthly_fee")
        .order("name")
        .execute()
    )

    students = students_response.data or []

    if not students:
        st.warning("No students found. Please add students first.")
    else:
        student_options = {
            (
                f"{student['name']} | "
                f"{student.get('subject') or '-'} | "
                f"ID {student['id']}"
            ): student["id"]
            for student in students
        }

        selected_label = st.selectbox(
            "👨‍🎓 Select Student",
            list(student_options.keys()),
            key="record_student"
        )

        student_id = student_options[selected_label]

        selected_student = next(
            (
                student for student in students
                if student["id"] == student_id
            ),
            None
        )

        if selected_student:
            student_name = selected_student.get("name") or ""
            monthly_fee = float(
                selected_student.get("monthly_fee") or 0
            )

            st.info(f"💵 Monthly Fee: **Rs. {monthly_fee:,.0f}**")

            col1, col2 = st.columns(2)

            with col1:
                month = st.selectbox(
                    "📅 Select Month",
                    months,
                    index=date.today().month - 1,
                    key="record_month"
                )

            with col2:
                year = st.selectbox(
                    "📅 Select Year",
                    years,
                    index=years.index(current_year),
                    key="record_year"
                )

            payment_date = st.date_input(
                "📅 Payment Date",
                value=date.today(),
                key="record_payment_date"
            )

            existing_payment_response = (
                supabase
                .table("payments")
                .select("id, amount, status, payment_date")
                .eq("student_id", student_id)
                .eq("month", month)
                .eq("year", year)
                .limit(1)
                .execute()
            )

            existing_payment_data = (
                existing_payment_response.data or []
            )

            existing_payment = (
                existing_payment_data[0]
                if existing_payment_data
                else None
            )

            payment_exists = existing_payment is not None

            if payment_exists:
                existing_amount = float(
                    existing_payment.get("amount") or 0
                )

                st.warning(
                    f"⚠️ Payment already exists for **{student_name}** "
                    f"in **{month} {year}**.\n\n"
                    f"Existing payment: **Rs. {existing_amount:,.0f}**"
                )

            if st.button(
                "💾 Record Full Payment",
                use_container_width=True,
                key="record_payment_button"
            ):
                if payment_exists:
                    st.error("❌ Payment already exists.")
                elif monthly_fee <= 0:
                    st.error(
                        "Student monthly fee must be greater than 0."
                    )
                else:
                    (
                        supabase
                        .table("payments")
                        .insert({
                            "student_id": student_id,
                            "month": month,
                            "year": year,
                            "amount": monthly_fee,
                            "status": "Paid",
                            "payment_date": payment_date.isoformat()
                        })
                        .execute()
                    )

                    st.success(
                        f"✅ Full payment of Rs. {monthly_fee:,.0f} "
                        f"recorded for {student_name}."
                    )
                    st.rerun()


# =========================================================
# PAYMENT RECORDS
# =========================================================

elif page == "Payment Records":

    st.title("💳 Payment Records")

    st.write("View all recorded student fee payments.")
    st.divider()

    payments_response = (
        supabase
        .table("payments")
        .select(
            "id, student_id, month, year, amount, status, payment_date"
        )
        .order("id", desc=True)
        .execute()
    )

    payments_data = payments_response.data or []

    students_response = (
        supabase
        .table("students")
        .select("id, name, subject")
        .execute()
    )

    students_data = students_response.data or []

    student_lookup = {
        student["id"]: student
        for student in students_data
    }

    payments = []

    for payment in payments_data:
        student = student_lookup.get(payment["student_id"], {})

        payments.append([
            payment["id"],
            student.get("name"),
            student.get("subject"),
            payment["month"],
            payment["year"],
            payment["amount"],
            payment["status"],
            payment["payment_date"]
        ])

    if not payments:
        st.info("No payment records found.")
    else:
        payment_df = pd.DataFrame(
            payments,
            columns=[
                "Payment ID",
                "Student Name",
                "Subject / Class",
                "Month",
                "Year",
                "Amount",
                "Status",
                "Payment Date"
            ]
        )

        display_payment = payment_df.copy()

        display_payment["Student Name"] = (
            display_payment["Student Name"].fillna("Deleted Student")
        )
        display_payment["Subject / Class"] = (
            display_payment["Subject / Class"].fillna("-")
        )
        display_payment["Status"] = (
            display_payment["Status"].fillna("Paid")
        )
        display_payment["Amount"] = (
            display_payment["Amount"]
            .fillna(0)
            .apply(lambda value: f"Rs. {value:,.0f}")
        )
        display_payment["Payment Date"] = (
            display_payment["Payment Date"].fillna("-")
        )

        st.dataframe(
            display_payment,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        total_payment_amount = (
            payment_df["Amount"].fillna(0).sum()
        )

        st.metric(
            "💵 Total Payments",
            f"Rs. {total_payment_amount:,.0f}"
        )

        st.divider()
        st.subheader("🧾 Generate Fee Receipt")

        st.write(
            "Select a payment record to generate its PDF receipt."
        )

        receipt_options = {}

        for payment in payments_data:
            student = student_lookup.get(payment["student_id"], {})
            student_name = student.get("name") or "Deleted Student"

            receipt_label = (
                f"Payment #{payment['id']} | "
                f"{student_name} | "
                f"{payment['month']} {payment['year']}"
            )

            receipt_options[receipt_label] = payment

        selected_receipt_label = st.selectbox(
            "Select payment",
            list(receipt_options.keys()),
            key="receipt_payment_select"
        )

        selected_receipt = receipt_options[selected_receipt_label]

        receipt_student = student_lookup.get(
            selected_receipt["student_id"],
            {}
        )

        if st.button(
            "🧾 Generate PDF Receipt",
            use_container_width=True,
            key="generate_fee_receipt_button"
        ):
            try:
                receipt_pdf = generate_fee_receipt(
                    institute_name="Skillciety",
                    student_name=(
                        receipt_student.get("name") or "Deleted Student"
                    ),
                    student_id=str(selected_receipt["student_id"]),
                    receipt_number=f"FEE-{selected_receipt['id']}",
                    fee_month=(
                        f"{selected_receipt['month']} "
                        f"{selected_receipt['year']}"
                    ),
                    payment_date=(
                        selected_receipt.get("payment_date") or "-"
                    ),
                    amount_paid=float(
                        selected_receipt.get("amount") or 0
                    )
                )

                st.download_button(
                    label="📥 Download PDF Receipt",
                    data=receipt_pdf,
                    file_name=(
                        f"Fee_Receipt_{selected_receipt['id']}.pdf"
                    ),
                    mime="application/pdf",
                    key=f"download_receipt_{selected_receipt['id']}",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Could not generate receipt: {e}")


# =========================================================
# EDIT / DELETE PAYMENT
# =========================================================

elif page == "Edit/Delete Payment":

    st.title("✏️ Edit / Delete Payment")

    st.write("Select an existing payment to edit or delete it.")
    st.divider()

    payments_response = (
        supabase
        .table("payments")
        .select(
            "id, student_id, month, year, amount, status, payment_date"
        )
        .order("id", desc=True)
        .execute()
    )

    payments_data = payments_response.data or []

    students_response = (
        supabase
        .table("students")
        .select("id, name, subject, monthly_fee")
        .execute()
    )

    students_data = students_response.data or []

    student_lookup = {
        student["id"]: student
        for student in students_data
    }

    if not payments_data:
        st.info("No payment records available to edit or delete.")
    else:
        payment_options = {}

        for payment in payments_data:
            payment_id = payment["id"]
            student = student_lookup.get(payment["student_id"], {})

            student_name = student.get("name") or "Deleted Student"
            subject = student.get("subject") or "-"
            month = payment.get("month") or "-"
            year = payment.get("year") or "-"
            amount = float(payment.get("amount") or 0)

            label = (
                f"Payment ID {payment_id} | {student_name} | "
                f"{subject} | {month} {year} | Rs. {amount:,.0f}"
            )

            payment_options[label] = payment_id

        selected_payment_label = st.selectbox(
            "💳 Select Payment",
            list(payment_options.keys()),
            key="edit_payment_select"
        )

        selected_payment_id = payment_options[selected_payment_label]

        selected_payment_response = (
            supabase
            .table("payments")
            .select(
                "id, student_id, month, year, amount, status, payment_date"
            )
            .eq("id", selected_payment_id)
            .limit(1)
            .execute()
        )

        selected_payment_data = (
            selected_payment_response.data or []
        )

        if not selected_payment_data:
            st.error("Payment record could not be found.")
        else:
            payment = selected_payment_data[0]
            payment_id = payment["id"]
            student_id = payment["student_id"]

            old_month = payment.get("month") or "January"
            old_year = payment.get("year") or current_year

            student = student_lookup.get(student_id, {})
            student_name = student.get("name") or "Deleted Student"
            subject = student.get("subject") or "-"
            student_fee = float(student.get("monthly_fee") or 0)

            old_payment_date = payment.get("payment_date")

            st.info(
                f"👨‍🎓 Student: **{student_name}**  \n"
                f"📚 Subject: **{subject}**  \n"
                f"🆔 Payment ID: **{payment_id}**  \n"
                f"💰 Monthly Fee: **Rs. {student_fee:,.0f}**"
            )

            st.divider()

            old_month_index = (
                months.index(old_month) if old_month in months else 0
            )

            edit_month = st.selectbox(
                "📅 Month",
                months,
                index=old_month_index,
                key=f"edit_month_{payment_id}"
            )

            edit_year_options = years.copy()

            if old_year not in edit_year_options:
                edit_year_options.append(old_year)
                edit_year_options.sort()

            edit_year = st.selectbox(
                "📅 Year",
                edit_year_options,
                index=edit_year_options.index(old_year),
                key=f"edit_year_{payment_id}"
            )

            st.info(
                f"The student's required full payment is "
                f"**Rs. {student_fee:,.0f}**."
            )

            edit_amount = st.number_input(
                "💵 Payment Amount",
                min_value=0.0,
                value=float(payment.get("amount") or student_fee),
                step=500.0,
                key=f"edit_amount_{payment_id}"
            )

            if student_fee > 0 and edit_amount >= student_fee:
                st.success("✅ Payment Status: Paid")
            else:
                st.warning(
                    "⚠️ Payment must equal the full monthly fee."
                )

            try:
                payment_date_value = (
                    date.fromisoformat(old_payment_date)
                    if old_payment_date
                    else date.today()
                )
            except (ValueError, TypeError):
                payment_date_value = date.today()

            edit_payment_date = st.date_input(
                "📅 Payment Date",
                value=payment_date_value,
                key=f"edit_date_{payment_id}"
            )

            st.divider()

            col1, col2 = st.columns(2)

            # -------------------------------------------------
            # UPDATE PAYMENT
            # -------------------------------------------------

            with col1:
                if st.button(
                    "💾 Update Payment",
                    use_container_width=True,
                    key=f"update_payment_{payment_id}"
                ):
                    if student_fee <= 0:
                        st.error(
                            "Student monthly fee must be greater than 0."
                        )
                    elif edit_amount != student_fee:
                        st.error(
                            f"Please enter the complete monthly fee: "
                            f"Rs. {student_fee:,.0f}"
                        )
                    else:
                        duplicate_response = (
                            supabase
                            .table("payments")
                            .select("id")
                            .eq("student_id", student_id)
                            .eq("month", edit_month)
                            .eq("year", edit_year)
                            .neq("id", payment_id)
                            .limit(1)
                            .execute()
                        )

                        duplicate_data = duplicate_response.data or []

                        if duplicate_data:
                            st.error(
                                "❌ Another payment already exists for "
                                "this student, month and year."
                            )
                        else:
                            (
                                supabase
                                .table("payments")
                                .update({
                                    "month": edit_month,
                                    "year": edit_year,
                                    "amount": student_fee,
                                    "status": "Paid",
                                    "payment_date": (
                                        edit_payment_date.isoformat()
                                    )
                                })
                                .eq("id", payment_id)
                                .execute()
                            )

                            st.success("✅ Payment updated successfully!")
                            st.rerun()

            # -------------------------------------------------
            # DELETE PAYMENT
            # -------------------------------------------------

            with col2:
                if st.button(
                    "🗑️ Delete Payment",
                    use_container_width=True,
                    key=f"delete_payment_{payment_id}"
                ):
                    try:
                        (
                            supabase
                            .table("payments")
                            .delete()
                            .eq("id", payment_id)
                            .execute()
                        )

                        st.success("🗑️ Payment deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(
                            f"❌ Payment could not be deleted: {e}"
                        )
