from infra.database import create_weaviate_client
from weaviate.classes.data import DataObject
from infra import load_db_config

db_config=load_db_config()

def check_collections():
    memory_schema=db_config['classes']
    clnt=create_weaviate_client()
    existing={x for x in clnt.collections.list_all()}
    try:
        for i,z in memory_schema.items():
            if i in existing:
                print(f"collection {clnt.collections.use(i).config.get()}")
    finally :
        clnt.close()

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

if __name__=="__main__":
    check_collections()
    test_insert_and_read()
    test_semantic_search()