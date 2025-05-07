import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Salary Analyzer", layout="wide")
st.title("💼 Salary Hike & Fair Pay Analyzer")

st.markdown("Welcome to your personalized salary analysis tool! Fill in your details to get started.")

with st.form("salary_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("👤 Full Name")
        company = st.text_input("🏢 Company Name")
        designation = st.text_input("🧑‍💻 Designation")
        experience = st.selectbox("📅 Work Experience", ["Fresher", "1-2 yrs", "3-5 yrs", "6-10 yrs", "10-15 yrs", "15+ yrs"])
    
    with col2:
        location = st.selectbox("📍 Work Location", ["Bangalore", "Hyderabad", "Mumbai", "Delhi", "Kolkata", "Chennai", "Pune", "Others"])
        tax_regime = st.radio("💸 Tax Regime", ["New Tax Regime", "Old Tax Regime", "New Regime (post Budget 2025-26)"])
        annual_ctc = st.number_input("💰 Annual CTC (LPA)", min_value=1.0, step=0.1)
        in_hand = st.number_input("📥 Monthly In-hand Salary (₹)", min_value=1000.0, step=100.0)

    submitted = st.form_submit_button("Analyze Salary 🔍")

if submitted and name:
    st.divider()
    gross_monthly = (annual_ctc * 1e5) / 12
    in_hand_ratio = in_hand / gross_monthly

    if experience == "Fresher":
        fair_min, fair_max = 0.50, 0.55
    elif experience == "1-2 yrs":
        fair_min, fair_max = 0.50, 0.55
    elif experience == "3-5 yrs":
        fair_min, fair_max = 0.55, 0.60
    elif experience == "6-10 yrs":
        fair_min, fair_max = 0.60, 0.65
    elif experience == "10-15 yrs":
        fair_min, fair_max = 0.65, 0.70
    else:
        fair_min, fair_max = 0.70, 0.75

    if fair_min <= in_hand_ratio <= fair_max:
        fair_comment = "✅ You are fairly paid as per your experience level."
    elif in_hand_ratio < fair_min:
        fair_comment = "⚠️ You might be underpaid based on market standards."
    else:
        fair_comment = "🎉 You are earning above market expectations!"

    st.subheader(f"Hello, {name}! 👋")
    st.info(f"""
**Designation**: {designation}  
**Company**: {company}  
**Work Location**: {location}  
**Experience**: {experience}  
**Annual CTC**: ₹{annual_ctc:.2f} LPA  
**Monthly In-hand**: ₹{in_hand:.2f}  
**Tax Regime**: {tax_regime}  
**Analysis**: {fair_comment}
""")

    hike_range = range(5, 201, 5)
    data = []

    for hike in hike_range:
        new_gross = gross_monthly * (1 + hike / 100)
        new_inhand = new_gross * in_hand_ratio
        arrear = new_inhand - in_hand
        may_salary = new_inhand + arrear
        data.append({
            "Hike %": hike,
            "New Gross Monthly": round(new_gross, 2),
            "New In-hand": round(new_inhand, 2),
            "April Arrear": round(arrear, 2),
            "May In-hand Salary": round(may_salary, 2)
        })

    df = pd.DataFrame(data)

    st.subheader("📊 Salary Projection Table")
    st.dataframe(df, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig1 = px.line(df, x="Hike %", y="New In-hand", title="📈 Hike % vs New In-hand Salary", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

    with col4:
        fig2 = px.bar(df, x="Hike %", y="May In-hand Salary", title="💵 Hike % vs May Salary (Incl. Arrear)")
        st.plotly_chart(fig2, use_container_width=True)

    def to_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            user_info = pd.DataFrame({
                "Name": [name], "Company": [company], "Designation": [designation], "Location": [location],
                "Experience": [experience], "Tax Regime": [tax_regime], "CTC (LPA)": [annual_ctc],
                "In-hand Monthly": [in_hand], "Fair Pay Comment": [fair_comment]
            })
            user_info.to_excel(writer, index=False, sheet_name="User Info")
            dataframe.to_excel(writer, index=False, sheet_name="Salary Analysis")
        output.seek(0)
        return output

    st.download_button(
        label="📥 Download Excel Report",
        data=to_excel(df),
        file_name=f"{name.replace(' ', '_')}_Salary_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
