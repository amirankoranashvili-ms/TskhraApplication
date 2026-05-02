import logging

from elasticsearch import AsyncElasticsearch

from src.app.core.config import settings

logger = logging.getLogger(__name__)

PRODUCTS_INDEX = "products"

INDEX_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "analyzer": {
            "product_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "asciifolding"],
            }
        }
    },
}

INDEX_MAPPINGS = {
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "text", "analyzer": "product_analyzer", "fields": {"keyword": {"type": "keyword"}}},
        "description": {"type": "text", "analyzer": "product_analyzer"},
        "price": {"type": "float"},
        "sku": {"type": "keyword"},
        "category_id": {"type": "integer"},
        "category_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "brand_id": {"type": "integer"},
        "brand_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "brand_logo_url": {"type": "keyword", "index": False},
        "cover_image_url": {"type": "keyword", "index": False},
        "stock_quantity": {"type": "integer"},
        "is_active": {"type": "boolean"},
        "is_deleted": {"type": "boolean"},
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"},
        "spec_values": {"type": "keyword"},
        "spec_fields": {"type": "object", "enabled": True},
    }
}


def get_elasticsearch_client() -> AsyncElasticsearch:
    kwargs: dict = {"hosts": [settings.ELASTICSEARCH_URL]}
    if settings.ELASTICSEARCH_PASSWORD:
        kwargs["basic_auth"] = ("elastic", settings.ELASTICSEARCH_PASSWORD)
    return AsyncElasticsearch(**kwargs)


async def setup_elasticsearch_index() -> None:
    client = get_elasticsearch_client()
    try:
        exists = await client.indices.exists(index=PRODUCTS_INDEX)
        if not exists:
            await client.indices.create(
                index=PRODUCTS_INDEX,
                settings=INDEX_SETTINGS,
                mappings=INDEX_MAPPINGS,
            )
            logger.info("Elasticsearch index '%s' created.", PRODUCTS_INDEX)
        else:
            await client.indices.put_mapping(index=PRODUCTS_INDEX, body=INDEX_MAPPINGS)
            logger.info("Elasticsearch index '%s' mappings updated.", PRODUCTS_INDEX)
    finally:
        await client.close()
