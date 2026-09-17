import streamlit as st
from supabase import create_client
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
    # GET TOTAL STUDENTS
    # -----------------------------------------------------

    students_count_response = (
        supabase
        .table("students")
        .select("id")
        .execute()
    )

    total_students = len(
        students_count_response.data or []
    )


    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_response = (
        supabase
        .table("students")
        .select(
            "id, name, subject, monthly_fee"
        )
        .order("name")
        .execute()
    )

    students_data = (
        students_response.data or []
    )


    # -----------------------------------------------------
    # GET PAYMENTS FOR SELECTED MONTH/YEAR
    # -----------------------------------------------------

    payments_response = (
        supabase
        .table("payments")
        .select(
            "student_id, amount"
        )
        .eq("month", selected_month)
        .eq("year", selected_year)
        .execute()
    )

    payments_data = (
        payments_response.data or []
    )


    # -----------------------------------------------------
    # CALCULATE PAYMENT TOTALS
    # -----------------------------------------------------

    payment_totals = {}

    for payment in payments_data:

        student_id = payment["student_id"]

        amount = payment["amount"] or 0

        payment_totals[student_id] = (
            payment_totals.get(student_id, 0)
            + amount
        )


    # -----------------------------------------------------
    # CREATE STUDENT RECORDS
    # -----------------------------------------------------

    student_records = []

    for student in students_data:

        student_id = student["id"]

        name = student["name"] or ""

        subject = student["subject"] or ""

        monthly_fee = (
            student["monthly_fee"] or 0
        )

        amount_received = payment_totals.get(
            student_id,
            0
        )

        student_records.append([
            student_id,
            name,
            subject,
            monthly_fee,
            amount_received
        ])


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


                info_col1, info_col2, info_col3 = (
                    st.columns(3)
                )


                info_col1.write(
                    f"🆔 **Student ID:** {student_id}"
                )

                info_col2.write(
                    f"📚 **Subject / Class:** {subject}"
                )

                info_col3.write(
                    f"💰 **Monthly Fee:** "
                    f"Rs. {monthly_fee:,.0f}"
                )


                info_col1, info_col2, info_col3 = (
                    st.columns(3)
                )


                info_col1.write(
                    f"💵 **Received:** "
                    f"Rs. {amount_received:,.0f}"
                )

                info_col2.write(
                    f"⏳ **Pending:** "
                    f"Rs. {pending:,.0f}"
                )

                info_col3.write(
                    f"📌 **Status:** {status}"
                )


                st.divider()


    # -----------------------------------------------------
    # FEE STATUS
    # -----------------------------------------------------

    st.subheader(
        f"📋 {selected_month} "
        f"{selected_year} Fee Status"
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
        "View complete fee collection details "
        "for a selected month."
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


    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_response = (
        supabase
        .table("students")
        .select(
            "id, name, subject, monthly_fee"
        )
        .order("name")
        .execute()
    )

    students_data = (
        students_response.data or []
    )


    # -----------------------------------------------------
    # GET PAYMENTS
    # -----------------------------------------------------

    payments_response = (
        supabase
        .table("payments")
        .select(
            "student_id, amount, payment_date"
        )
        .eq("month", report_month)
        .eq("year", report_year)
        .execute()
    )

    payments_data = (
        payments_response.data or []
    )


    # -----------------------------------------------------
    # PAYMENT TOTALS
    # -----------------------------------------------------

    payment_totals = {}

    payment_dates = {}


    for payment in payments_data:

        student_id = payment["student_id"]

        amount = payment["amount"] or 0


        payment_totals[student_id] = (
            payment_totals.get(student_id, 0)
            + amount
        )


        payment_dates[student_id] = (
            payment.get("payment_date")
        )


    # -----------------------------------------------------
    # CREATE REPORT RECORDS
    # -----------------------------------------------------

    report_records = []


    for student in students_data:

        student_id = student["id"]

        student_name = student["name"] or ""

        subject = student["subject"] or ""

        monthly_fee = (
            student["monthly_fee"] or 0
        )

        amount_received = payment_totals.get(
            student_id,
            0
        )

        payment_date = payment_dates.get(
            student_id,
            None
        )


        report_records.append([
            student_id,
            student_name,
            subject,
            monthly_fee,
            amount_received,
            payment_date
        ])


    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # STUDENT FEE DETAILS
    # -----------------------------------------------------

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
            f"No students found for "
            f"{report_month} {report_year}."
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


    # -----------------------------------------------------
    # PENDING STUDENTS
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # DOWNLOAD REPORT
    # -----------------------------------------------------

    csv_report = (
        report_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    st.download_button(
        label="📥 Download Monthly Report",
        data=csv_report,
        file_name=(
            f"{report_month}_{report_year}"
            "_fee_report.csv"
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

            # -------------------------------------------------
            # CHECK DUPLICATE STUDENT
            # -------------------------------------------------

            students_response = (
                supabase
                .table("students")
                .select(
                    "id, name, subject"
                )
                .execute()
            )


            students_data = (
                students_response.data or []
            )


            duplicate_student = None


            for student in students_data:

                existing_name = (
                    student["name"] or ""
                ).strip().lower()


                existing_subject = (
                    student["subject"] or ""
                ).strip().lower()


                if (
                    existing_name
                    == name.strip().lower()
                    and
                    existing_subject
                    == subject.strip().lower()
                ):

                    duplicate_student = student

                    break


            if duplicate_student:

                st.error(
                    f"❌ Student already exists "
                    f"with ID "
                    f"{duplicate_student['id']}."
                )


            else:

                # ---------------------------------------------
                # INSERT STUDENT
                # ---------------------------------------------

                supabase.table(
                    "students"
                ).insert({
                    "name": name.strip(),
                    "subject": subject.strip(),
                    "monthly_fee": monthly_fee
                }).execute()


                st.success(
                    f"✅ {name} added successfully!"
                )


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
                f"{student['subject'] or '-'} | "
                f"ID {student['id']}"
            ):
            student["id"]
            for student in students
        }

        selected_label = st.selectbox(
            "Select Student",
            list(student_options.keys()),
            key="edit_student_select"
        )

        student_id = student_options[selected_label]

        # Get selected student's current data
        selected_student = next(
            (
                student
                for student in students
                if student["id"] == student_id
            ),
            None
        )

        if selected_student:

            st.subheader("Edit Student Information")

            new_name = st.text_input(
                "Student Name",
                value=selected_student["name"],
                key="edit_name"
            )

            new_subject = st.text_input(
                "Subject",
                value=selected_student["subject"] or "",
                key="edit_subject"
            )

            new_monthly_fee = st.number_input(
                "Monthly Fee",
                min_value=0.0,
                value=float(selected_student["monthly_fee"]),
                step=500.0,
                key="edit_fee"
            )

            # UPDATE STUDENT
            if st.button(
                "💾 Update Student",
                key="update_student_button"
            ):

                if not new_name.strip():
                    st.error("Student name cannot be empty.")

                else:

                    supabase.table("students").update({
                        "name": new_name.strip(),
                        "subject": new_subject.strip(),
                        "monthly_fee": new_monthly_fee
                    }).eq(
                        "id",
                        student_id
                    ).execute()

                    st.success("Student updated successfully! ✅")

                    st.rerun()

            st.divider()

            # DELETE STUDENT
            st.subheader("🗑️ Delete Student")

            st.warning(
                "Deleting a student will also delete all payment "
                "records associated with this student."
            )

            confirm_delete = st.checkbox(
                "I understand that this action cannot be undone.",
                key="confirm_delete_student"
            )

            if st.button(
                "🗑️ Delete Student",
                key="delete_student_button"
            ):

                if not confirm_delete:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    # Delete payment records first
                    supabase.table("payments").delete().eq(
                        "student_id",
                        student_id
                    ).execute()

                    # Then delete the student
                    supabase.table("students").delete().eq(
                        "id",
                        student_id
                    ).execute()

                    st.success(
                        "Student and associated payment records "
                        "deleted successfully! ✅"
                    )

                    st.rerun()
        # -----------------------------------------------------
        # GET SELECTED STUDENT
        # -----------------------------------------------------

        selected_student_response = (
            supabase
            .table("students")
            .select(
                "id, name, subject, monthly_fee"
            )
            .eq("id", student_id)
            .limit(1)
            .execute()
        )


        selected_student_data = (
            selected_student_response.data or []
        )


        if not selected_student_data:

            st.error(
                "Student record could not be found."
            )

        else:

            selected_student = (
                selected_student_data[0]
            )


            new_name = st.text_input(
                "Student Name",
                value=selected_student["name"] or "",
                key="edit_student_name"
            )


            new_subject = st.text_input(
                "Subject / Class",
                value=selected_student["subject"] or "",
                key="edit_student_subject"
            )


            new_fee = st.number_input(
                "Monthly Fee",
                min_value=0.0,
                value=float(
                    selected_student["monthly_fee"] or 0
                ),
                step=500.0,
                key="edit_student_fee"
            )


            st.info(
                "Changing the fee updates the "
                "student's current monthly fee."
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

                    supabase.table(
                        "students"
                    ).update({
                        "name": new_name.strip(),
                        "subject": new_subject.strip(),
                        "monthly_fee": new_fee
                    }).eq(
                        "id",
                        student_id
                    ).execute()


                    st.success(
                        f"✅ {new_name} "
                        "updated successfully!"
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


    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_response = (
        supabase
        .table("students")
        .select(
            "id, name, subject, monthly_fee"
        )
        .order("name")
        .execute()
    )


    students = (
        students_response.data or []
    )


    if not students:

        st.warning(
            "No students found. "
            "Please add students first."
        )

    else:

        student_options = {
            (
                f"{student['name']} | "
                f"{student['subject'] or '-'} | "
                f"ID {student['id']}"
            ):
            student["id"]
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


        # -----------------------------------------------------
        # GET SELECTED STUDENT
        # -----------------------------------------------------

        selected_student_response = (
            supabase
            .table("students")
            .select(
                "id, name, subject, monthly_fee"
            )
            .eq("id", student_id)
            .limit(1)
            .execute()
        )


        selected_student_data = (
            selected_student_response.data or []
        )


        if not selected_student_data:

            st.error(
                "Student record could not be found."
            )

        else:

            selected_student = (
                selected_student_data[0]
            )


            student_name = (
                selected_student["name"] or ""
            )


            monthly_fee = (
                selected_student["monthly_fee"] or 0
            )


            st.info(
                f"💵 Monthly Fee: "
                f"**Rs. {monthly_fee:,.0f}**"
            )


            # -------------------------------------------------
            # MONTH / YEAR
            # -------------------------------------------------

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


            # -------------------------------------------------
            # PAYMENT AMOUNT
            # -------------------------------------------------

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


            # -------------------------------------------------
            # CHECK EXISTING PAYMENT
            # -------------------------------------------------

            existing_payment_response = (
                supabase
                .table("payments")
                .select(
                    "id, amount, status, payment_date"
                )
                .eq(
                    "student_id",
                    student_id
                )
                .eq(
                    "month",
                    month
                )
                .eq(
                    "year",
                    year
                )
                .order(
                    "id",
                    desc=True
                )
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


            payment_exists = (
                existing_payment is not None
            )


            if payment_exists:

                existing_amount = (
                    existing_payment["amount"] or 0
                )


                st.error(
                    f"⚠️ Payment already exists for "
                    f"**{student_name}** in "
                    f"**{month} {year}**.\n\n"
                    f"Existing payment: "
                    f"**Rs. {existing_amount:,.0f}**\n\n"
                    f"Please use **Edit/Delete Payment** "
                    f"to update this payment."
                )


            # -------------------------------------------------
            # PAYMENT STATUS
            # -------------------------------------------------

            if (
                amount >= monthly_fee
                and monthly_fee > 0
            ):

                payment_status = "Paid"

            elif amount > 0:

                payment_status = "Partial"

            else:

                payment_status = "Unpaid"


            st.info(
                f"Payment Status: "
                f"**{payment_status}**"
            )


            # -------------------------------------------------
            # RECORD PAYMENT
            # -------------------------------------------------

            if st.button(
                "💾 Record Payment",
                use_container_width=True,
                key="record_payment_button"
            ):

                if payment_exists:

                    st.error(
                        "❌ Payment was NOT recorded "
                        "because a payment already "
                        "exists for this student, "
                        "month and year."
                    )


                elif amount <= 0:

                    st.error(
                        "Please enter a payment amount "
                        "greater than 0."
                    )


                else:

                    supabase.table(
                        "payments"
                    ).insert({
                        "student_id": student_id,
                        "month": month,
                        "year": year,
                        "amount": amount,
                        "status": payment_status,
                        "payment_date": (
                            payment_date.isoformat()
                        )
                    }).execute()


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


    # -----------------------------------------------------
    # GET PAYMENTS
    # -----------------------------------------------------

    payments_response = (
        supabase
        .table("payments")
        .select(
            """
            id,
            student_id,
            month,
            year,
            amount,
            status,
            payment_date
            """
        )
        .order(
            "id",
            desc=True
        )
        .execute()
    )


    payments_data = (
        payments_response.data or []
    )


    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_response = (
        supabase
        .table("students")
        .select(
            "id, name, subject"
        )
        .execute()
    )


    students_data = (
        students_response.data or []
    )


    # -----------------------------------------------------
    # CREATE STUDENT LOOKUP
    # -----------------------------------------------------

    student_lookup = {
        student["id"]: student
        for student in students_data
    }


    # -----------------------------------------------------
    # CREATE PAYMENT LIST
    # -----------------------------------------------------

    payments = []


    for payment in payments_data:

        student = student_lookup.get(
            payment["student_id"],
            {}
        )


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


    # -----------------------------------------------------
    # DISPLAY PAYMENTS
    # -----------------------------------------------------

    if not payments:

        st.info(
            "No payment records found."
        )


    else:

        payment_data = []


        for record in payments:

            payment_data.append([
                record[0],
                record[1] or "Deleted Student",
                record[2] or "-",
                record[3],
                record[4],
                record[5] or 0,
                record[6] or "-",
                record[7] or "-"
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


        display_payment = (
            payment_df.copy()
        )


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


        total_payment_amount = (
            payment_df["Amount"].sum()
        )


        st.metric(
            "💵 Total Payments",
            f"Rs. {total_payment_amount:,.0f}"
        )


# =========================================================
# EDIT / DELETE PAYMENT
# =========================================================

elif page == "Edit/Delete Payment":

    st.title("✏️ Edit / Delete Payment")


    st.write(
        "Select an existing payment to edit "
        "or delete it."
    )


    st.divider()


    # -----------------------------------------------------
    # GET ALL PAYMENTS
    # -----------------------------------------------------

    payments_response = (
        supabase
        .table("payments")
        .select(
            """
            id,
            student_id,
            month,
            year,
            amount,
            status,
            payment_date
            """
        )
        .order(
            "id",
            desc=True
        )
        .execute()
    )


    payments_data = (
        payments_response.data or []
    )


    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_response = (
        supabase
        .table("students")
        .select(
            "id, name, subject"
        )
        .execute()
    )


    students_data = (
        students_response.data or []
    )


    student_lookup = {
        student["id"]: student
        for student in students_data
    }


    # -----------------------------------------------------
    # CREATE PAYMENT LIST
    # -----------------------------------------------------

    payments = []


    for payment in payments_data:

        student = student_lookup.get(
            payment["student_id"],
            {}
        )


        payments.append([
            payment["id"],
            payment["student_id"],
            student.get("name"),
            student.get("subject"),
            payment["month"],
            payment["year"],
            payment["amount"],
            payment["status"],
            payment["payment_date"]
        ])


    # -----------------------------------------------------
    # CHECK PAYMENTS
    # -----------------------------------------------------

    if not payments:

        st.info(
            "No payment records available "
            "to edit or delete."
        )


    else:

        payment_options = {}


        for payment in payments:

            payment_id = payment[0]

            student_name = (
                payment[2]
                or "Deleted Student"
            )

            subject = (
                payment[3]
                or "-"
            )

            month = (
                payment[4]
                or "-"
            )

            year = (
                payment[5]
                or "-"
            )

            amount = (
                payment[6]
                or 0
            )


            label = (
                f"Payment ID {payment_id} | "
                f"{student_name} | "
                f"{subject} | "
                f"{month} {year} | "
                f"Rs. {amount:,.0f}"
            )


            payment_options[label] = (
                payment_id
            )


        # -------------------------------------------------
        # SELECT PAYMENT
        # -------------------------------------------------

        selected_payment_label = (
            st.selectbox(
                "💳 Select Payment",
                list(
                    payment_options.keys()
                ),
                key="edit_payment_select"
            )
        )


        selected_payment_id = (
            payment_options[
                selected_payment_label
            ]
        )


        # -------------------------------------------------
        # GET SELECTED PAYMENT
        # -------------------------------------------------

        selected_payment_response = (
            supabase
            .table("payments")
            .select(
                """
                id,
                student_id,
                month,
                year,
                amount,
                status,
                payment_date
                """
            )
            .eq(
                "id",
                selected_payment_id
            )
            .limit(1)
            .execute()
        )


        selected_payment_data = (
            selected_payment_response.data
            or []
        )


        if not selected_payment_data:

            st.error(
                "Payment record could not be found."
            )


        else:

            payment = (
                selected_payment_data[0]
            )


            payment_id = payment["id"]

            student_id = payment["student_id"]

            old_month = (
                payment["month"]
                or "January"
            )

            old_year = (
                payment["year"]
                or current_year
            )

            old_amount = (
                payment["amount"]
                or 0
            )

            old_status = (
                payment["status"]
                or "Unpaid"
            )

            old_payment_date = (
                payment["payment_date"]
            )


            student = student_lookup.get(
                student_id,
                {}
            )


            student_name = (
                student.get("name")
                or "Deleted Student"
            )

            subject = (
                student.get("subject")
                or "-"
            )


            # -------------------------------------------------
            # STUDENT INFO
            # -------------------------------------------------

            st.info(
                f"👨‍🎓 Student: "
                f"**{student_name}**  \n"
                f"📚 Subject: "
                f"**{subject}**  \n"
                f"🆔 Payment ID: "
                f"**{payment_id}**"
            )


            st.divider()


            # -------------------------------------------------
            # MONTH
            # -------------------------------------------------

            if old_month in months:

                old_month_index = (
                    months.index(old_month)
                )

            else:

                old_month_index = 0


            edit_month = st.selectbox(
                "📅 Month",
                months,
                index=old_month_index,
                key=f"edit_month_{payment_id}"
            )


            # -------------------------------------------------
            # YEAR
            # -------------------------------------------------

            edit_year_options = years.copy()


            if old_year not in edit_year_options:

                edit_year_options.append(
                    old_year
                )

                edit_year_options.sort()


            old_year_index = (
                edit_year_options.index(
                    old_year
                )
            )


            edit_year = st.selectbox(
                "📅 Year",
                edit_year_options,
                index=old_year_index,
                key=f"edit_year_{payment_id}"
            )


            # -------------------------------------------------
            # AMOUNT
            # -------------------------------------------------

            edit_amount = st.number_input(
                "💵 Payment Amount",
                min_value=0.0,
                value=float(old_amount),
                step=500.0,
                key=f"edit_amount_{payment_id}"
            )


            # -------------------------------------------------
            # GET STUDENT FEE
            # -------------------------------------------------

            student_fee = 0


            if student_id is not None:

                fee_response = (
                    supabase
                    .table("students")
                    .select("monthly_fee")
                    .eq(
                        "id",
                        student_id
                    )
                    .limit(1)
                    .execute()
                )


                fee_data = (
                    fee_response.data or []
                )


                if fee_data:

                    student_fee = (
                        fee_data[0]["monthly_fee"]
                        or 0
                    )


            # -------------------------------------------------
            # PAYMENT STATUS
            # -------------------------------------------------

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
                f"Payment Status: "
                f"**{edit_status}**"
            )


            # -------------------------------------------------
            # PAYMENT DATE
            # -------------------------------------------------

            try:

                if old_payment_date:

                    payment_date_value = (
                        date.fromisoformat(
                            old_payment_date
                        )
                    )

                else:

                    payment_date_value = (
                        date.today()
                    )

            except (ValueError, TypeError):

                payment_date_value = (
                    date.today()
                )


            edit_payment_date = st.date_input(
                "📅 Payment Date",
                value=payment_date_value,
                key=f"edit_date_{payment_id}"
            )


            st.divider()


            col1, col2 = st.columns(2)


            # =================================================
            # UPDATE PAYMENT
            # =================================================

            with col1:

                if st.button(
                    "💾 Update Payment",
                    use_container_width=True,
                    key=(
                        f"update_payment_"
                        f"{payment_id}"
                    )
                ):

                    if edit_amount <= 0:

                        st.error(
                            "Payment amount must be "
                            "greater than 0."
                        )


                    else:

                        # -------------------------------------
                        # CHECK DUPLICATE
                        # -------------------------------------

                        duplicate_response = (
                            supabase
                            .table("payments")
                            .select("id")
                            .eq(
                                "student_id",
                                student_id
                            )
                            .eq(
                                "month",
                                edit_month
                            )
                            .eq(
                                "year",
                                edit_year
                            )
                            .neq(
                                "id",
                                payment_id
                            )
                            .limit(1)
                            .execute()
                        )


                        duplicate_data = (
                            duplicate_response.data
                            or []
                        )


                        duplicate_payment = (
                            duplicate_data[0]
                            if duplicate_data
                            else None
                        )


                        if duplicate_payment:

                            st.error(
                                "❌ Another payment "
                                "already exists for "
                                "this student, month "
                                "and year. Please "
                                "choose another "
                                "month/year."
                            )


                        else:

                            # ---------------------------------
                            # UPDATE PAYMENT
                            # ---------------------------------

                            supabase.table(
                                "payments"
                            ).update({
                                "month": edit_month,
                                "year": edit_year,
                                "amount": edit_amount,
                                "status": edit_status,
                                "payment_date": (
                                    edit_payment_date
                                    .isoformat()
                                )
                            }).eq(
                                "id",
                                payment_id
                            ).execute()


                            st.success(
                                "✅ Payment updated "
                                "successfully!"
                            )


                            st.rerun()


            # =================================================
            # DELETE PAYMENT
            # =================================================

            with col2:

                if st.button(
                    "🗑️ Delete Payment",
                    use_container_width=True,
                    key=(
                        f"delete_payment_"
                        f"{payment_id}"
                    )
                ):

                    supabase.table(
                        "payments"
                    ).delete().eq(
                        "id",
                        payment_id
                    ).execute()


                    st.success(
                        "🗑️ Payment deleted "
                        "successfully!"
                    )


                    st.rerun()

                    st.write("Supabase URL loaded:", bool(st.secrets["SUPABASE_URL"]))
st.write("Supabase KEY loaded:", bool(st.secrets["SUPABASE_KEY"]))