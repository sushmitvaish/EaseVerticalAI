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
        Execute searches and extract company names with smart filtering

        Args:
            queries: List of search queries
            max_companies: Maximum companies to extract

        Returns:
            List of unique, filtered company names (no duplicates, no competitors)
        """
        all_companies = []  # Changed from set to list to preserve order
        seen_base_names = set()  # Track normalized names for fuzzy dedup

        for query in queries:
            try:
                # Search
                logger.info(f"Executing search: {query}")
                search_results = search_client.search(query, max_results=10)

                # Format results for LLM
                results_text = self._format_search_results(search_results)

                # Extract companies using LLM (already filters competitors via prompt)
                companies = self._extract_companies(results_text)

                # Smart filtering: competitors + fuzzy deduplication
                for company in companies:
                    # Apply comprehensive early filter
                    if self._should_include_company(company, seen_base_names):
                        all_companies.append(company)
                        # Track normalized name
                        base_name = self._normalize_company_name(company)
                        seen_base_names.add(base_name)

                logger.info(f"Added {len(companies)} companies from this search (after filtering)")

                # Check if we have enough
                if len(all_companies) >= max_companies:
                    break

            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
                continue

        # Limit to max
        companies_list = all_companies[:max_companies]
        logger.info(f"Total unique companies after smart filtering: {len(companies_list)}")

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
        (LLM prompt already includes competitor filtering instructions)

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

    def _normalize_company_name(self, name: str) -> str:
        """
        Normalize company name for fuzzy duplicate detection
        Extracts parent company identifier to catch subsidiaries

        Args:
            name: Company name

        Returns:
            Normalized parent company identifier
        """
        normalized = name.lower()

        # Remove common suffixes and domains
        suffixes = ['.com', '.net', '.io', '.org', '.co',
                   ' inc.', ' inc', ' llc', ' ltd', ' limited',
                   ' corporation', ' corp', ' corp.',
                   ' company', ' co.', ' group', ' holdings']

        for suffix in suffixes:
            normalized = normalized.replace(suffix, '')

        normalized = normalized.strip()

        # Extract parent company name (first significant word)
        # This catches: "AutoNation Honda Chandler" -> "autonation"
        #              "Lithia & Driveway" -> "lithia"
        #              "Penske Automotive Group" -> "penske"

        # Remove common connecting words
        connecting_words = [' and ', ' & ', ' the ', ' of ', ' at ']
        for word in connecting_words:
            normalized = normalized.replace(word, ' ')

        # Get first word as parent identifier
        words = normalized.split()
        if words:
            parent_name = words[0]
            # Filter out very short words (likely not company names)
            if len(parent_name) > 2:
                return parent_name

        return normalized

    def _should_include_company(self, company_name: str, seen_base_names: set) -> bool:
        """
        Comprehensive filter: Check if company should be included
        Combines competitor filtering + fuzzy duplicate detection

        Args:
            company_name: Company name to check
            seen_base_names: Set of already seen normalized names

        Returns:
            True if company should be included, False otherwise
        """
        # DMS competitors list
        dms_competitors = {
            'CDK Global', 'Reynolds and Reynolds', 'Reynolds & Reynolds',
            'DealerSocket', 'Dealertrack DMS', 'Auto/Mate', 'PBS Systems',
            'AutoMate', 'Quorum', 'Quorum Information Technologies',
            'DealerBuilt', 'Dominion', 'VinSolutions', 'Frazer',
            'Tekion', 'Autosoft DMS', 'Dealer-FX', 'ProMax'
        }

        # Check 1: Is it a DMS competitor?
        is_competitor = any(comp.lower() in company_name.lower() for comp in dms_competitors)
        if is_competitor:
            logger.info(f"Smart filter: Removing DMS competitor '{company_name}'")
            return False

        # Check 2: Is it a fuzzy duplicate?
        base_name = self._normalize_company_name(company_name)
        if base_name in seen_base_names:
            logger.info(f"Smart filter: Removing fuzzy duplicate '{company_name}' (base: {base_name})")
            return False

        # Passed all checks
        return True


# Global instance
research_agent = ResearchAgent()
