"""
Document processor for AxleWave company documentation
Creates embeddings and context for the AI agents
"""
import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process AxleWave documentation and create searchable context"""

    def __init__(self, docs_dir: str = "AxelwaveTechnologies_DemoData"):
        self.docs_dir = Path(docs_dir)
        self.context_file = Path("data/axlewave_context/company_context.json")
        self.context_file.parent.mkdir(parents=True, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            text = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            return "\n".join(text)
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""

    def create_company_context(self) -> Dict[str, Any]:
        """
        Create structured context about AxleWave Technologies
        This will be used by agents to understand the company
        """

        # Manual extraction from the technical docs (since we have limited doc reading capabilities)
        context = {
            "company_name": "AxleWave Technologies",
            "product_name": "DealerFlow Cloud",
            "industry": "Automotive Dealership Management",
            "product_type": "Cloud-based Dealer Management System (DMS)",

            "product_description": """
            DealerFlow Cloud is a comprehensive cloud-based dealership management system
            designed for automotive dealerships. It provides end-to-end solutions for
            managing dealership operations including customer management, vehicle inventory,
            sales processes, service operations, and accounting.
            """,

            "key_features": [
                "Customer Relationship Management (CRM)",
                "Vehicle Inventory Management with VIN decoding",
                "Deal Desking and Contracting",
                "Service Repair Order (RO) Management",
                "General Ledger and Accounting",
                "API-first architecture with REST APIs",
                "OAuth2 and OIDC authentication",
                "Real-time webhooks for key events",
                "Multi-location support"
            ],

            "api_capabilities": [
                "Customer CRUD and search operations",
                "Vehicle management with VIN decode",
                "Deal management (desking, contracting)",
                "Repair Order lifecycle management",
                "Accounting and general ledger integration",
                "Webhook events for real-time updates"
            ],

            "target_customers": {
                "primary": [
                    "Automotive franchise dealerships",
                    "Multi-location dealer groups",
                    "Used car dealerships",
                    "Auto retail chains"
                ],
                "characteristics": [
                    "Need modern cloud-based DMS",
                    "Managing multiple locations",
                    "Want to replace legacy on-premise systems",
                    "Require integrated sales and service operations",
                    "Need API integrations with other systems"
                ]
            },

            "potential_partners": {
                "categories": [
                    "Payment Processing Companies",
                    "VIN Data Providers",
                    "Automotive Valuation Services (KBB, Black Book)",
                    "Credit Bureau & Financing Partners",
                    "Insurance Verification Services",
                    "Parts & Inventory Suppliers",
                    "CRM and Marketing Automation Platforms",
                    "Accounting Software Providers",
                    "Document Management Systems",
                    "Dealer Compliance & Regulatory Solutions"
                ],
                "integration_needs": [
                    "RESTful API compatibility",
                    "Webhook support",
                    "OAuth2/OIDC authentication",
                    "Real-time data synchronization"
                ]
            },

            "competitors": [
                "CDK Global",
                "Reynolds & Reynolds",
                "DealerSocket",
                "Dealertrack (Cox Automotive)",
                "Auto/Mate",
                "PBS Systems"
            ],

            "value_propositions": [
                "Cloud-native architecture (vs legacy on-premise)",
                "Modern API-first design",
                "Real-time data with webhooks",
                "Easier integrations with third-party services",
                "Lower total cost of ownership",
                "Automatic updates and maintenance",
                "Multi-location capabilities"
            ],

            "technical_stack": {
                "authentication": "OIDC, OAuth2, mTLS",
                "api_style": "RESTful",
                "data_formats": "JSON",
                "sdks": ["JavaScript/TypeScript", "Python"],
                "integration": "Webhooks, OpenAPI spec"
            }
        }

        return context

    def save_context(self) -> str:
        """Save company context to file"""
        context = self.create_company_context()

        with open(self.context_file, 'w') as f:
            json.dump(context, indent=2, fp=f)

        logger.info(f"Company context saved to {self.context_file}")
        return str(self.context_file)

    def load_context(self) -> Dict[str, Any]:
        """Load company context from file"""
        if not self.context_file.exists():
            logger.info("Context file doesn't exist, creating new one")
            self.save_context()

        with open(self.context_file, 'r') as f:
            context = json.load(f)

        logger.info("Company context loaded")
        return context

    def get_customer_profile(self) -> str:
        """Get a formatted string describing ideal customer profile"""
        context = self.load_context()

        profile = f"""
Company: {context['company_name']}
Product: {context['product_name']}

Product Description:
{context['product_description']}

Key Features:
{chr(10).join('- ' + feature for feature in context['key_features'])}

Ideal Customer Profile:
Type: {', '.join(context['target_customers']['primary'])}

Customer Characteristics:
{chr(10).join('- ' + char for char in context['target_customers']['characteristics'])}

Competitors to find lookalikes:
{', '.join(context['competitors'])}
        """

        return profile.strip()

    def get_partner_profile(self) -> str:
        """Get a formatted string describing ideal partner profile"""
        context = self.load_context()

        profile = f"""
Company: {context['company_name']}
Product: {context['product_name']}

Product Description:
{context['product_description']}

Partner Categories Needed:
{chr(10).join('- ' + cat for cat in context['potential_partners']['categories'])}

Integration Requirements:
{chr(10).join('- ' + req for req in context['potential_partners']['integration_needs'])}

Technical Capabilities:
{chr(10).join('- ' + cap for cap in context['api_capabilities'])}
        """

        return profile.strip()


# Global document processor instance
doc_processor = DocumentProcessor()
