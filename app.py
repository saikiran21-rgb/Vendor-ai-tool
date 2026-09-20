import streamlit as st
import pandas as pd
import altair as alt
from fpdf import FPDF
 
 
def detect_final_cost_column(df):
    final_keywords = ["final", "total", "grand", "net", "amount", "payable", "due", "cost"]
    columns = [col.lower() for col in df.columns]
 
    # Detect Qty column
    qty_column = None
    for col in df.columns:
        if col.lower() in ["qty", "quantity"]:
            qty_column = col
            break
 
    # Find matching cost columns
    matches = [
        df.columns[i]
        for i, col in enumerate(columns)
        if any(keyword in col for keyword in final_keywords)
    ]
 
    if not matches:
        return None
 
    # Prefer cost columns that appear AFTER Qty
    if qty_column:
        qty_index = df.columns.get_loc(qty_column)
        matches_after_qty = [col for col in matches if df.columns.get_loc(col) > qty_index]
        if matches_after_qty:
            matches = matches_after_qty
 
    # Pick the most specific column name
    matches_sorted = sorted(matches, key=lambda x: len(x), reverse=True)
    return matches_sorted[0]
 
 
def generate_pdf(vendor_costs, cheapest_vendor, cheapest_cost, savings_percentage):
    """Build a simple PDF report using fpdf2 (pure Python, no external binary needed)."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Vendor Comparison Report", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
 
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Vendor Cost Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for vendor, cost in vendor_costs.items():
        pdf.cell(0, 7, f"{vendor}: {cost:,.2f}", new_x="LMARGIN", new_y="NEXT")
 
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Result", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Cheapest Vendor: {cheapest_vendor} ({cheapest_cost:,.2f})", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Savings Percentage: {savings_percentage:.2f}%", new_x="LMARGIN", new_y="NEXT")
 
    # fpdf2 returns a bytearray with dest="S"; Streamlit's download_button needs bytes
    return bytes(pdf.output(dest="S"))
 
 
st.title("Vendor Comparison AI Tool")
 
uploaded_files = st.file_uploader("Upload Vendor Quote Files", accept_multiple_files=True, type=["xlsx"])
 
if st.button("Compare Vendors"):
    if not uploaded_files:
        st.warning("Please upload at least one vendor quote file first.")
        st.stop()
 
    vendor_costs = {}
 
    # 1. Read files and detect cost column
    for file in uploaded_files:
        df = pd.read_excel(file)
        vendor_name = file.name.replace(".xlsx", "")
        final_cost_column = detect_final_cost_column(df)
 
        if final_cost_column is None:
            st.error(f"No final cost column found in {file.name}")
            continue
 
        total_cost = df[final_cost_column].sum()
        vendor_costs[vendor_name] = total_cost
 
    if not vendor_costs:
        st.error("No valid cost data found in any uploaded file.")
        st.stop()
 
    # 2. Vendor summary
    st.subheader("Vendor Cost Summary")
    for vendor, cost in vendor_costs.items():
        st.write(f"{vendor}: {cost}")
 
    # 3. Cheapest vendor
    cheapest_vendor = min(vendor_costs, key=vendor_costs.get)
    cheapest_cost = vendor_costs[cheapest_vendor]
    st.success(f"Cheapest Vendor → {cheapest_vendor} ({cheapest_cost})")
 
    # 4. Savings percentage
    highest_cost = max(vendor_costs.values())
    lowest_cost = min(vendor_costs.values())
    savings_percentage = ((highest_cost - lowest_cost) / highest_cost) * 100 if highest_cost else 0
 
    st.subheader("Savings Analysis")
    st.write(f"Highest Vendor Cost: {highest_cost}")
    st.write(f"Lowest Vendor Cost: {lowest_cost}")
    st.write(f"Savings Percentage: {savings_percentage:.2f}%")
 
    # 5. Bar chart (Altair)
    st.subheader("Vendor Cost Bar Chart")
    df_table = pd.DataFrame({
        "Vendor": list(vendor_costs.keys()),
        "Cost": list(vendor_costs.values())
    })
    chart = alt.Chart(df_table).mark_bar().encode(
        x="Vendor",
        y="Cost",
        color="Vendor"
    )
    st.altair_chart(chart, use_container_width=True)
 
    # 6. Color-coded vendor table
    st.subheader("Color-Coded Vendor Table")
    min_cost = df_table["Cost"].min()
    max_cost = df_table["Cost"].max()
 
    def highlight_row(row):
        if row["Cost"] == min_cost:
            return ["background-color: #d4f7d4"] * len(row)
        elif row["Cost"] == max_cost:
            return ["background-color: #f7d4d4"] * len(row)
        else:
            return ["background-color: #fff7d4"] * len(row)
 
    st.dataframe(df_table.style.apply(highlight_row, axis=1))
 
    # 7. PDF report download
    pdf_bytes = generate_pdf(vendor_costs, cheapest_vendor, cheapest_cost, savings_percentage)
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="vendor_comparison.pdf",
        mime="application/pdf"
    )
