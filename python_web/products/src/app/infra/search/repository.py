import logging
from typing import List, Tuple, Optional

from elasticsearch import AsyncElasticsearch

from src.app.core.schemas.product_schemas import ProductSlim
from src.app.core.products.entities import Brand
from src.app.infra.search.client import PRODUCTS_INDEX

logger = logging.getLogger(__name__)


class ElasticsearchProductRepository:
    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def search_products(
        self,
        q: str,
        limit: int,
        offset: int,
        *,
        in_stock: bool = True,
        category_id: Optional[int] = None,
        brand_ids: Optional[List[int]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort: Optional[List[str]] = None,
        spec_filters: Optional[dict] = None,
    ) -> Tuple[List[ProductSlim], int]:
        must = [{"multi_match": {"query": q, "fields": ["title^3", "sku^2", "brand_name", "category_name"]}}]
        filter_clauses = [
            {"term": {"is_active": True}},
            {"term": {"is_deleted": False}},
        ]

        if in_stock:
            filter_clauses.append({"range": {"stock_quantity": {"gt": 0}}})
        if category_id is not None:
            filter_clauses.append({"term": {"category_id": category_id}})
        if brand_ids:
            filter_clauses.append({"terms": {"brand_id": brand_ids}})

        price_range = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        if price_range:
            filter_clauses.append({"range": {"price": price_range}})

        if spec_filters:
            for field_name, values in spec_filters.items():
                filter_clauses.append({"terms": {f"spec_fields.{field_name}": values}})

        es_sort = self._build_sort(sort)

        body = {
            "query": {"bool": {"must": must, "filter": filter_clauses}},
            "from": offset,
            "size": limit,
            "_source": [
                "id", "title", "price", "cover_image_url",
                "brand_id", "brand_name", "brand_logo_url", "stock_quantity",
            ],
        }
        if es_sort:
            body["sort"] = es_sort

        result = await self.client.search(index=PRODUCTS_INDEX, body=body)

        products = []
        for hit in result["hits"]["hits"]:
            src = hit["_source"]
            product = ProductSlim(
                id=src["id"],
                brand=Brand(
                    id=src.get("brand_id", 0),
                    name=src.get("brand_name", ""),
                    logo_url=src.get("brand_logo_url"),
                ),
                price=src["price"],
                title=src["title"],
                cover_image_url=src.get("cover_image_url"),
                stock_quantity=src.get("stock_quantity", 0),
            )
            products.append(product)

        total_count = result["hits"]["total"]["value"]
        return products, total_count

    @staticmethod
    def _build_sort(sort: Optional[List[str]]) -> list | None:
        if not sort:
            return None
        es_sort = []
        for s in sort:
            parts = s.split(":")
            field = parts[0]
            order = parts[1] if len(parts) > 1 else "asc"
            es_sort.append({field: {"order": order}})
        return es_sort

    async def index_product(self, product_data: dict) -> None:
        await self.client.index(
            index=PRODUCTS_INDEX,
            id=str(product_data["id"]),
            document=product_data,
        )
        logger.info("Indexed product %s in Elasticsearch.", product_data.get("id"))

    async def index_products_batch(self, products: List[dict]) -> None:
        if not products:
            return
        actions = []
        for doc in products:
            actions.append({"index": {"_index": PRODUCTS_INDEX, "_id": str(doc["id"])}})
            actions.append(doc)
        await self.client.bulk(operations=actions, refresh="wait_for")
        logger.info("Indexed %d products in Elasticsearch.", len(products))

    async def delete_product_document(self, product_id: int) -> None:
        try:
            await self.client.delete(index=PRODUCTS_INDEX, id=str(product_id))
            logger.info("Deleted product %s from Elasticsearch index.", product_id)
        except Exception:
            logger.warning("Product %s not found in Elasticsearch for deletion.", product_id)

    async def delete_all_documents(self) -> None:
        await self.client.delete_by_query(
            index=PRODUCTS_INDEX,
            body={"query": {"match_all": {}}},
            refresh=True,
        )
        logger.info("Deleted all documents from Elasticsearch index.")
