import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

st.set_page_config(page_title="Salary App", layout="wide")

# Sidebar
tab = st.sidebar.radio("📂 Select a feature", ["🏠 Home", "📈 Salary Analyzer", "📊 Salary Predictor"])

# ------------------ 🏠 Home ------------------
if tab == "🏠 Home":
    st.title("🏠 Welcome to the Salary App")
    st.markdown("""
    This application helps you:
    - 🔍 Analyze your salary and get fair pay insights  
    - 💹 Simulate different hike scenarios  
    - 🤖 Predict expected salary using machine learning  

    Use the sidebar to navigate between tools.
    """)

# ------------------ 📈 Salary Analyzer ------------------
elif tab == "📈 Salary Analyzer":
    st.title("💼 Salary Hike & Fair Pay Analyzer")
    st.markdown("Welcome to your personalized salary analysis tool for 2025. Fill in your details to get started.")

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

            if annual_ctc <= 6:
                estimated_ratio = 0.85
            elif annual_ctc <= 12:
                estimated_ratio = 0.80
            elif annual_ctc <= 20:
                estimated_ratio = 0.75
            else:
                estimated_ratio = 0.70

            experience_factor = 0
            if experience == "1-2 yrs":
                experience_factor = 0.02
            elif experience == "3-5 yrs":
                experience_factor = 0.05
            elif experience == "6-10 yrs":
                experience_factor = 0.07
            elif experience == "10-15 yrs":
                experience_factor = 0.10
            elif experience == "15+ yrs":
                experience_factor = 0.12

            adjusted_ratio = estimated_ratio + experience_factor
            gross_monthly = (annual_ctc * 1e5) / 12
            estimated_in_hand = round(gross_monthly * adjusted_ratio, -2)

            in_hand = st.number_input(
                f"📥 Monthly In-hand Salary (₹) [Estimated: ₹{estimated_in_hand:,.0f}]",
                min_value=1000.0,
                step=100.0,
                value=estimated_in_hand,
                key="editable_in_hand"
            )

        submitted = st.form_submit_button("Analyze Salary 🔍")

    if submitted and name:
        st.divider()
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
**Monthly In-hand**: ₹{in_hand:,.2f}  
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
                "New Gross Monthly (₹)": round(new_gross, 2),
                "New In-hand (₹)": round(new_inhand, 2),
                "April Arrear (₹)": round(arrear, 2),
                "May In-hand Salary (₹)": round(may_salary, 2)
            })

        df = pd.DataFrame(data)

        st.subheader("📊 Salary Projection Table")
        st.dataframe(df, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig1 = px.line(df, x="Hike %", y="New In-hand (₹)", title="📈 Hike % vs New In-hand Salary", markers=True)
            st.plotly_chart(fig1, use_container_width=True)

        with col4:
            fig2 = px.bar(df, x="Hike %", y="May In-hand Salary (₹)", title="💵 Hike % vs May Salary (Incl. Arrear)")
            st.plotly_chart(fig2, use_container_width=True)

        def to_excel(user_info_df, salary_df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                user_info_df.to_excel(writer, index=False, sheet_name="User Info")
                salary_df.to_excel(writer, index=False, sheet_name="Salary Analysis")
            output.seek(0)
            return output

        user_df = pd.DataFrame({
            "Name": [name], "Company": [company], "Designation": [designation],
            "Location": [location], "Experience": [experience], "Tax Regime": [tax_regime],
            "Annual CTC (LPA)": [annual_ctc], "Monthly In-hand (₹)": [in_hand],
            "CTC to In-hand Ratio": [round(in_hand_ratio, 3)], "Fair Pay Comment": [fair_comment]
        })

        st.download_button(
            label="📥 Download Excel Report",
            data=to_excel(user_df, df),
            file_name=f"{name.replace(' ', '_')}_Salary_Report_2025.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ------------------ 📊 Salary Predictor ------------------
elif tab == "📊 Salary Predictor":
    st.title("📊 Salary Predictor (ML-Based)")
    st.markdown("Enter your job profile details to predict your expected annual salary.")

    col1, col2 = st.columns(2)

    with col1:
        role = st.selectbox("🧑‍💻 Role", ["Software Engineer", "Data Analyst", "Project Manager", "DevOps", "HR", "Finance"])
        education = st.selectbox("🎓 Education Level", ["Bachelor's", "Master's", "PhD"])
        experience_years = st.slider("📅 Years of Experience", 0, 30, 3)

    with col2:
        location = st.selectbox("📍 Location", ["Bangalore", "Hyderabad", "Mumbai", "Delhi", "Chennai", "Other"])
        industry = st.selectbox("🏢 Industry", ["IT", "Finance", "Healthcare", "Manufacturing", "Other"])
        skills = st.multiselect("🛠️ Key Skills", ["Python", "SQL", "AWS", "Excel", "Java", "Leadership"])

    predict_btn = st.button("🎯 Predict Salary")

    if predict_btn:
        # Simulate a model using dummy encoding and coefficients
        base_salary = 4  # Base in LPA

        role_factor = {
            "Software Engineer": 2.0,
            "Data Analyst": 1.8,
            "Project Manager": 3.0,
            "DevOps": 2.5,
            "HR": 1.5,
            "Finance": 1.6
        }

        education_bonus = {"Bachelor's": 0, "Master's": 1, "PhD": 2}
        location_bonus = {"Bangalore": 1, "Hyderabad": 0.8, "Mumbai": 0.6, "Delhi": 0.5, "Chennai": 0.7, "Other": 0.3}
        industry_bonus = {"IT": 1.0, "Finance": 0.8, "Healthcare": 0.6, "Manufacturing": 0.5, "Other": 0.3}

        skill_score = len(skills) * 0.3

        predicted_salary = base_salary + role_factor[role] + education_bonus[education] + \
                           location_bonus[location] + industry_bonus[industry] + \
                           (experience_years * 0.25) + skill_score

        st.success(f"💰 Estimated Annual Salary: ₹{predicted_salary:.2f} LPA")
