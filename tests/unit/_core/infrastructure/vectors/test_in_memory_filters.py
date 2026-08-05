"""In-memory vector filter semantics (#328 F10).

`_matches_filters` handled `$eq`, `$in`, `$ne` and bare equality. Anything else
fell through every branch and the loop continued to `return True`, so an
unsupported operator was **silently discarded**:

    {"year": {"$gte": 2020}} matched a record with year=2015     # fails OPEN

A top-level `$and` is not a dict-valued *field* condition, so it took the bare
equality branch, compared `metadata.get("$and")` (None) against a list, and
matched nothing:

    {"$and": [...]} matched no record at all                     # fails CLOSED

Fail-open is the dangerous direction. `VectorQuery`'s docstring — the shared VO
both backends consume — advertises `{"year": {"$gte": 2020}}` and `{"$and": [...]}`
as *the* filter contract with no backend qualification, so a consumer writing
tenant or ACL scoping against it would get unfiltered results on the default
backend, with no error. `inmemory` is the default whenever `VECTOR_STORE_TYPE`
is unset, including in prod.

The fix is to be loud, not to implement the operators: `NotImplementedError`
names what is unsupported. Implementing `$gte`/`$and` here would make the
in-memory store *more* capable than the S3 Vectors backend it exists to stand in
for, which is the portability the class docstring promises.
"""

from __future__ import annotations

import pytest

from src._core.infrastructure.vectors.in_memory.base_store import _matches_filters

_METADATA = {"category": "tech", "year": 2015, "tenant": "acme"}


class TestSupportedOperators:
    def test_bare_equality_matches(self) -> None:
        assert _matches_filters(_METADATA, {"category": "tech"}) is True

    def test_bare_equality_rejects(self) -> None:
        assert _matches_filters(_METADATA, {"category": "sci"}) is False

    def test_eq(self) -> None:
        assert _matches_filters(_METADATA, {"category": {"$eq": "tech"}}) is True
        assert _matches_filters(_METADATA, {"category": {"$eq": "sci"}}) is False

    def test_in(self) -> None:
        assert (
            _matches_filters(_METADATA, {"category": {"$in": ["tech", "sci"]}}) is True
        )
        assert _matches_filters(_METADATA, {"category": {"$in": ["sci"]}}) is False

    def test_ne(self) -> None:
        assert _matches_filters(_METADATA, {"category": {"$ne": "tech"}}) is False
        assert _matches_filters(_METADATA, {"category": {"$ne": "sci"}}) is True

    def test_multiple_fields_are_conjunctive(self) -> None:
        assert _matches_filters(_METADATA, {"category": "tech", "year": 2015}) is True
        assert _matches_filters(_METADATA, {"category": "tech", "year": 2020}) is False


class TestUnsupportedOperatorsAreLoud:
    @pytest.mark.parametrize("operator", ["$gte", "$gt", "$lte", "$lt"])
    def test_comparison_operators_raise_instead_of_matching_everything(
        self, operator: str
    ) -> None:
        # Previously: returned True for year=2015 against {"$gte": 2020}.
        with pytest.raises(NotImplementedError) as exc:
            _matches_filters(_METADATA, {"year": {operator: 2020}})

        assert operator in str(exc.value)
        assert "year" in str(exc.value)

    def test_the_error_names_what_is_supported(self) -> None:
        with pytest.raises(NotImplementedError) as exc:
            _matches_filters(_METADATA, {"year": {"$gte": 2020}})

        message = str(exc.value)
        for supported in ("$eq", "$in", "$ne"):
            assert supported in message

    def test_a_supported_operator_beside_an_unsupported_one_still_raises(self) -> None:
        # Silently honouring the half it understands is the same fail-open bug
        # wearing a disguise.
        with pytest.raises(NotImplementedError):
            _matches_filters(_METADATA, {"year": {"$eq": 2015, "$gte": 2020}})

    @pytest.mark.parametrize("operator", ["$and", "$or", "$not"])
    def test_compound_operators_raise_instead_of_matching_nothing(
        self, operator: str
    ) -> None:
        # Previously: {"$and": [...]} took the bare-equality branch, compared
        # None against a list, and matched nothing — a filter that silently
        # empties every result set.
        with pytest.raises(NotImplementedError) as exc:
            _matches_filters(
                _METADATA, {operator: [{"category": "tech"}, {"year": 2015}]}
            )

        assert operator in str(exc.value)


class TestFailureDirection:
    def test_an_unsupported_filter_never_widens_a_result_set(self) -> None:
        """The property that matters, stated directly.

        A tenant-scoping filter that is silently dropped returns other tenants'
        rows. Raising is acceptable; matching more than asked is not.
        """
        with pytest.raises(NotImplementedError):
            _matches_filters(_METADATA, {"tenant": {"$gte": "zzz"}})

    def test_an_empty_filter_matches(self) -> None:
        # No filter is not an unsupported filter.
        assert _matches_filters(_METADATA, {}) is True
