from unittest.mock import MagicMock

from src.app.core.products.entities import SortByOption
from src.app.infra.database.utils import (
    PriceAscSortHandler,
    PriceDescSortHandler,
    NewestSortHandler,
    PopularSortHandler,
)


def _build_chain():
    chain = PriceAscSortHandler()
    chain.set_next(PriceDescSortHandler()).set_next(NewestSortHandler()).set_next(
        PopularSortHandler()
    )
    return chain


def test_price_asc_sort():
    chain = _build_chain()
    mock_stmt = MagicMock()
    result = chain.handle(mock_stmt, SortByOption.PRICE_ASC)
    assert result is not None
    mock_stmt.order_by.assert_called_once()


def test_price_desc_sort():
    chain = _build_chain()
    mock_stmt = MagicMock()
    result = chain.handle(mock_stmt, SortByOption.PRICE_DESC)
    assert result is not None


def test_newest_sort():
    chain = _build_chain()
    mock_stmt = MagicMock()
    result = chain.handle(mock_stmt, SortByOption.NEWEST)
    assert result is not None


def test_popular_sort():
    chain = _build_chain()
    mock_stmt = MagicMock()
    result = chain.handle(mock_stmt, SortByOption.POPULAR)
    assert result is not None


def test_chain_fallback():
    chain = PriceAscSortHandler()
    mock_stmt = MagicMock()
    _ = chain.handle(mock_stmt, SortByOption.POPULAR)
    mock_stmt.order_by.assert_called_once()
