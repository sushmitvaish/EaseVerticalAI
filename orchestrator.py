"""
Orchestrator - Main agent coordinator
Coordinates all agents to complete the company discovery workflow
"""
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from agents.intent_classifier import intent_classifier
from agents.research_agent import research_agent
from agents.enrichment_agent import enrichment_agent
from agents.scoring_agent import scoring_agent
from config.settings import settings

logger = logging.getLogger(__name__)


class LeadGeneratorOrchestrator:
    """
    Main orchestrator that coordinates all agents
    Workflow:
    1. Classify user intent
    2. Discover companies (Research Agent)
    3. Enrich companies (Enrichment Agent)
    4. Score and rank companies (Scoring Agent)
    5. Return top N results
    """

    def __init__(self):
        self.max_companies_to_analyze = settings.max_companies_to_analyze
        self.top_n_results = settings.top_n_results
        self.cache_dir = Path("data/results_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Lead Generator Orchestrator initialized")

    def generate_leads(
        self,
        user_input: str,
        discovery_type: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Main entry point - generate leads based on user input

        Args:
            user_input: Natural language input from user
            discovery_type: Override automatic classification ("customer", "partner", or "both")
            use_cache: Whether to use cached results

        Returns:
            Dictionary with discovered companies
        """
        logger.info("=" * 80)
        logger.info("Starting lead generation workflow")
        logger.info(f"User input: {user_input}")
        logger.info("=" * 80)

        # Step 1: Classify intent (if not overridden)
        if discovery_type:
            intent = discovery_type
            logger.info(f"Using provided discovery type: {intent}")
        else:
            intent_result = intent_classifier.classify(user_input)
            intent = intent_result["intent"]
            logger.info(f"Classified intent: {intent} (confidence: {intent_result['confidence']})")

            if intent == "unclear":
                return {
                    "status": "error",
                    "message": "Could not determine if you want customers or partners. Please clarify.",
                    "intent_result": intent_result
                }

        # Step 2: Execute discovery based on intent
        results = {}

        if intent in ["customer", "both"]:
            logger.info("\n--- Discovering Customers ---")
            customers = self._discover_and_score("customer")
            results["customers"] = customers

        if intent in ["partner", "both"]:
            logger.info("\n--- Discovering Partners ---")
            partners = self._discover_and_score("partner")
            results["partners"] = partners

        # Cache results
        if settings.cache_results:
            self._cache_results(results, intent)

        logger.info("=" * 80)
        logger.info("Lead generation workflow completed")
        logger.info("=" * 80)

        return {
            "status": "success",
            "intent": intent,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }

    def _discover_and_score(self, discovery_type: str) -> List[Dict[str, Any]]:
        """
        Complete discovery and scoring workflow for one type

        Args:
            discovery_type: "customer" or "partner"

        Returns:
            List of top N scored companies
        """
        # Step 1: Research - Discover companies
        logger.info(f"Step 1: Discovering {discovery_type}s...")

        if discovery_type == "customer":
            company_names = research_agent.discover_customers(
                max_companies=self.max_companies_to_analyze
            )
        else:
            company_names = research_agent.discover_partners(
                max_companies=self.max_companies_to_analyze
            )

        if not company_names:
            logger.warning(f"No {discovery_type}s discovered")
            return []

        logger.info(f"Discovered {len(company_names)} {discovery_type}s")

        # Step 2: Enrichment - Get detailed information
        logger.info(f"Step 2: Enriching {discovery_type} information...")
        enriched_companies = enrichment_agent.enrich_companies_batch(company_names)

        if not enriched_companies:
            logger.warning(f"No {discovery_type}s enriched")
            return []

        logger.info(f"Enriched {len(enriched_companies)} {discovery_type}s")

        # Step 3: Scoring - Score and rank companies
        logger.info(f"Step 3: Scoring and ranking {discovery_type}s...")
        top_companies = scoring_agent.score_and_rank(
            companies=enriched_companies,
            discovery_type=discovery_type,
            top_n=self.top_n_results
        )

        logger.info(f"Selected top {len(top_companies)} {discovery_type}s")

        # Note: Filtering and deduplication already done during extraction (research_agent)
        # No post-processing needed - results are clean!

        return top_companies

    def _cache_results(self, results: Dict[str, Any], intent: str):
        """Cache results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_file = self.cache_dir / f"{intent}_{timestamp}.json"

        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results cached to {cache_file}")

    def format_results_for_display(self, results: Dict[str, Any]) -> str:
        """
        Format results in a human-readable way

        Args:
            results: Results dictionary from generate_leads()

        Returns:
            Formatted string
        """
        if results.get("status") == "error":
            return f"Error: {results.get('message')}"

        output = []
        output.append("=" * 80)
        output.append("LEAD GENERATION RESULTS")
        output.append("=" * 80)
        output.append(f"Intent: {results.get('intent')}")
        output.append(f"Timestamp: {results.get('timestamp')}")
        output.append("")

        result_data = results.get("results", {})

        # Format customers
        if "customers" in result_data:
            output.append("\n" + "=" * 80)
            output.append("TOP 10 POTENTIAL CUSTOMERS")
            output.append("=" * 80)
            for i, company in enumerate(result_data["customers"], 1):
                output.append(f"\n{i}. {company['company_name']}")
                output.append(f"   Website: {company['website']}")
                output.append(f"   Headquarters: {company['headquarters']}")
                output.append(f"   Size: {company['size']}")
                output.append(f"   Fit Score: {company['fit_score']}/10")
                output.append(f"   Rationale: {company['rationale']}")

        # Format partners
        if "partners" in result_data:
            output.append("\n" + "=" * 80)
            output.append("TOP 10 POTENTIAL PARTNERS")
            output.append("=" * 80)
            for i, company in enumerate(result_data["partners"], 1):
                output.append(f"\n{i}. {company['company_name']}")
                output.append(f"   Website: {company['website']}")
                output.append(f"   Headquarters: {company['headquarters']}")
                output.append(f"   Size: {company['size']}")
                output.append(f"   Fit Score: {company['fit_score']}/10")
                output.append(f"   Rationale: {company['rationale']}")
                if "integration_type" in company:
                    output.append(f"   Integration Type: {company['integration_type']}")

        output.append("\n" + "=" * 80)

        return "\n".join(output)


# Global orchestrator instance
orchestrator = LeadGeneratorOrchestrator()
