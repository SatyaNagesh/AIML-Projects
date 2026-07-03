import logging

from tavily import AsyncTavilyClient

from src.agent.state import ResearchState
from src.config import settings
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)

RESEARCH_SYSTEM = (
    "You are a research agent. Given a topic, generate 3-5 specific search queries "
    "to comprehensively cover the subject. Return a JSON object: "
    '{"queries": ["query1", "query2", ...]}'
)


async def research_node(state: ResearchState) -> dict:
    llm = LLMClient()
    tavily = AsyncTavilyClient(api_key=settings.tavily_api_key)

    query_decision = await llm.generate_json(
        system=RESEARCH_SYSTEM,
        user=f"Generate search queries for the topic: {state.topic}",
    )
    queries = query_decision.get("queries", [state.topic])
    state.query = "; ".join(queries)

    search_results = []
    for q in queries[:5]:
        try:
            resp = await tavily.search(query=q, search_depth="advanced", max_results=5)
            results = resp.get("results", [])
            for r in results:
                search_results.append({
                    "query": q,
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0),
                })
            logger.info("Search for '%s' returned %d results", q, len(results))
        except Exception as e:
            logger.warning("Tavily search failed for '%s': %s", q, e)

    extracted = []
    for sr in search_results[:15]:
        extracted.append({
            "source_url": sr["url"],
            "title": sr["title"],
            "content": sr["content"],
            "relevance_score": sr.get("score", 0),
        })

    return {
        "search_results": search_results,
        "extracted_content": extracted,
    }
