import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("💰 Amortization Calculator")

st.write("Upload an Excel file or manually enter details to calculate amortization schedule.")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file (optional)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
else:
    st.subheader("Manual Input")
    payee_id = st.text_input("Payee ID", "EMP-101")
    total_incentive = st.number_input("Total Incentive", min_value=0.0, value=12000.0)
    cap = st.number_input("Cap (%)", min_value=0.0, value=90.0)
    term = st.number_input("Term", min_value=1, value=12)
    frequency = st.selectbox("Payment Frequency", ["Monthly", "Quarterly"])
    start_date = st.date_input("Payment Start Date", datetime(2025, 2, 1))

    df = pd.DataFrame([{
        "Payee ID": payee_id,
        "Total Incentive": total_incentive,
        "Cap %": cap,
        "Term": term,
        "Payment Frequency": frequency,
        "Payment Start Date": start_date.strftime("%Y-%m-%d")
    }])

if st.button("Calculate Amortization"):
    results = []

    for _, row in df.iterrows():
        total = row["Total Incentive"]
        cap = row["Cap %"] / 100
        term = int(row["Term"])
        freq = row["Payment Frequency"].lower()
        start = datetime.strptime(str(row["Payment Start Date"]), "%Y-%m-%d")

        step = 30 if freq == "monthly" else 90
        payment_amount = (total * cap) / term
        cumulative = 0

        for i in range(1, term + 1):
            pay_date = start + timedelta(days=step * (i - 1))
            cumulative += payment_amount
            results.append({
                "Payee ID": row["Payee ID"],
                "Payment No": i,
                "Payment Date": pay_date.strftime("%Y-%m-%d"),
                "Payment Amount": round(payment_amount, 2),
                "Cumulative Amount": round(cumulative, 2),
                "End Date": (start + timedelta(days=step * term)).strftime("%Y-%m-%d")
            })

    result_df = pd.DataFrame(results)
    st.success("✅ Amortization calculated successfully!")
    st.dataframe(result_df)

    st.download_button(
        "Download Results as Excel",
        data=result_df.to_csv(index=False).encode('utf-8'),
        file_name="amortization_schedule.csv",
        mime="text/csv"
    )