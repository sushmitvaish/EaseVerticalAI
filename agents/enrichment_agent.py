"""
Enrichment Agent
Gathers detailed information about companies (website, location, size, etc.)
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from utils.llm_client import llm_client
from utils.search_client import search_client

logger = logging.getLogger(__name__)


class CompanyInfo:
    """Structured company information"""

    def __init__(self, data: Dict[str, Any]):
        self.company_name = data.get("company_name", "unknown")
        self.website = data.get("website", "unknown")
        self.headquarters = data.get("headquarters", "unknown")
        self.locations = data.get("locations", [])
        self.size = data.get("size", "unknown")
        self.size_reasoning = data.get("size_reasoning", "")
        self.description = data.get("description", "")
        self.confidence = data.get("confidence", 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "website": self.website,
            "headquarters": self.headquarters,
            "locations": self.locations,
            "size": self.size,
            "size_reasoning": self.size_reasoning,
            "description": self.description,
            "confidence": self.confidence,
        }

    def __repr__(self):
        return f"CompanyInfo({self.company_name}, {self.website}, {self.size})"


class EnrichmentAgent:
    """
    Agent that enriches company information
    Searches for company details and extracts structured data
    """

    def __init__(self):
        self.enrichment_prompt = self._load_prompt("prompts/company_enrichment.txt")
        logger.info("Enrichment Agent initialized")

    def _load_prompt(self, path: str) -> str:
        """Load prompt template from file"""
        prompt_file = Path(path)
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()
        else:
            logger.warning(f"Prompt file not found: {path}")
            return ""

    def enrich_company(self, company_name: str) -> Optional[CompanyInfo]:
        """
        Enrich a single company with detailed information

        Args:
            company_name: Name of the company to enrich

        Returns:
            CompanyInfo object or None if enrichment fails
        """
        logger.info(f"Enriching company: {company_name}")

        try:
            # Search for company information
            search_results = search_client.search_company_info(company_name)

            if not search_results:
                logger.warning(f"No search results for {company_name}")
                return self._create_minimal_info(company_name)

            # Format search results for LLM
            results_text = self._format_search_results(search_results)

            # Extract structured information using LLM
            company_info = self._extract_company_info(company_name, results_text)

            logger.info(f"Enriched {company_name}: {company_info.website}, {company_info.size}")
            return company_info

        except Exception as e:
            logger.error(f"Enrichment failed for {company_name}: {e}")
            return self._create_minimal_info(company_name)

    def enrich_companies_batch(self, company_names: List[str]) -> Dict[str, CompanyInfo]:
        """
        Enrich multiple companies

        Args:
            company_names: List of company names

        Returns:
            Dictionary mapping company name to CompanyInfo
        """
        logger.info(f"Enriching {len(company_names)} companies...")

        enriched = {}
        for name in company_names:
            info = self.enrich_company(name)
            if info:
                enriched[name] = info

        logger.info(f"Successfully enriched {len(enriched)} companies")
        return enriched

    def _format_search_results(self, search_results: List) -> str:
        """Format search results for LLM processing"""
        formatted = []
        for i, result in enumerate(search_results, 1):
            formatted.append(
                f"Result {i}:\nTitle: {result.title}\nSnippet: {result.snippet}\nURL: {result.url}\n"
            )
        return "\n".join(formatted)

    def _extract_company_info(
        self, company_name: str, search_results_text: str
    ) -> CompanyInfo:
        """
        Extract structured company information using LLM

        Args:
            company_name: Company name
            search_results_text: Formatted search results

        Returns:
            CompanyInfo object
        """
        # Format prompt
        prompt = self.enrichment_prompt.format(
            company_name=company_name, search_results=search_results_text
        )

        try:
            # Get LLM response
            response = llm_client.generate_json(
                prompt=prompt,
                system_prompt="You are a business intelligence analyst. Extract structured company information.",
            )

            # Create CompanyInfo object
            company_info = CompanyInfo(response)
            return company_info

        except Exception as e:
            logger.error(f"Failed to extract company info: {e}")
            return self._create_minimal_info(company_name)

    def _create_minimal_info(self, company_name: str) -> CompanyInfo:
        """Create minimal company info when enrichment fails"""
        return CompanyInfo({
            "company_name": company_name,
            "website": "unknown",
            "headquarters": "unknown",
            "locations": [],
            "size": "unknown",
            "size_reasoning": "Unable to determine from search results",
            "description": "Information not available",
            "confidence": 0.0,
        })


# Global instance
enrichment_agent = EnrichmentAgent()
