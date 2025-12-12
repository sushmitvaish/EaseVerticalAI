"""
Scoring & Validation Agent
Evaluates and scores companies for customer/partner fit
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

from utils.llm_client import llm_client
from utils.document_processor import doc_processor
from agents.enrichment_agent import CompanyInfo

logger = logging.getLogger(__name__)


@dataclass
class ScoringResult:
    """Result of company scoring"""
    company_name: str
    fit_score: float
    rationale: str
    recommended: bool
    extra_data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "fit_score": self.fit_score,
            "rationale": self.rationale,
            "recommended": self.recommended,
            **self.extra_data
        }


class ScoringAgent:
    """
    Agent that scores and validates companies
    Determines how good of a fit each company is
    """

    def __init__(self):
        self.customer_scoring_prompt = self._load_prompt("prompts/customer_scoring.txt")
        self.partner_scoring_prompt = self._load_prompt("prompts/partner_scoring.txt")
        logger.info("Scoring Agent initialized")

    def _load_prompt(self, path: str) -> str:
        """Load prompt template from file"""
        prompt_file = Path(path)
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()
        else:
            logger.warning(f"Prompt file not found: {path}")
            return ""

    def score_customer(self, company_info: CompanyInfo) -> ScoringResult:
        """
        Score a company as a potential customer

        Args:
            company_info: Company information

        Returns:
            ScoringResult
        """
        logger.info(f"Scoring customer: {company_info.company_name}")

        # Get company profile
        company_profile = doc_processor.get_customer_profile()

        # Format prompt
        prompt = self.customer_scoring_prompt.format(
            company_profile=company_profile,
            company_name=company_info.company_name,
            website=company_info.website,
            headquarters=company_info.headquarters,
            size=company_info.size,
            description=company_info.description,
        )

        try:
            # Get LLM response
            response = llm_client.generate_json(
                prompt=prompt,
                system_prompt="You are a B2B sales analyst. Evaluate customer fit.",
            )

            # Create ScoringResult
            result = ScoringResult(
                company_name=company_info.company_name,
                fit_score=response.get("fit_score", 0.0),
                rationale=response.get("rationale", ""),
                recommended=response.get("recommended", False),
                extra_data={
                    "key_strengths": response.get("key_strengths", []),
                    "potential_objections": response.get("potential_objections", []),
                }
            )

            logger.info(f"Customer score: {result.fit_score}/10 - {'Recommended' if result.recommended else 'Not recommended'}")
            return result

        except Exception as e:
            logger.error(f"Customer scoring failed: {e}")
            return self._create_default_score(company_info.company_name)

    def score_partner(self, company_info: CompanyInfo) -> ScoringResult:
        """
        Score a company as a potential partner

        Args:
            company_info: Company information

        Returns:
            ScoringResult
        """
        logger.info(f"Scoring partner: {company_info.company_name}")

        # Get company profile
        company_profile = doc_processor.get_partner_profile()

        # Format prompt
        prompt = self.partner_scoring_prompt.format(
            company_profile=company_profile,
            company_name=company_info.company_name,
            website=company_info.website,
            headquarters=company_info.headquarters,
            size=company_info.size,
            description=company_info.description,
        )

        try:
            # Get LLM response
            response = llm_client.generate_json(
                prompt=prompt,
                system_prompt="You are a partnership strategy analyst. Evaluate partner fit.",
            )

            # Create ScoringResult
            result = ScoringResult(
                company_name=company_info.company_name,
                fit_score=response.get("fit_score", 0.0),
                rationale=response.get("rationale", ""),
                recommended=response.get("recommended", False),
                extra_data={
                    "integration_type": response.get("integration_type", ""),
                    "value_proposition": response.get("value_proposition", ""),
                }
            )

            logger.info(f"Partner score: {result.fit_score}/10 - {'Recommended' if result.recommended else 'Not recommended'}")
            return result

        except Exception as e:
            logger.error(f"Partner scoring failed: {e}")
            return self._create_default_score(company_info.company_name)

    def score_and_rank(
        self,
        companies: Dict[str, CompanyInfo],
        discovery_type: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Score multiple companies and return top N

        Args:
            companies: Dictionary of company names to CompanyInfo
            discovery_type: "customer" or "partner"
            top_n: Number of top companies to return

        Returns:
            List of top N companies with scores and details
        """
        logger.info(f"Scoring and ranking {len(companies)} {discovery_type}s...")

        scored_companies = []

        for company_name, company_info in companies.items():
            try:
                # Score company
                if discovery_type == "customer":
                    score = self.score_customer(company_info)
                else:
                    score = self.score_partner(company_info)

                # Combine company info and score
                company_data = {
                    "company_name": company_info.company_name,
                    "website": company_info.website,
                    "headquarters": company_info.headquarters,
                    "locations": company_info.locations,
                    "size": company_info.size,
                    "fit_score": score.fit_score,
                    "rationale": score.rationale,
                    "recommended": score.recommended,
                    **score.extra_data
                }

                scored_companies.append(company_data)

            except Exception as e:
                logger.error(f"Failed to score {company_name}: {e}")
                continue

        # Sort by fit score (descending)
        scored_companies.sort(key=lambda x: x["fit_score"], reverse=True)

        # Return top N
        top_companies = scored_companies[:top_n]

        logger.info(f"Top {len(top_companies)} {discovery_type}s selected")
        return top_companies

    def _create_default_score(self, company_name: str) -> ScoringResult:
        """Create default score when scoring fails"""
        return ScoringResult(
            company_name=company_name,
            fit_score=0.0,
            rationale="Unable to score company due to error",
            recommended=False,
            extra_data={}
        )


# Global instance
scoring_agent = ScoringAgent()
