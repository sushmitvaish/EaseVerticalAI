"""
Research Agent
Discovers potential customer and partner companies using search and LLM
"""
import logging
from pathlib import Path
from typing import List, Dict, Any

from utils.llm_client import llm_client
from utils.search_client import search_client
from utils.document_processor import doc_processor

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Agent that discovers companies through intelligent search
    Generates search queries and extracts company names from results
    """

    def __init__(self):
        self.customer_prompt = self._load_prompt("prompts/customer_discovery.txt")
        self.partner_prompt = self._load_prompt("prompts/partner_discovery.txt")
        self.extraction_prompt = self._load_prompt("prompts/company_extraction.txt")
        logger.info("Research Agent initialized")

    def _load_prompt(self, path: str) -> str:
        """Load prompt template from file"""
        prompt_file = Path(path)
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()
        else:
            logger.warning(f"Prompt file not found: {path}")
            return ""

    def discover_customers(self, max_companies: int = 30) -> List[str]:
        """
        Discover potential customer companies

        Args:
            max_companies: Maximum number of companies to discover

        Returns:
            List of company names
        """
        logger.info("Discovering potential customers...")

        # Get company profile
        company_profile = doc_processor.get_customer_profile()

        # Generate search queries using LLM
        queries = self._generate_search_queries(company_profile, "customer")

        # Execute searches
        companies = self._search_and_extract_companies(queries, max_companies)

        logger.info(f"Discovered {len(companies)} potential customers")
        return companies

    def discover_partners(self, max_companies: int = 30) -> List[str]:
        """
        Discover potential partner companies

        Args:
            max_companies: Maximum number of companies to discover

        Returns:
            List of company names
        """
        logger.info("Discovering potential partners...")

        # Get company profile
        company_profile = doc_processor.get_partner_profile()

        # Generate search queries using LLM
        queries = self._generate_search_queries(company_profile, "partner")

        # Execute searches
        companies = self._search_and_extract_companies(queries, max_companies)

        logger.info(f"Discovered {len(companies)} potential partners")
        return companies

    def _generate_search_queries(
        self, company_profile: str, discovery_type: str
    ) -> List[str]:
        """
        Use LLM to generate targeted search queries

        Args:
            company_profile: Profile of the target company
            discovery_type: "customer" or "partner"

        Returns:
            List of search queries
        """
        logger.info(f"Generating {discovery_type} search queries...")

        # Select appropriate prompt
        if discovery_type == "customer":
            prompt_template = self.customer_prompt
        else:
            prompt_template = self.partner_prompt

        # Format prompt
        prompt = prompt_template.format(company_profile=company_profile)

        try:
            # Get LLM response
            response = llm_client.generate_json(
                prompt=prompt,
                system_prompt="You are a B2B market research expert. Generate targeted search queries.",
            )

            queries = response.get("queries", [])
            strategy = response.get("strategy", "No strategy provided")

            logger.info(f"Generated {len(queries)} search queries")
            logger.info(f"Search strategy: {strategy}")

            return queries

        except Exception as e:
            logger.error(f"Failed to generate search queries: {e}")
            # Return fallback queries
            return self._get_fallback_queries(discovery_type)

    def _get_fallback_queries(self, discovery_type: str) -> List[str]:
        """Fallback search queries if LLM generation fails"""
        if discovery_type == "customer":
            return [
                "largest automotive dealership groups United States",
                "top car dealer groups by revenue",
                "multi-location franchise car dealerships",
                "automotive retail chains North America",
            ]
        else:  # partner
            return [
                "automotive payment processing API",
                "VIN data provider APIs",
                "vehicle valuation services API",
                "dealership software integration partners",
            ]

    def _search_and_extract_companies(
        self, queries: List[str], max_companies: int
    ) -> List[str]:
        """
        Execute searches and extract company names

        Args:
            queries: List of search queries
            max_companies: Maximum companies to extract

        Returns:
            List of unique company names
        """
        all_companies = set()

        for query in queries:
            try:
                # Search
                logger.info(f"Executing search: {query}")
                search_results = search_client.search(query, max_results=10)

                # Format results for LLM
                results_text = self._format_search_results(search_results)

                # Extract companies using LLM
                companies = self._extract_companies(results_text)

                # Add to set (deduplication)
                all_companies.update(companies)

                logger.info(f"Extracted {len(companies)} companies from this search")

                # Check if we have enough
                if len(all_companies) >= max_companies:
                    break

            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
                continue

        # Convert to list and limit
        companies_list = list(all_companies)[:max_companies]
        logger.info(f"Total unique companies extracted: {len(companies_list)}")

        return companies_list

    def _format_search_results(self, search_results: List) -> str:
        """Format search results for LLM processing"""
        formatted = []
        for i, result in enumerate(search_results, 1):
            formatted.append(
                f"Result {i}:\nTitle: {result.title}\nSnippet: {result.snippet}\nURL: {result.url}\n"
            )
        return "\n".join(formatted)

    def _extract_companies(self, search_results_text: str) -> List[str]:
        """
        Extract company names from search results using LLM

        Args:
            search_results_text: Formatted search results

        Returns:
            List of company names
        """
        # Format prompt
        prompt = self.extraction_prompt.format(search_results=search_results_text)

        try:
            # Get LLM response
            response = llm_client.generate_json(
                prompt=prompt,
                system_prompt="You are a data extraction expert. Extract company names from text.",
            )

            companies = response.get("companies", [])
            logger.debug(f"Extracted companies: {companies}")

            return companies

        except Exception as e:
            logger.error(f"Company extraction failed: {e}")
            return []


# Global instance
research_agent = ResearchAgent()
