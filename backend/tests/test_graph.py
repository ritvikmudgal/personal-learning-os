"""Tests for concept graph service, cycle detection, and DAG traversals."""

import pytest
from app.domain.concept import ConceptCreate, ConceptRelationshipCreate
from app.services.graph_service import GraphService


@pytest.mark.asyncio
async def test_concept_crud(test_session):
    """Test concept creation and retrieval."""
    service = GraphService(test_session)
    concept = await service.create_concept(
        ConceptCreate(name="Set Theory", domain="Mathematics", difficulty_level="beginner")
    )
    assert concept.id is not None
    assert concept.name == "Set Theory"

    retrieved = await service.get_concept(concept.id)
    assert retrieved is not None
    assert retrieved.name == "Set Theory"


@pytest.mark.asyncio
async def test_prerequisite_traversal(test_session):
    """Test direct and transitive prerequisite traversal."""
    service = GraphService(test_session)
    c1 = await service.create_concept(ConceptCreate(name="Arithmetic"))
    c2 = await service.create_concept(ConceptCreate(name="Algebra"))
    c3 = await service.create_concept(ConceptCreate(name="Calculus"))

    # Arithmetic is prerequisite for Algebra (Arithmetic -> Algebra)
    await service.create_relationship(
        ConceptRelationshipCreate(
            source_concept_id=c1.id,
            target_concept_id=c2.id,
            relationship_type="prerequisite",
        )
    )
    # Algebra is prerequisite for Calculus (Algebra -> Calculus)
    await service.create_relationship(
        ConceptRelationshipCreate(
            source_concept_id=c2.id,
            target_concept_id=c3.id,
            relationship_type="prerequisite",
        )
    )

    # Direct prerequisites of Calculus
    direct_prereqs = await service.get_direct_prerequisites(c3.id)
    assert len(direct_prereqs) == 1
    assert direct_prereqs[0].name == "Algebra"

    # Transitive prerequisites of Calculus
    all_prereqs = await service.traverse_prerequisite_chain(c3.id)
    prereq_names = [p.name for p in all_prereqs]
    assert "Algebra" in prereq_names
    assert "Arithmetic" in prereq_names


@pytest.mark.asyncio
async def test_cycle_detection(test_session):
    """Test that creating a prerequisite cycle is rejected."""
    service = GraphService(test_session)
    c1 = await service.create_concept(ConceptCreate(name="A"))
    c2 = await service.create_concept(ConceptCreate(name="B"))
    c3 = await service.create_concept(ConceptCreate(name="C"))

    # A -> B -> C
    await service.create_relationship(
        ConceptRelationshipCreate(
            source_concept_id=c1.id,
            target_concept_id=c2.id,
            relationship_type="prerequisite",
        )
    )
    await service.create_relationship(
        ConceptRelationshipCreate(
            source_concept_id=c2.id,
            target_concept_id=c3.id,
            relationship_type="prerequisite",
        )
    )

    # Attempt C -> A (would make A -> B -> C -> A cycle)
    with pytest.raises(ValueError, match="cycle"):
        await service.create_relationship(
            ConceptRelationshipCreate(
                source_concept_id=c3.id,
                target_concept_id=c1.id,
                relationship_type="prerequisite",
            )
        )


@pytest.mark.asyncio
async def test_subgraph_retrieval(test_session):
    """Test prerequisite subgraph (nodes and edges) extraction."""
    service = GraphService(test_session)
    c1 = await service.create_concept(ConceptCreate(name="Physics 101"))
    c2 = await service.create_concept(ConceptCreate(name="Vector Math"))
    await service.create_relationship(
        ConceptRelationshipCreate(
            source_concept_id=c2.id,
            target_concept_id=c1.id,
            relationship_type="prerequisite",
        )
    )

    nodes, edges = await service.get_prerequisite_subgraph(c1.id)
    node_names = {n.name for n in nodes}
    assert "Physics 101" in node_names
    assert "Vector Math" in node_names
    assert (c2.id, c1.id) in edges
