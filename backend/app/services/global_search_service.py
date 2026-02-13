"""
Global Search Service
Implements cross-module search functionality using PostgreSQL full-text search
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text

from app.models.recipe import Recipe
from app.models.knowledge_article import KnowledgeArticle
from app.models.priority_item import PriorityItem
from app.models.project import Project
from app.models.insurance_policy import InsurancePolicy
from app.models.document import Document
from app.models.expense_category import ExpenseCategory
from app.models.income_source import IncomeSource


class GlobalSearchService:
    """Service for global search across all modules"""

    @staticmethod
    def search_all(
        db: Session,
        query: str,
        limit: int = 50,
        modules: Optional[list[str]] = None
    ) -> dict:
        """
        Search across all modules

        Args:
            db: Database session
            query: Search query string
            limit: Maximum results per module
            modules: Optional list of modules to search (default: all)
                    Options: recipes, knowledge, projects, priorities, assets, financial

        Returns:
            Dictionary with search results grouped by module
        """
        results = {}

        # Default to all modules if none specified
        if modules is None:
            modules = ["recipes", "knowledge", "projects", "priorities", "assets", "financial"]

        if "recipes" in modules:
            results["recipes"] = GlobalSearchService._search_recipes(db, query, limit)

        if "knowledge" in modules:
            results["knowledge"] = GlobalSearchService._search_knowledge(db, query, limit)

        if "projects" in modules:
            results["projects"] = GlobalSearchService._search_projects(db, query, limit)

        if "priorities" in modules:
            results["priorities"] = GlobalSearchService._search_priorities(db, query, limit)

        if "assets" in modules:
            results["assets"] = GlobalSearchService._search_assets(db, query, limit)

        if "financial" in modules:
            results["financial"] = GlobalSearchService._search_financial(db, query, limit)

        # Calculate total results
        total_results = sum(len(module_results) for module_results in results.values())

        return {
            "query": query,
            "total_results": total_results,
            "results": results
        }

    @staticmethod
    def _search_recipes(db: Session, query: str, limit: int) -> list[dict]:
        """Search recipes by name and ingredient names"""
        from app.models.ingredient import Ingredient

        search_pattern = f"%{query}%"

        # Search in recipe name or ingredient names
        recipes = db.query(Recipe).outerjoin(Recipe.ingredients).filter(
            or_(
                Recipe.name.ilike(search_pattern),
                Recipe.steps.ilike(search_pattern),
                Ingredient.name.ilike(search_pattern)
            )
        ).distinct().limit(limit).all()

        return [
            {
                "id": str(r.id),
                "type": "recipe",
                "title": r.name,
                "subtitle": f"{len(r.ingredients)} ingredients",
                "url": f"/meals/recipes/{r.id}",
                "module": "recipes"
            }
            for r in recipes
        ]

    @staticmethod
    def _search_knowledge(db: Session, query: str, limit: int) -> list[dict]:
        """Search knowledge articles using PostgreSQL FTS"""
        # Use PostgreSQL full-text search on search_vector
        query_text = query.replace(" ", " & ")  # Convert to tsquery format

        try:
            articles = db.query(KnowledgeArticle).filter(
                KnowledgeArticle.search_vector.op('@@')(func.to_tsquery('english', query_text))
            ).limit(limit).all()
        except:
            # Fallback to ILIKE if FTS fails (e.g., invalid query)
            search_pattern = f"%{query}%"
            articles = db.query(KnowledgeArticle).filter(
                or_(
                    KnowledgeArticle.title.ilike(search_pattern),
                    KnowledgeArticle.description.ilike(search_pattern)
                )
            ).limit(limit).all()

        return [
            {
                "id": str(a.id),
                "type": "knowledge_article",
                "title": a.title,
                "subtitle": a.article_type.value,
                "url": f"/knowledge/{a.id}",
                "module": "knowledge"
            }
            for a in articles
        ]

    @staticmethod
    def _search_projects(db: Session, query: str, limit: int) -> list[dict]:
        """Search projects by name and description"""
        search_pattern = f"%{query}%"

        projects = db.query(Project).filter(
            or_(
                Project.name.ilike(search_pattern),
                Project.description.ilike(search_pattern)
            )
        ).limit(limit).all()

        return [
            {
                "id": str(p.id),
                "type": "project",
                "title": p.name,
                "subtitle": f"Status: {p.status.value}",
                "url": f"/projects/{p.id}",
                "module": "projects"
            }
            for p in projects
        ]

    @staticmethod
    def _search_priorities(db: Session, query: str, limit: int) -> list[dict]:
        """Search priority items by name and description"""
        search_pattern = f"%{query}%"

        priorities = db.query(PriorityItem).filter(
            or_(
                PriorityItem.name.ilike(search_pattern),
                PriorityItem.description.ilike(search_pattern)
            )
        ).limit(limit).all()

        return [
            {
                "id": str(p.id),
                "type": "priority_item",
                "title": p.name,
                "subtitle": f"Net Score: {p.net_score}",
                "url": f"/projects/priorities/{p.id}",
                "module": "priorities"
            }
            for p in priorities
        ]

    @staticmethod
    def _search_assets(db: Session, query: str, limit: int) -> list[dict]:
        """Search insurance policies and documents"""
        search_pattern = f"%{query}%"

        results = []

        # Search insurance policies
        policies = db.query(InsurancePolicy).filter(
            or_(
                InsurancePolicy.policy_name.ilike(search_pattern),
                InsurancePolicy.provider.ilike(search_pattern),
                InsurancePolicy.policy_number.ilike(search_pattern)
            )
        ).limit(limit // 2).all()

        for p in policies:
            results.append({
                "id": str(p.id),
                "type": "insurance_policy",
                "title": p.policy_name,
                "subtitle": f"{p.policy_type.value} - {p.provider}",
                "url": f"/assets/insurance/{p.id}",
                "module": "assets"
            })

        # Search documents
        documents = db.query(Document).filter(
            or_(
                Document.title.ilike(search_pattern),
                Document.description.ilike(search_pattern)
            )
        ).limit(limit // 2).all()

        for d in documents:
            results.append({
                "id": str(d.id),
                "type": "document",
                "title": d.title,
                "subtitle": d.document_type.value,
                "url": f"/assets/documents/{d.id}",
                "module": "assets"
            })

        return results[:limit]

    @staticmethod
    def _search_financial(db: Session, query: str, limit: int) -> list[dict]:
        """Search expense categories and income sources"""
        search_pattern = f"%{query}%"

        results = []

        # Search expense categories
        categories = db.query(ExpenseCategory).filter(
            or_(
                ExpenseCategory.name.ilike(search_pattern),
                ExpenseCategory.description.ilike(search_pattern)
            )
        ).limit(limit // 2).all()

        for c in categories:
            results.append({
                "id": str(c.id),
                "type": "expense_category",
                "title": c.name,
                "subtitle": f"Category - ${c.budgeted_amount:.2f}",
                "url": f"/financial/categories/{c.id}",
                "module": "financial"
            })

        # Search income sources
        income_sources = db.query(IncomeSource).filter(
            or_(
                IncomeSource.name.ilike(search_pattern),
                IncomeSource.description.ilike(search_pattern)
            )
        ).limit(limit // 2).all()

        for i in income_sources:
            results.append({
                "id": str(i.id),
                "type": "income_source",
                "title": i.name,
                "subtitle": f"Income - ${i.amount:.2f}/{i.frequency.value}",
                "url": f"/financial/income/{i.id}",
                "module": "financial"
            })

        return results[:limit]

    @staticmethod
    def quick_search(db: Session, query: str, limit: int = 10) -> list[dict]:
        """
        Quick search for autocomplete/quick results
        Returns top results across all modules mixed together

        Args:
            db: Database session
            query: Search query string
            limit: Total maximum results to return

        Returns:
            List of search results sorted by relevance
        """
        all_results = GlobalSearchService.search_all(db, query, limit=5)

        # Flatten all results into single list
        combined = []
        for module_name, module_results in all_results["results"].items():
            combined.extend(module_results)

        # Sort by relevance (exact matches first, then partial matches)
        query_lower = query.lower()

        def relevance_score(item):
            title_lower = item["title"].lower()
            if title_lower == query_lower:
                return 0  # Exact match
            elif title_lower.startswith(query_lower):
                return 1  # Starts with
            elif query_lower in title_lower:
                return 2  # Contains
            else:
                return 3  # Other match

        combined.sort(key=relevance_score)

        return combined[:limit]
