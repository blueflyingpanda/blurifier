import logging

from django.conf import settings
from elasticsearch import AsyncElasticsearch

from core.schemas import SearchResponseSchema

logger = logging.getLogger(__name__)


class ElasticsearchService:
    def __init__(self):
        self.index_name = settings.ELASTICSEARCH_INDEX_NAME

    async def create_index(self) -> bool:
        client = AsyncElasticsearch([settings.ELASTICSEARCH['default']['hosts']])
        try:
            exists = await client.indices.exists(index=self.index_name)
            if exists:
                return True

            mapping = {
                'mappings': {
                    'properties': {
                        'text_hash': {'type': 'keyword'},
                        'original_text': {'type': 'text'},
                        'processed_text': {'type': 'text'},
                    }
                }
            }

            await client.indices.create(index=self.index_name, body=mapping)
            return True
        except Exception as e:
            logger.error(f'Failed to create index: {e}')
            return False
        finally:
            await client.close()

    async def index_document(
        self, text_hash: str, original_text: str, processed_text: str | None = None
    ) -> bool:
        client = AsyncElasticsearch([settings.ELASTICSEARCH['default']['hosts']])
        try:
            document = {
                'text_hash': text_hash,
                'original_text': original_text,
                'processed_text': processed_text,
            }
            await client.index(index=self.index_name, id=text_hash, body=document)
            return True
        except Exception as e:
            logger.error(f'Failed to index document: {e}')
            return False
        finally:
            await client.close()

    async def search_text(self, query: str) -> list[SearchResponseSchema]:
        client = AsyncElasticsearch([settings.ELASTICSEARCH['default']['hosts']])
        try:
            search_body = {
                'query': {
                    'match': {
                        'original_text': {
                            'query': query,
                            'fuzziness': 'AUTO',
                            'operator': 'or',
                        }
                    }
                },
            }
            response = await client.search(index=self.index_name, body=search_body)
            results = []
            for hit in response['hits']['hits']:
                src = hit['_source']
                results.append(
                    SearchResponseSchema(
                        text_hash=src.get('text_hash', ''),
                        original_text=src.get('original_text', ''),
                        processed_text=src.get('processed_text'),
                    )
                )
            return results
        except Exception as e:
            logger.error(f'Search failed: {e}')
            return []
        finally:
            await client.close()


es_service = ElasticsearchService()
