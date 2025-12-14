"""
Tavily AI Search client for intelligent web search
"""
import logging
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from tavily import TavilyClient

from config.settings import settings

logger = logging.getLogger(__name__)


class SearchResult:
    """Structured search result"""

    def __init__(self, title: str, url: str, snippet: str, **kwargs):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            **self.extra,
        }

    def __repr__(self):
        return f"SearchResult(title={self.title}, url={self.url})"


class SearchClient:
    """
    Tavily AI Search client for intelligent web search

    Tavily provides AI-optimized search results specifically designed for
    LLM applications, with better quality and relevance than traditional search APIs.
    """

    def __init__(self):
        """Initialize Tavily search client"""
        if not settings.tavily_api_key:
            raise ValueError(
                "TAVILY_API_KEY not set. Get your free API key at https://tavily.com"
            )

        self.client = TavilyClient(api_key=settings.tavily_api_key)
        logger.info("Tavily search client initialized")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "basic",
    ) -> List[SearchResult]:
        """
        Perform AI-optimized web search using Tavily

        Args:
            query: Search query
            max_results: Maximum number of results to return (default: 10)
            search_depth: "basic" for faster results, "advanced" for deeper research

        Returns:
            List of SearchResult objects

        Raises:
            Exception: If search fails after retries
        """
        logger.info(f"Searching Tavily: {query}")

        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=False,  # We don't need AI-generated answers
            )

            results = []
            for item in response.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        score=item.get("score", 0),
                    )
                )

            logger.info(f"Tavily returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise

    def search_company_info(self, company_name: str) -> List[SearchResult]:
        """
        Specialized search for company information

        Args:
            company_name: Name of the company

        Returns:
            Search results about the company's website, headquarters, and location
        """
        query = f"{company_name} company headquarters website location"
        return self.search(query, max_results=5)

    def batch_search(
        self, queries: List[str], max_results: int = 10
    ) -> Dict[str, List[SearchResult]]:
        """
        Execute multiple searches in batch

        Args:
            queries: List of search queries
            max_results: Results per query

        Returns:
            Dictionary mapping query to results
        """
        results = {}
        for query in queries:
            try:
                results[query] = self.search(query, max_results)
            except Exception as e:
                logger.error(f"Batch search failed for query '{query}': {e}")
                results[query] = []

        return results


# Global search client instance
search_client = SearchClient()
