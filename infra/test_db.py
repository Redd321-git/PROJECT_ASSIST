from infra.database import create_weaviate_client
from weaviate.classes.data import DataObject

def test_insert_and_read():
    client = create_weaviate_client()

    try:
        coll = client.collections.get("EpisodicMemory")

        uuid = coll.data.insert(
            properties={
                "doc_id": "test-2",
                "doc": "thi is the second time i asked how to test Weaviate",
                "memory_type": "episodic"
            }
        )

        print("Inserted UUID:", uuid)

        obj = coll.query.fetch_object_by_id(uuid)
        print("Fetched object:", obj.properties)

    finally:
        client.close()

test_insert_and_read()


def test_semantic_search():
    client = create_weaviate_client()

    try:
        coll = client.collections.get("SemanticMemory")

        coll.data.insert_many([
            {
                "doc_id": "1",
                "doc": "Postgres database initialized successfully",
                "memory_type": "semantic"
            },
            {
                "doc_id": "2",
                "doc": "Weaviate vector database schema created",
                "memory_type": "semantic"
            },
            {
                "doc_id": "3",
                "doc": "User is testing vector search functionality",
                "memory_type": "semantic"
            }
        ])

        res = coll.query.near_text(
            query="how do I test vector search",
            limit=2
        )

        for o in res.objects:
            print(o.properties)

    finally:
        client.close()

test_semantic_search()