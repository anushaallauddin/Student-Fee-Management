import streamlit as st
import sqlite3
from datetime import date
import pandas as pd


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Student Fee Management",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("fees.db")
cursor = conn.cursor()


# =========================================================
# CREATE STUDENTS TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT,
    monthly_fee REAL
)
""")


# =========================================================
# CREATE PAYMENTS TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    month TEXT,
    year INTEGER,
    amount REAL,
    status TEXT,
    payment_date TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
)
""")

conn.commit()


# =========================================================
# DATABASE MIGRATION
# =========================================================

cursor.execute("PRAGMA table_info(payments)")

payment_columns = [
    column[1]
    for column in cursor.fetchall()
]

if "year" not in payment_columns:

    cursor.execute("""
    ALTER TABLE payments
    ADD COLUMN year INTEGER
    """)

    conn.commit()


# =========================================================
# FIX OLD PAYMENTS WITH MISSING YEAR
# =========================================================

cursor.execute("""
UPDATE payments
SET year = CAST(substr(payment_date, 1, 4) AS INTEGER)
WHERE year IS NULL
AND payment_date IS NOT NULL
AND payment_date != ''
""")

conn.commit()


# =========================================================
# MONTHS / YEARS
# =========================================================

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

current_year = date.today().year

years = list(
    range(
        current_year - 2,
        current_year + 5
    )
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📚 Student Fee System")

page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Monthly Report",
        "Add Student",
        "Edit Student",
        "Record Fee",
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
        "Manage students, monthly fees and payment records."
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
    # TOTAL STUDENTS
    # -----------------------------------------------------

    cursor.execute("""
    SELECT COUNT(*)
    FROM students
    """)

    total_students = cursor.fetchone()[0]


    # -----------------------------------------------------
    # STUDENTS + PAYMENTS
    # -----------------------------------------------------

    cursor.execute("""
    SELECT
        students.id,
        students.name,
        students.subject,
        students.monthly_fee,
        COALESCE(SUM(payments.amount), 0)

    FROM students

    LEFT JOIN payments

    ON students.id = payments.student_id

    AND payments.month = ?

    AND payments.year = ?

    GROUP BY
        students.id,
        students.name,
        students.subject,
        students.monthly_fee

    ORDER BY students.name
    """, (
        selected_month,
        selected_year
    ))

    student_records = cursor.fetchall()


    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

    total_expected = 0
    total_received = 0
    total_pending = 0

    paid_students = 0
    partial_students = 0
    unpaid_students = 0


    for record in student_records:

        monthly_fee = record[3] or 0
        amount_received = record[4] or 0

        total_expected += monthly_fee
        total_received += amount_received

        pending = max(
            monthly_fee - amount_received,
            0
        )

        total_pending += pending


        if (
            monthly_fee > 0
            and amount_received >= monthly_fee
        ):

            paid_students += 1

        elif amount_received > 0:

            partial_students += 1

        else:

            unpaid_students += 1


    # -----------------------------------------------------
    # DASHBOARD CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "👥 Students",
        total_students
    )

    col2.metric(
        "💰 Expected",
        f"Rs. {total_expected:,.0f}"
    )

    col3.metric(
        "💵 Received",
        f"Rs. {total_received:,.0f}"
    )

    col4.metric(
        "⏳ Pending",
        f"Rs. {total_pending:,.0f}"
    )

    col5.metric(
        "✅ Paid",
        paid_students
    )

    st.divider()


    # -----------------------------------------------------
    # SEARCH RESULT
    # -----------------------------------------------------

    if search_name.strip():

        search_results = [
            record
            for record in student_records
            if search_name.strip().lower()
            in record[1].lower()
        ]


        if not search_results:

            st.warning(
                f"❌ No student found with name "
                f"'{search_name.strip()}'."
            )

        else:

            st.subheader(
                f"🔎 Search Results for "
                f"'{search_name.strip()}'"
            )

            for record in search_results:

                student_id = record[0]
                student_name = record[1]
                subject = record[2] or "-"
                monthly_fee = record[3] or 0
                amount_received = record[4] or 0

                pending = max(
                    monthly_fee - amount_received,
                    0
                )


                if (
                    monthly_fee > 0
                    and amount_received >= monthly_fee
                ):

                    status = "✅ Paid"

                elif amount_received > 0:

                    status = "🟡 Partial"

                else:

                    status = "❌ Unpaid"


                st.markdown(
                    f"### 👨‍🎓 {student_name}"
                )


                info_col1, info_col2, info_col3 = st.columns(3)


                info_col1.write(
                    f"🆔 **Student ID:** {student_id}"
                )

                info_col2.write(
                    f"📚 **Subject / Class:** {subject}"
                )

                info_col3.write(
                    f"💰 **Monthly Fee:** Rs. {monthly_fee:,.0f}"
                )


                info_col1, info_col2, info_col3 = st.columns(3)


                info_col1.write(
                    f"💵 **Received:** Rs. {amount_received:,.0f}"
                )

                info_col2.write(
                    f"⏳ **Pending:** Rs. {pending:,.0f}"
                )

                info_col3.write(
                    f"📌 **Status:** {status}"
                )


                st.divider()


    # -----------------------------------------------------
    # FEE STATUS
    # -----------------------------------------------------

    st.subheader(
        f"📋 {selected_month} {selected_year} Fee Status"
    )

    header = st.columns(6)

    header[0].write("**Student**")
    header[1].write("**Class / Subject**")
    header[2].write("**Monthly Fee**")
    header[3].write("**Received**")
    header[4].write("**Pending**")
    header[5].write("**Status**")

    st.divider()


    for record in student_records:

        student_name = record[1]
        subject = record[2] or "-"
        monthly_fee = record[3] or 0
        amount_received = record[4] or 0

        pending = max(
            monthly_fee - amount_received,
            0
        )


        if (
            monthly_fee > 0
            and amount_received >= monthly_fee
        ):

            status = "✅ Paid"

        elif amount_received > 0:

            status = "🟡 Partial"

        else:

            status = "❌ Unpaid"


        row = st.columns(6)

        row[0].write(student_name)
        row[1].write(subject)

        row[2].write(
            f"Rs. {monthly_fee:,.0f}"
        )

        row[3].write(
            f"Rs. {amount_received:,.0f}"
        )

        row[4].write(
            f"Rs. {pending:,.0f}"
        )

        row[5].write(status)


