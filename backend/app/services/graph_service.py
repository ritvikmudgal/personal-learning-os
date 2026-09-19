"""Concept graph service — graph algorithms and concept relationships."""

from collections import deque
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Concept, ConceptRelationship, RelationshipType
from app.db.repositories.concept_repo import ConceptRepository
from app.domain.concept import ConceptCreate, ConceptRelationshipCreate
from app.utils.logging import get_logger

logger = get_logger("service.graph")


class GraphService:
    """Service for concept graph management and DAG traversal algorithms."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ConceptRepository(session)

    async def create_concept(self, data: ConceptCreate) -> Concept:
        """Create a new concept."""
        return await self.repo.create(data)

    async def update_concept(self, concept_id: int, data: dict) -> Concept | None:
        """Update an existing concept."""
        return await self.repo.update(concept_id, data)

    async def get_concept(self, concept_id: int) -> Concept | None:
        """Get a concept by ID."""
        return await self.repo.get_by_id(concept_id)

    async def get_all_concepts(self, domain: str | None = None) -> list[Concept]:
        """Get all concepts, optionally filtered by domain."""
        return await self.repo.get_all(domain=domain)

    async def create_relationship(
        self, data: ConceptRelationshipCreate
    ) -> ConceptRelationship:
        """Create a relationship between concepts, checking for cycles if PREREQUISITE."""
        if data.source_concept_id == data.target_concept_id:
            raise ValueError("A concept cannot have a relationship with itself")

        source = await self.repo.get_by_id(data.source_concept_id)
        if not source:
            raise ValueError(f"Source concept {data.source_concept_id} not found")

        target = await self.repo.get_by_id(data.target_concept_id)
        if not target:
            raise ValueError(f"Target concept {data.target_concept_id} not found")

        rel_type = RelationshipType(data.relationship_type)
        if rel_type == RelationshipType.PREREQUISITE:
            if await self.would_create_cycle(
                data.source_concept_id, data.target_concept_id
            ):
                raise ValueError(
                    f"Creating prerequisite relationship from {data.source_concept_id} "
                    f"to {data.target_concept_id} would introduce a cycle"
                )

        return await self.repo.add_relationship(data)

    async def remove_relationship(self, relationship_id: int) -> bool:
        """Remove a relationship by ID."""
        return await self.repo.remove_relationship(relationship_id)

    async def get_direct_prerequisites(self, concept_id: int) -> list[Concept]:
        """Get direct prerequisites for a concept."""
        return await self.repo.get_prerequisites(concept_id)

    async def get_direct_dependents(self, concept_id: int) -> list[Concept]:
        """Get direct dependents for a concept."""
        return await self.repo.get_dependents(concept_id)

    async def would_create_cycle(self, source_id: int, target_id: int) -> bool:
        """Check if adding edge source_id -[PREREQUISITE]-> target_id creates a cycle.

        Source is prerequisite of Target (source -> target).
        A cycle would be created if source_id is reachable from target_id following dependent edges.
        """
        visited = set()
        queue = deque([target_id])

        while queue:
            curr_id = queue.popleft()
            if curr_id == source_id:
                return True
            if curr_id in visited:
                continue
            visited.add(curr_id)

            dependents = await self.repo.get_dependents(curr_id)
            for d in dependents:
                if d.id not in visited:
                    queue.append(d.id)

        return False


    async def traverse_prerequisite_chain(
        self, concept_id: int
    ) -> list[Concept]:
        """Get all transitive prerequisites of a concept using BFS.

        Returns list of Concept objects ordered by traversal depth.
        """
        visited = set()
        queue = deque([concept_id])
        result = []

        while queue:
            curr_id = queue.popleft()
            if curr_id in visited:
                continue
            visited.add(curr_id)

            if curr_id != concept_id:
                concept = await self.repo.get_by_id(curr_id)
                if concept:
                    result.append(concept)

            prereqs = await self.repo.get_prerequisites(curr_id)
            for p in prereqs:
                if p.id not in visited:
                    queue.append(p.id)

        return result

    async def traverse_dependent_chain(
        self, concept_id: int
    ) -> list[Concept]:
        """Get all transitive dependents of a concept using BFS.

        Returns list of Concept objects ordered by traversal depth.
        """
        visited = set()
        queue = deque([concept_id])
        result = []

        while queue:
            curr_id = queue.popleft()
            if curr_id in visited:
                continue
            visited.add(curr_id)

            if curr_id != concept_id:
                concept = await self.repo.get_by_id(curr_id)
                if concept:
                    result.append(concept)

            dependents = await self.repo.get_dependents(curr_id)
            for d in dependents:
                if d.id not in visited:
                    queue.append(d.id)

        return result

    async def get_prerequisite_subgraph(
        self, concept_id: int
    ) -> tuple[list[Concept], list[tuple[int, int]]]:
        """Get full prerequisite DAG starting from concept_id.

        Returns (nodes, edges) where edges are (source_id, target_id) tuples.
        """
        nodes_dict: dict[int, Concept] = {}
        edges: set[tuple[int, int]] = set()

        root = await self.repo.get_by_id(concept_id)
        if not root:
            return [], []

        nodes_dict[concept_id] = root
        queue = deque([concept_id])
        visited = set()

        while queue:
            curr_id = queue.popleft()
            if curr_id in visited:
                continue
            visited.add(curr_id)

            prereqs = await self.repo.get_prerequisites(curr_id)
            for p in prereqs:
                nodes_dict[p.id] = p
                edges.add((p.id, curr_id))  # p.id is prerequisite for curr_id
                if p.id not in visited:
                    queue.append(p.id)

        return list(nodes_dict.values()), list(edges)
