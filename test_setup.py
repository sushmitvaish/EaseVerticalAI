"""
Test script to verify setup and configuration
Run this after setup to ensure everything is working
"""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from config.settings import settings
        from utils.llm_client import llm_client
        from utils.search_client import search_client
        from utils.document_processor import doc_processor
        from agents.intent_classifier import intent_classifier
        from agents.research_agent import research_agent
        from agents.enrichment_agent import enrichment_agent
        from agents.scoring_agent import scoring_agent
        from orchestrator import orchestrator

        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_configuration():
    """Test configuration settings"""
    print("\nTesting configuration...")
    try:
        from config.settings import settings

        print(f"  LLM Provider: {settings.llm_provider}")
        print(f"  LLM Model: {settings.ollama_model if settings.llm_provider == 'ollama' else settings.huggingface_model}")
        print(f"  Search Provider: {settings.search_provider}")
        print(f"  Cache Results: {settings.cache_results}")

        print("✅ Configuration loaded")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_company_context():
    """Test that company context can be loaded"""
    print("\nTesting company context...")
    try:
        from utils.document_processor import doc_processor

        context = doc_processor.load_context()
        print(f"  Company: {context['company_name']}")
        print(f"  Product: {context['product_name']}")
        print(f"  Industry: {context['industry']}")

        print("✅ Company context loaded")
        return True
    except Exception as e:
        print(f"❌ Company context test failed: {e}")
        return False


def test_llm_connection():
    """Test LLM connection (if configured)"""
    print("\nTesting LLM connection...")
    try:
        from utils.llm_client import llm_client
        from config.settings import settings

        if settings.llm_provider == "ollama":
            print("  Testing Ollama connection...")
            try:
                response = llm_client.generate(
                    prompt="Say 'Hello' in one word.",
                    temperature=0.0,
                    max_tokens=10
                )
                print(f"  LLM Response: {response.strip()}")
                print("✅ LLM connection successful")
                return True
            except Exception as e:
                print(f"⚠️  Ollama connection failed: {e}")
                print("  Make sure Ollama is running: ollama serve")
                return False
        else:
            print("  Skipping LLM test (HuggingFace requires API token)")
            return True

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


def test_search():
    """Test search functionality"""
    print("\nTesting search...")
    try:
        from utils.search_client import search_client

        results = search_client.search("test query", max_results=1)
        print(f"  Found {len(results)} result(s)")

        if results:
            print(f"  Sample: {results[0].title[:50]}...")

        print("✅ Search working")
        return True
    except Exception as e:
        print(f"⚠️  Search test failed: {e}")
        print("  This is okay if you haven't configured a search API yet")
        return True  # Don't fail on search errors


def main():
    """Run all tests"""
    print("=" * 60)
    print("DealerFlow Lead Generator - Setup Verification")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_configuration()))
    results.append(("Company Context", test_company_context()))
    results.append(("LLM Connection", test_llm_connection()))
    results.append(("Search", test_search()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")

    all_passed = all(passed for _, passed in results)

    print("=" * 60)

    if all_passed:
        print("\n✅ All tests passed! You're ready to run the application.")
        print("\nTo start the app:")
        print("  streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("  - Ollama not running: ollama serve")
        print("  - Model not downloaded: ollama pull llama3.1:8b")
        print("  - .env file not configured")

    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