# =========================================================
# MONTHLY REPORT
# =========================================================

elif page == "Monthly Report":

    st.title("📊 Monthly Fee Report")

    st.write(
        "View complete fee collection details for a selected month."
    )

    st.divider()


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


    cursor.execute("""
    SELECT
        students.id,
        students.name,
        students.subject,
        students.monthly_fee,
        COALESCE(SUM(payments.amount), 0),
        MAX(payments.payment_date)

    FROM students

    LEFT JOIN payments

    ON students.id = payments.student_id

    AND payments.month = ?

    AND payments.year = ?

    GROUP BY
        students.id,
        students.name,
        students.subject,
        students.monthly_fee

    ORDER BY students.name
    """, (
        report_month,
        report_year
    ))

    report_records = cursor.fetchall()


    total_expected = 0
    total_received = 0
    total_pending = 0

    paid_count = 0
    partial_count = 0
    unpaid_count = 0

    report_data = []


    for record in report_records:

        student_name = record[1]
        subject = record[2] or "-"
        monthly_fee = record[3] or 0
        amount_received = record[4] or 0
        payment_date = record[5] or "-"

        pending = max(
            monthly_fee - amount_received,
            0
        )


        total_expected += monthly_fee
        total_received += amount_received
        total_pending += pending


        if (
            monthly_fee > 0
            and amount_received >= monthly_fee
        ):

            status = "Paid"
            paid_count += 1

        elif amount_received > 0:

            status = "Partial"
            partial_count += 1

        else:

            status = "Unpaid"
            unpaid_count += 1


        report_data.append([
            student_name,
            subject,
            monthly_fee,
            amount_received,
            pending,
            status,
            payment_date
        ])


    st.subheader(
        f"📌 {report_month} {report_year} Summary"
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "💰 Total Expected",
        f"Rs. {total_expected:,.0f}"
    )

    col2.metric(
        "💵 Total Received",
        f"Rs. {total_received:,.0f}"
    )

    col3.metric(
        "⏳ Total Pending",
        f"Rs. {total_pending:,.0f}"
    )


    st.divider()


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "✅ Paid Students",
        paid_count
    )

    col2.metric(
        "🟡 Partial Payments",
        partial_count
    )

    col3.metric(
        "❌ Unpaid Students",
        unpaid_count
    )


    st.divider()


    st.subheader(
        "📋 Student Fee Details"
    )


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

        for column in [
            "Monthly Fee",
            "Amount Received",
            "Pending"
        ]:

            display_report[column] = (
                display_report[column]
                .apply(
                    lambda x:
                    f"Rs. {x:,.0f}"
                )
            )


        st.dataframe(
            display_report,
            use_container_width=True,
            hide_index=True
        )


    st.divider()


    st.subheader(
        "⏳ Pending Fee Students"
    )


    pending_data = [
        row
        for row in report_data
        if row[4] > 0
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


        for column in [
            "Monthly Fee",
            "Amount Received",
            "Pending"
        ]:

            display_pending[column] = (
                display_pending[column]
                .apply(
                    lambda x:
                    f"Rs. {x:,.0f}"
                )
            )


        st.dataframe(
            display_pending,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.success(
            "🎉 No pending fees for this month!"
        )


    st.divider()


    csv_report = report_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="📥 Download Monthly Report",
        data=csv_report,
        file_name=(
            f"{report_month}_{report_year}_fee_report.csv"
        ),
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# ADD STUDENT
# =========================================================

elif page == "Add Student":

    st.title("👨‍🎓 Add New Student")


    name = st.text_input(
        "Student Name"
    )


    subject = st.text_input(
        "Subject / Class"
    )


    monthly_fee = st.number_input(
        "Monthly Fee",
        min_value=0.0,
        step=500.0
    )


    if st.button(
        "➕ Add Student",
        use_container_width=True
    ):

        if not name.strip():

            st.error(
                "Please enter the student's name."
            )

        else:

            # Prevent duplicate student entry
            cursor.execute("""
            SELECT id
            FROM students
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            AND LOWER(TRIM(COALESCE(subject, ''))) =
                LOWER(TRIM(?))
            LIMIT 1
            """, (
                name.strip(),
                subject.strip()
            ))

            duplicate_student = cursor.fetchone()


            if duplicate_student:

                st.error(
                    f"❌ Student already exists "
                    f"with ID {duplicate_student[0]}."
                )

            else:

                cursor.execute("""
                INSERT INTO students
                (
                    name,
                    subject,
                    monthly_fee
                )

                VALUES (?, ?, ?)
                """, (
                    name.strip(),
                    subject.strip(),
                    monthly_fee
                ))

                conn.commit()


                st.success(
                    f"✅ {name} added successfully!"
                )

                st.rerun()


# =========================================================
# EDIT STUDENT
# =========================================================

elif page == "Edit Student":

    st.title("✏️ Edit Student")


    cursor.execute("""
    SELECT
        id,
        name,
        subject,
        monthly_fee

    FROM students

    ORDER BY name
    """)

    students = cursor.fetchall()


    if not students:

        st.warning(
            "No students found."
        )

    else:

        student_options = {
            f"{student[1]} | {student[2] or '-'} | ID {student[0]}":
            student[0]
            for student in students
        }


        selected_label = st.selectbox(
            "Select Student",
            list(student_options.keys()),
            key="edit_student_select"
        )


        student_id = student_options[
            selected_label
        ]


        cursor.execute("""
        SELECT
            id,
            name,
            subject,
            monthly_fee

        FROM students

        WHERE id = ?
        """, (
            student_id,
        ))


        selected_student = cursor.fetchone()


        new_name = st.text_input(
            "Student Name",
            value=selected_student[1],
            key="edit_student_name"
        )


        new_subject = st.text_input(
            "Subject / Class",
            value=selected_student[2] or "",
            key="edit_student_subject"
        )


        new_fee = st.number_input(
            "Monthly Fee",
            min_value=0.0,
            value=float(
                selected_student[3] or 0
            ),
            step=500.0,
            key="edit_student_fee"
        )


        st.info(
            "Changing the fee updates the student's current monthly fee."
        )


        if st.button(
            "💾 Update Student",
            use_container_width=True
        ):

            if not new_name.strip():

                st.error(
                    "Student name cannot be empty."
                )

            else:

                cursor.execute("""
                UPDATE students

                SET
                    name = ?,
                    subject = ?,
                    monthly_fee = ?

                WHERE id = ?
                """, (
                    new_name.strip(),
                    new_subject.strip(),
                    new_fee,
                    student_id
                ))


                conn.commit()


                st.success(
                    f"✅ {new_name} updated successfully!"
                )


                st.rerun()


# =========================================================
# RECORD FEE
# =========================================================

elif page == "Record Fee":

    st.title("💰 Record Fee Payment")

    st.write(
        "Record one payment per student for each month."
    )

    st.divider()


    cursor.execute("""
    SELECT
        id,
        name,
        subject,
        monthly_fee

    FROM students

    ORDER BY name
    """)

    students = cursor.fetchall()


    if not students:

        st.warning(
            "No students found. Please add students first."
        )

    else:

        student_options = {
            f"{student[1]} | {student[2] or '-'} | ID {student[0]}":
            student[0]
            for student in students
        }


        selected_label = st.selectbox(
            "👨‍🎓 Select Student",
            list(student_options.keys()),
            key="record_student"
        )


        student_id = student_options[
            selected_label
        ]


        cursor.execute("""
        SELECT
            id,
            name,
            subject,
            monthly_fee

        FROM students

        WHERE id = ?
        """, (
            student_id,
        ))


        selected_student = cursor.fetchone()


        student_name = selected_student[1]
        monthly_fee = selected_student[3] or 0


        st.info(
            f"💵 Monthly Fee: **Rs. {monthly_fee:,.0f}**"
        )


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


        amount = st.number_input(
            "💵 Payment Amount",
            min_value=0.0,
            step=500.0,
            key="record_amount"
        )


        payment_date = st.date_input(
            "📅 Payment Date",
            value=date.today(),
            key="record_payment_date"
        )


        cursor.execute("""
        SELECT
            id,
            amount,
            status,
            payment_date

        FROM payments

        WHERE student_id = ?
        AND month = ?
        AND year = ?

        ORDER BY id DESC
        LIMIT 1
        """, (
            student_id,
            month,
            year
        ))


        existing_payment = cursor.fetchone()


        payment_exists = existing_payment is not None


        if payment_exists:

            existing_payment_id = existing_payment[0]
            existing_amount = existing_payment[1] or 0

            st.error(
                f"⚠️ Payment already exists for "
                f"**{student_name}** in "
                f"**{month} {year}**.\n\n"
                f"Existing payment: "
                f"**Rs. {existing_amount:,.0f}**\n\n"
                f"Please use **Edit/Delete Payment** "
                f"to update this payment."
            )


        if amount >= monthly_fee and monthly_fee > 0:

            payment_status = "Paid"

        elif amount > 0:

            payment_status = "Partial"

        else:

            payment_status = "Unpaid"


        st.info(
            f"Payment Status: **{payment_status}**"
        )


        if st.button(
            "💾 Record Payment",
            use_container_width=True,
            key="record_payment_button"
        ):

            if payment_exists:

                st.error(
                    "❌ Payment was NOT recorded because "
                    "a payment already exists for this "
                    "student, month and year."
                )

            elif amount <= 0:

                st.error(
                    "Please enter a payment amount greater than 0."
                )

            else:

                cursor.execute("""
                INSERT INTO payments
                (
                    student_id,
                    month,
                    year,
                    amount,
                    status,
                    payment_date
                )

                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    month,
                    year,
                    amount,
                    payment_status,
                    payment_date.isoformat()
                ))


                conn.commit()


                st.success(
                    f"✅ Rs. {amount:,.0f} payment "
                    f"recorded for {student_name}."
                )


                st.rerun()


# =========================================================
# PAYMENT RECORDS
# =========================================================

elif page == "Payment Records":

    st.title("💳 Payment Records")

    st.write(
        "View all recorded student fee payments."
    )

    st.divider()


    cursor.execute("""
    SELECT
        payments.id,
        students.name,
        students.subject,
        payments.month,
        payments.year,
        payments.amount,
        payments.status,
        payments.payment_date

    FROM payments

    LEFT JOIN students

    ON payments.student_id = students.id

    ORDER BY
        payments.year DESC,
        CASE payments.month
            WHEN 'January' THEN 1
            WHEN 'February' THEN 2
            WHEN 'March' THEN 3
            WHEN 'April' THEN 4
            WHEN 'May' THEN 5
            WHEN 'June' THEN 6
            WHEN 'July' THEN 7
            WHEN 'August' THEN 8
            WHEN 'September' THEN 9
            WHEN 'October' THEN 10
            WHEN 'November' THEN 11
            WHEN 'December' THEN 12
        END DESC,
        payments.id DESC
    """)

    payment_records = cursor.fetchall()


    if not payment_records:

        st.info(
            "No payment records found."
        )

    else:

        payment_data = []


        for record in payment_records:

            payment_data.append([
                record[0],
                record[1] or "Deleted Student",
                record[2] or "-",
                record[3],
                record[4],
                record[5],
                record[6],
                record[7]
            ])


        payment_df = pd.DataFrame(
            payment_data,
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


        display_payment["Amount"] = (
            display_payment["Amount"]
            .apply(
                lambda x:
                f"Rs. {x:,.0f}"
            )
        )


        st.dataframe(
            display_payment,
            use_container_width=True,
            hide_index=True
        )


        st.divider()


        st.metric(
            "💵 Total Payments",
            f"Rs. {payment_df['Amount'].sum():,.0f}"
        )


# =========================================================
# EDIT / DELETE PAYMENT
# =========================================================

elif page == "Edit/Delete Payment":

    st.title("✏️ Edit / Delete Payment")

    st.write(
        "Select an existing payment to edit or delete it."
    )

    st.divider()


    cursor.execute("""
    SELECT
        payments.id,
        payments.student_id,
        students.name,
        students.subject,
        payments.month,
        payments.year,
        payments.amount,
        payments.status,
        payments.payment_date

    FROM payments

    LEFT JOIN students

    ON payments.student_id = students.id

    ORDER BY payments.id DESC
    """)

    payments = cursor.fetchall()


    if not payments:

        st.info(
            "No payment records available to edit or delete."
        )

    else:

        payment_options = {}


        for payment in payments:

            payment_id = payment[0]
            student_name = payment[2] or "Deleted Student"
            subject = payment[3] or "-"
            month = payment[4] or "-"
            year = payment[5] or "-"
            amount = payment[6] or 0

            label = (
                f"Payment ID {payment_id} | "
                f"{student_name} | "
                f"{subject} | "
                f"{month} {year} | "
                f"Rs. {amount:,.0f}"
            )

            payment_options[label] = payment_id


        selected_payment_label = st.selectbox(
            "💳 Select Payment",
            list(payment_options.keys()),
            key="edit_payment_select"
        )


        selected_payment_id = payment_options[
            selected_payment_label
        ]


        cursor.execute("""
        SELECT
            payments.id,
            payments.student_id,
            students.name,
            students.subject,
            payments.month,
            payments.year,
            payments.amount,
            payments.status,
            payments.payment_date

        FROM payments

        LEFT JOIN students

        ON payments.student_id = students.id

        WHERE payments.id = ?
        """, (
            selected_payment_id,
        ))


        selected_payment = cursor.fetchone()


        if selected_payment is None:

            st.error(
                "Payment record could not be found."
            )

        else:

            payment_id = selected_payment[0]
            student_id = selected_payment[1]
            student_name = selected_payment[2] or "Deleted Student"
            subject = selected_payment[3] or "-"
            old_month = selected_payment[4] or "January"
            old_year = selected_payment[5] or current_year
            old_amount = selected_payment[6] or 0
            old_payment_date = selected_payment[8]


            st.info(
                f"👨‍🎓 Student: **{student_name}**  \n"
                f"📚 Subject: **{subject}**  \n"
                f"🆔 Payment ID: **{payment_id}**"
            )


            st.divider()


            if old_month in months:

                old_month_index = months.index(
                    old_month
                )

            else:

                old_month_index = 0


            edit_month = st.selectbox(
                "📅 Month",
                months,
                index=old_month_index,
                key=f"edit_month_{payment_id}"
            )


            edit_year_options = years.copy()


            if old_year not in edit_year_options:

                edit_year_options.append(
                    old_year
                )

                edit_year_options.sort()


            old_year_index = edit_year_options.index(
                old_year
            )


            edit_year = st.selectbox(
                "📅 Year",
                edit_year_options,
                index=old_year_index,
                key=f"edit_year_{payment_id}"
            )


            edit_amount = st.number_input(
                "💵 Payment Amount",
                min_value=0.0,
                value=float(old_amount),
                step=500.0,
                key=f"edit_amount_{payment_id}"
            )


            student_fee = 0


            if student_id is not None:

                cursor.execute("""
                SELECT monthly_fee
                FROM students
                WHERE id = ?
                """, (
                    student_id,
                ))


                fee_result = cursor.fetchone()


                if fee_result:

                    student_fee = fee_result[0] or 0


            if (
                student_fee > 0
                and edit_amount >= student_fee
            ):

                edit_status = "Paid"

            elif edit_amount > 0:

                edit_status = "Partial"

            else:

                edit_status = "Unpaid"


            st.info(
                f"Payment Status: **{edit_status}**"
            )


            try:

                if old_payment_date:

                    payment_date_value = date.fromisoformat(
                        old_payment_date
                    )

                else:

                    payment_date_value = date.today()

            except ValueError:

                payment_date_value = date.today()


            edit_payment_date = st.date_input(
                "📅 Payment Date",
                value=payment_date_value,
                key=f"edit_date_{payment_id}"
            )


            st.divider()


            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "💾 Update Payment",
                    use_container_width=True,
                    key=f"update_payment_{payment_id}"
                ):

                    if edit_amount <= 0:

                        st.error(
                            "Payment amount must be greater than 0."
                        )

                    else:

                        cursor.execute("""
                        SELECT id
                        FROM payments
                        WHERE student_id = ?
                        AND month = ?
                        AND year = ?
                        AND id != ?
                        LIMIT 1
                        """, (
                            student_id,
                            edit_month,
                            edit_year,
                            payment_id
                        ))


                        duplicate_payment = cursor.fetchone()


                        if duplicate_payment:

                            st.error(
                                "❌ Another payment already exists "
                                "for this student, month and year. "
                                "Please choose another month/year."
                            )

                        else:

                            cursor.execute("""
                            UPDATE payments

                            SET
                                month = ?,
                                year = ?,
                                amount = ?,
                                status = ?,
                                payment_date = ?

                            WHERE id = ?
                            """, (
                                edit_month,
                                edit_year,
                                edit_amount,
                                edit_status,
                                edit_payment_date.isoformat(),
                                payment_id
                            ))


                            conn.commit()


                            st.success(
                                "✅ Payment updated successfully!"
                            )


                            st.rerun()


            with col2:

                if st.button(
                    "🗑️ Delete Payment",
                    use_container_width=True,
                    key=f"delete_payment_{payment_id}"
                ):

                    cursor.execute("""
                    DELETE FROM payments
                    WHERE id = ?
                    """, (
                        payment_id,
                    ))


                    conn.commit()


                    st.success(
                        "🗑️ Payment deleted successfully!"
                    )


                    st.rerun()


# =========================================================
# CLOSE DATABASE
# =========================================================

conn.close()