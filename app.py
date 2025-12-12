"""
Streamlit UI for DealerFlow Lead Generator
Natural language interface for discovering customers and partners
"""
import streamlit as st
import logging
import sys
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lead_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import orchestrator
from orchestrator import orchestrator
from utils.document_processor import doc_processor

# Page config
st.set_page_config(
    page_title="DealerFlow Lead Generator",
    page_icon="🚗",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False


def main():
    """Main application"""

    # Header
    st.title("🚗 DealerFlow Cloud - Lead Generator")
    st.markdown("### AI-Powered Customer & Partner Discovery")

    st.markdown("""
    This tool uses open-source LLMs (Llama/Mistral) and web search to discover:
    - **Potential Customers**: Automotive dealerships that could benefit from DealerFlow Cloud
    - **Potential Partners**: Technology companies that could integrate with DealerFlow Cloud
    """)

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.subheader("Company Context")
        company_context = doc_processor.load_context()
        st.info(f"**Product**: {company_context['product_name']}\n\n**Industry**: {company_context['industry']}")

        st.subheader("Settings")
        discovery_mode = st.selectbox(
            "Discovery Mode",
            ["Auto-detect", "Customers Only", "Partners Only", "Both"],
            help="Auto-detect uses AI to understand your intent"
        )

        st.subheader("About")
        st.markdown("""
        **Technology Stack:**
        - LLM: Llama 3.1 / Mistral 7B
        - Search: DuckDuckGo (free)
        - Framework: LangChain
        - UI: Streamlit

        **Data Sources:**
        - Web search results
        - Public company information
        - No LinkedIn scraping
        """)

    # Main interface
    st.header("🎯 Discover Leads")

    # Input method selection
    input_tab1, input_tab2 = st.tabs(["Natural Language", "Predefined Queries"])

    with input_tab1:
        st.markdown("**Describe what you want to find in natural language:**")

        user_input = st.text_area(
            "Your Request",
            placeholder="Examples:\n- Find me potential customers for our dealership management system\n- Who could we partner with to enhance our platform?\n- Generate both customer and partner lists",
            height=100
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            generate_button = st.button("🚀 Generate Leads", type="primary", use_container_width=True)

    with input_tab2:
        st.markdown("**Or choose a predefined query:**")

        predefined_queries = {
            "Top 10 Potential Customers": "Find me the top 10 automotive dealerships that would benefit from DealerFlow Cloud",
            "Top 10 Technology Partners": "Discover technology companies that could integrate with our dealership management platform",
            "Both Customers and Partners": "Generate comprehensive lists of both potential customers and integration partners"
        }

        selected_query = st.selectbox("Select a query", list(predefined_queries.keys()))

        if st.button("🚀 Run Predefined Query", use_container_width=True):
            user_input = predefined_queries[selected_query]
            generate_button = True
        else:
            generate_button = False

    # Process request
    if generate_button and user_input:
        st.session_state.processing = True

        # Map discovery mode
        discovery_type_map = {
            "Auto-detect": None,
            "Customers Only": "customer",
            "Partners Only": "partner",
            "Both": "both"
        }
        discovery_type = discovery_type_map[discovery_mode]

        # Show progress
        with st.spinner("🤖 AI agents are working... This may take 2-5 minutes..."):
            progress_container = st.container()

            with progress_container:
                st.info("**Workflow Progress:**")
                progress_steps = st.empty()

                # Update progress
                progress_steps.markdown("""
                - ✅ Classifying intent...
                - ⏳ Discovering companies via web search...
                - ⏳ Enriching company information...
                - ⏳ Scoring and ranking results...
                """)

                try:
                    # Run orchestrator
                    results = orchestrator.generate_leads(
                        user_input=user_input,
                        discovery_type=discovery_type
                    )

                    progress_steps.markdown("""
                    - ✅ Classifying intent...
                    - ✅ Discovering companies via web search...
                    - ✅ Enriching company information...
                    - ✅ Scoring and ranking results...
                    """)

                    st.session_state.results = results
                    st.session_state.processing = False

                    st.success("✅ Lead generation completed!")

                except Exception as e:
                    logger.error(f"Lead generation failed: {e}", exc_info=True)
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.session_state.processing = False
                    return

    # Display results
    if st.session_state.results:
        results = st.session_state.results

        if results.get("status") == "error":
            st.error(results.get("message"))
        else:
            st.success(f"**Intent detected**: {results.get('intent').upper()}")

            result_data = results.get("results", {})

            # Display customers
            if "customers" in result_data:
                st.header("🎯 Top 10 Potential Customers")

                customers = result_data["customers"]

                for i, company in enumerate(customers, 1):
                    with st.expander(f"#{i} - {company['company_name']} (Score: {company['fit_score']}/10)"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Website**: {company['website']}")
                            st.markdown(f"**Headquarters**: {company['headquarters']}")
                            st.markdown(f"**Size**: {company['size']}")

                        with col2:
                            st.markdown(f"**Fit Score**: {company['fit_score']}/10")
                            st.markdown(f"**Recommended**: {'✅ Yes' if company['recommended'] else '❌ No'}")

                        st.markdown(f"**Rationale**: {company['rationale']}")

                        if company.get('key_strengths'):
                            st.markdown("**Key Strengths**:")
                            for strength in company['key_strengths']:
                                st.markdown(f"- {strength}")

                # Download as JSON
                st.download_button(
                    label="📥 Download Customer List (JSON)",
                    data=json.dumps(customers, indent=2),
                    file_name="potential_customers.json",
                    mime="application/json"
                )

            # Display partners
            if "partners" in result_data:
                st.header("🤝 Top 10 Potential Partners")

                partners = result_data["partners"]

                for i, company in enumerate(partners, 1):
                    with st.expander(f"#{i} - {company['company_name']} (Score: {company['fit_score']}/10)"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Website**: {company['website']}")
                            st.markdown(f"**Headquarters**: {company['headquarters']}")
                            st.markdown(f"**Size**: {company['size']}")

                        with col2:
                            st.markdown(f"**Fit Score**: {company['fit_score']}/10")
                            st.markdown(f"**Recommended**: {'✅ Yes' if company['recommended'] else '❌ No'}")
                            if company.get('integration_type'):
                                st.markdown(f"**Integration Type**: {company['integration_type']}")

                        st.markdown(f"**Rationale**: {company['rationale']}")

                        if company.get('value_proposition'):
                            st.markdown(f"**Value Proposition**: {company['value_proposition']}")

                # Download as JSON
                st.download_button(
                    label="📥 Download Partner List (JSON)",
                    data=json.dumps(partners, indent=2),
                    file_name="potential_partners.json",
                    mime="application/json"
                )


if __name__ == "__main__":
    main()
