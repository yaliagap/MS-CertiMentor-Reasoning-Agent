"""
Microsoft Learn MCP Tools
Tools for searching and retrieving Microsoft Learn content using MCP Server.
"""
from agent_framework import tool
from typing import List, Dict, Any
import asyncio
from .mcp_client import get_mcp_client


@tool
async def search_learning_paths(
    topics: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for Microsoft Learn learning paths related to certification topics.

    This tool connects to Microsoft Learn MCP Server to find relevant
    learning paths for Microsoft certification preparation.

    Args:
        topics: Certification topics to search (e.g., "Azure AI", "Power Platform")
        max_results: Maximum number of learning paths to return (default: 5)

    Returns:
        List of learning paths with:
        - title: Learning path title
        - url: Microsoft Learn URL
        - description: Brief description
        - duration_minutes: Estimated duration
        - modules: List of modules in the path

    Example:
        >>> paths = await search_learning_paths("Azure AI Fundamentals", max_results=3)
        >>> print(paths[0]["title"])
        "Get started with AI on Azure"
    """
    client = get_mcp_client()

    try:
        # Search for learning paths using MCP
        results = await client.search_docs(
            query=f"{topics} certification learning path",
            max_results=max_results,
            content_type="learning-path"
        )

        # Transform results to expected format
        # MCP returns: title, content, contentUrl, id
        learning_paths = []
        for result in results:
            path = {
                "title": result.get("title", ""),
                "url": result.get("contentUrl", result.get("url", "")),  # MCP uses contentUrl
                "description": result.get("content", result.get("description", ""))[:200],  # MCP uses content
                "duration_minutes": result.get("duration_minutes", 0),
                "modules": result.get("modules", []),
                "relevance_score": result.get("score", 0.0)
            }
            learning_paths.append(path)

        return learning_paths if learning_paths else await _get_fallback_learning_paths(topics, max_results)

    except Exception as e:
        print(f"[MCP Tool] search_learning_paths failed, using fallback: {e}")
        return await _get_fallback_learning_paths(topics, max_results)


@tool
async def search_certification_modules(
    topics: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for individual Microsoft Learn modules related to certification topics.

    Use this to find specific modules when you need more granular content
    than full learning paths.

    Args:
        topics: Certification topics to search
        max_results: Maximum number of modules to return (default: 10)

    Returns:
        List of modules with title, URL, description, and duration

    Example:
        >>> modules = await search_certification_modules("Azure Machine Learning")
        >>> print(f"Found {len(modules)} modules")
    """
    client = get_mcp_client()

    try:
        # Search for modules using MCP
        results = await client.search_docs(
            query=f"{topics} certification module",
            max_results=max_results,
            content_type="module"
        )

        # Transform results
        # MCP returns: title, content, contentUrl, id
        modules = []
        for result in results:
            module = {
                "title": result.get("title", ""),
                "url": result.get("contentUrl", result.get("url", "")),  # MCP uses contentUrl
                "description": result.get("content", result.get("description", ""))[:200],  # MCP uses content
                "duration_minutes": result.get("duration_minutes", 0),
                "level": result.get("level", "beginner")
            }
            modules.append(module)

        return modules

    except Exception as e:
        print(f"[MCP Tool] search_certification_modules failed: {e}")
        return []


@tool
async def get_certification_exams(
    certification_area: str
) -> List[Dict[str, Any]]:
    """
    Get information about Microsoft certification exams.

    Args:
        certification_area: Certification area (e.g., "Azure AI", "Azure Administrator")

    Returns:
        List of certification exams with:
        - exam_code: Exam code (e.g., "AI-900", "AZ-104")
        - title: Exam title
        - url: Registration URL
        - description: Exam description
        - level: Fundamentals, Associate, or Expert

    Example:
        >>> exams = await get_certification_exams("Azure AI")
        >>> print(exams[0]["exam_code"])
        "AI-900"
    """
    client = get_mcp_client()

    try:
        # Search for certification information using MCP
        results = await client.search_docs(
            query=f"{certification_area} certification exam",
            max_results=5,
            content_type="certification"
        )

        # Transform results
        # MCP returns: title, content, contentUrl, id
        # Extract exam code from title if available
        exams = []
        for result in results:
            title = result.get("title", "")
            # Try to extract exam code from title (e.g., "AI-900", "AZ-104")
            exam_code = ""
            import re
            match = re.search(r'([A-Z]{2}-\d{3,4})', title)
            if match:
                exam_code = match.group(1)

            exam = {
                "exam_code": exam_code,
                "title": title,
                "url": result.get("contentUrl", result.get("url", "")),  # MCP uses contentUrl
                "description": result.get("content", result.get("description", ""))[:200],  # MCP uses content
                "level": result.get("level", "fundamentals")
            }
            exams.append(exam)

        return exams if exams else await _get_fallback_certifications(certification_area)

    except Exception as e:
        print(f"[MCP Tool] get_certification_exams failed, using fallback: {e}")
        return await _get_fallback_certifications(certification_area)


@tool
async def fetch_learning_path_details(
    url: str
) -> Dict[str, Any]:
    """
    Fetch detailed information about a specific learning path.

    Use this after finding a learning path with search_learning_paths()
    to get complete details including all modules, prerequisites, etc.

    Args:
        url: Microsoft Learn URL of the learning path

    Returns:
        Detailed learning path information including:
        - title: Full title
        - description: Detailed description
        - modules: List of all modules with details
        - prerequisites: Required prerequisites
        - duration_minutes: Total duration
        - skills_gained: List of skills

    Example:
        >>> details = await fetch_learning_path_details(
        ...     "https://learn.microsoft.com/training/paths/azure-ai-fundamentals"
        ... )
        >>> print(details["duration_minutes"])
        480
    """
    client = get_mcp_client()

    try:
        # Fetch content details using MCP
        content = await client.fetch_content(url)

        return {
            "title": content.get("title", ""),
            "description": content.get("description", ""),
            "modules": content.get("modules", []),
            "prerequisites": content.get("prerequisites", []),
            "duration_minutes": content.get("duration_minutes", 0),
            "skills_gained": content.get("skills", []),
            "url": url
        }

    except Exception as e:
        print(f"[MCP Tool] fetch_learning_path_details failed: {e}")
        return {}


# Fallback functions (when MCP is unavailable)

async def _get_fallback_learning_paths(topics: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fallback data when MCP server is unavailable.
    Returns simulated but realistic Microsoft Learn paths.
    """
    print("[INFO] Using fallback data - MCP server unavailable or returned no results")

    # Simulated realistic Microsoft Learn data
    base_paths = [
        {
            "title": f"Get started with {topics}",
            "url": f"https://learn.microsoft.com/training/paths/get-started-{topics.lower().replace(' ', '-')}",
            "description": f"Learn the fundamentals of {topics} and how to apply them in real-world scenarios.",
            "duration_minutes": 300,
            "modules": ["Introduction", "Core Concepts", "Hands-on Labs"],
            "relevance_score": 0.95
        },
        {
            "title": f"Implement {topics} solutions",
            "url": f"https://learn.microsoft.com/training/paths/implement-{topics.lower().replace(' ', '-')}",
            "description": f"Build production-ready solutions using {topics} services and best practices.",
            "duration_minutes": 420,
            "modules": ["Architecture", "Implementation", "Deployment"],
            "relevance_score": 0.88
        },
        {
            "title": f"Advanced {topics} techniques",
            "url": f"https://learn.microsoft.com/training/paths/advanced-{topics.lower().replace(' ', '-')}",
            "description": f"Master advanced {topics} concepts and optimization strategies.",
            "duration_minutes": 360,
            "modules": ["Advanced Topics", "Performance", "Security"],
            "relevance_score": 0.82
        }
    ]

    return base_paths[:max_results]


async def _get_fallback_certifications(certification_area: str) -> List[Dict[str, Any]]:
    """
    Fallback certification data when MCP is unavailable.
    """
    print("[INFO] Using fallback certification data")

    cert_mapping = {
        "azure ai": {
            "exam_code": "AI-900",
            "title": "Microsoft Azure AI Fundamentals",
            "description": "Demonstrates foundational knowledge of machine learning and AI concepts",
            "url": "https://learn.microsoft.com/certifications/exams/ai-900",
            "level": "fundamentals"
        },
        "azure": {
            "exam_code": "AZ-900",
            "title": "Microsoft Azure Fundamentals",
            "description": "Validates foundational knowledge of cloud services and Azure",
            "url": "https://learn.microsoft.com/certifications/exams/az-900",
            "level": "fundamentals"
        },
        "power platform": {
            "exam_code": "PL-900",
            "title": "Microsoft Power Platform Fundamentals",
            "description": "Demonstrates foundational knowledge of Power Platform",
            "url": "https://learn.microsoft.com/certifications/exams/pl-900",
            "level": "fundamentals"
        }
    }

    # Find matching certification
    skill_lower = certification_area.lower()
    for key, cert in cert_mapping.items():
        if key in skill_lower:
            return [cert]

    # Default to Azure fundamentals
    return [cert_mapping["azure"]]
