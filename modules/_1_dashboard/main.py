import streamlit as st
import pandas as pd

from modules._1_dashboard.utils import get_case_studies_stats

def display_content_page():

    # Title and description
    st.title("AI Case Study Library")
    st.markdown("""
    This dashboard provides an overview of the AI Case Study Library.
    """)

    # Fetch data
    try:
        
        stats = get_case_studies_stats()
        
        # Display total count
        st.metric(
            label="Total Case Studies",
            value=stats["total_case_studies"],
            help="Total number of case studies in the database"
        )
        
        # Company Distribution
        st.subheader("Case Studies by Company")
        company_data = stats["company_distribution"]
        if company_data:
            company_df = pd.DataFrame({
                'Company': company_data.keys(),
                'Count': company_data.values()
            }).sort_values('Count', ascending=False)
            
            st.dataframe(
                company_df,
                hide_index=True,
                column_config={
                    "Company": st.column_config.LinkColumn(
                        "Company",
                        help="Click to visit company website",
                        validate="^https?://.*",  # Validate URLs
                    )
                }
            )
        else:
            st.info("No company data available")

        # Sector Distribution
        st.subheader("Case Studies by Sector")
        sector_data = stats["sector_distribution"]
        if sector_data:
            sector_df = pd.DataFrame({
                'Sector': sector_data.keys(),
                'Count': sector_data.values()
            }).sort_values('Count', ascending=False)
            st.dataframe(sector_df, hide_index=True)
        else:
            st.info("No sector data available")

        # Industry Distribution
        st.subheader("Case Studies by Industry")
        industry_data = stats["industry_distribution"]
        if industry_data:
            industry_df = pd.DataFrame({
                'Industry': industry_data.keys(),
                'Count': industry_data.values()
            }).sort_values('Count', ascending=False)
            st.dataframe(industry_df, hide_index=True)
        else:
            st.info("No industry data available")
        
        # Business Function Distribution
        st.subheader("Case Studies by Business Function")
        function_data = stats["business_functions"]
        if function_data:
            function_df = pd.DataFrame({
                'Business Function': function_data.keys(),
                'Count': function_data.values()
            }).sort_values('Count', ascending=False)
            st.dataframe(function_df, hide_index=True)
        else:
            st.info("No business function data available")
        
        # Business Impact Distribution
        st.subheader("Case Studies by Business Impact")
        impact_data = stats["business_impacts"]
        if impact_data:
            impact_df = pd.DataFrame({
                'Business Impact': impact_data.keys(),
                'Count': impact_data.values()
            }).sort_values('Count', ascending=False)
            st.dataframe(impact_df, hide_index=True)
        else:
            st.info("No business impact data available")

        # Maturity Model Distribution
        st.subheader("Case Studies by Maturity Model")
        maturity_data = stats["maturity_models"]
        if maturity_data:
            maturity_df = pd.DataFrame({
                'Maturity Model': maturity_data.keys(),
                'Count': maturity_data.values()
            }).sort_values('Count', ascending=False)
            st.dataframe(maturity_df, hide_index=True)
        else:
            st.info("No maturity model data available")

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}") 