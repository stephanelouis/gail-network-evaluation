import streamlit as st

from utils.firestore_manager import get_db
from utils.helpers import load_company_urls

def display_content_page():
    
    # Title and description
    st.title("View Case Studies")
    st.markdown("""
    Search and view case studies by their source URL.
    """)

    # Load URLs from file
    urls = load_company_urls()
    if not urls:
        st.error("No company URLs available. Please check the configuration file.")
        return

    # URL input and search button in a form
    with st.form("search_form", clear_on_submit=False):
        url = st.selectbox(
            "Select company URL:",
            options=urls,
            key="url_select"
        )
        search_button = st.form_submit_button("Search", type="primary", use_container_width=True)
    
    if search_button and url:
        try:
            
            # Get Firestore client
            db = get_db()
            if db is None:
                st.error("Failed to connect to the database. Please check your Firebase configuration.")
                return
            
            # Set collecton ref for the query
            try:
                case_studies_ref = db.collection('case_studies_v3')
                if case_studies_ref is None:
                    st.error("Failed to access the case_studies_v3 collection.")
                    return
            except Exception as e:
                st.error(f"Error accessing collection: {str(e)}")
                return

            # Set query to fetch case studies where source_url starts with the input URL
            try:
                query = case_studies_ref.where('source_url', '>=', url)\
                                      .where('source_url', '<=', url + '\uf8ff')
                if query is None:
                    st.error("Failed to create query.")
                    return
            except Exception as e:
                st.error(f"Error creating query: {str(e)}")
                return
            
            # Fetch the documents
            try:
                docs = query.get()
            except Exception as e:
                st.error(f"Error fetching documents: {str(e)}")
                return
            
            if docs:
                # Convert to list of dictionaries
                case_studies = []
                for doc in docs:
                    try:
                        data = doc.to_dict() if doc else {}
                        if data:  # Only add if we have data
                            data['id'] = doc.id
                            case_studies.append(data)
                    except Exception as e:
                        st.warning(f"Skipped a case study due to error: {str(e)}")
                
                if case_studies:  # Only proceed if we have valid case studies
                    st.success(f"Found {len(case_studies)} case studies")
                    
                    # Display case study details in expanders
                    for case_study in case_studies:

                        # Safe get for source_url and updated_at
                        source_url = case_study.get('source_url', 'No URL available')
                        updated_at = case_study.get('updated_at', 'N/A')
                        
                        with st.expander(f"📄 {source_url} (Last updated: {updated_at})"):
                            
                            # Display case study final if available
                            case_study_final = case_study.get('case_study_final')
                            if case_study_final:
                                st.markdown("### Final Case Study")
                                st.markdown(case_study_final)
                            else:
                                st.info("No final case study available")
                            
                            st.markdown("### Additional Details")
                            # Display ID and created_at safely
                            st.text(f"ID: {case_study.get('id', 'N/A')}")
                            st.text(f"Created at: {case_study.get('created_at', 'N/A')}")
                            
                            # Display classification separately and safely
                            classification = case_study.get('case_study_classification')
                            if classification:
                                st.markdown("#### Classification")
                                if isinstance(classification, dict):
                                    for key, value in classification.items():
                                        if value is not None:  # Only display if value exists
                                            st.text(f"{key}: {value}")
                                else:
                                    st.text(f"Classification: {classification}")
                            else:
                                st.info("No classification available")
                else:
                    st.warning("No valid case studies found")
            else:
                st.info("No case studies found with this URL")
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.error("Please check your Firebase configuration and ensure you have access to the database.")
            
    elif search_button:
        st.warning("Please select a URL to search for case studies")