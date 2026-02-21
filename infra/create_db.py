import psycopg2
from . import get_dotenv,load_db_config
from infra.database import create_db_engine, create_weaviate_client
from infra.models import Base
from weaviate.classes.config import Property,DataType,Configure
import weaviate

db_config=load_db_config()
env_file=get_dotenv()

def create_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT):
	con=psycopg2.connect(
		dbname=DB_NAME,
		user=DB_USER,
		password=DB_PASSWORD,
		host=DB_HOST,
		port=DB_PORT
	)
	con.autocommit=True
	return con

def create_rdatabase():
	con=create_connection("postgres", env_file['DB_USER'], env_file['DB_PASSWORD'], env_file['DB_HOST'], env_file['DB_PORT'])
	cur=con.cursor()
	cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{env_file['DB_NAME']}'")
	exists=cur.fetchone()
	if not exists:
		try:
			cur.execute(f"CREATE DATABASE {env_file['DB_NAME']};")
			con2=create_connection(env_file['DB_NAME'], env_file['DB_USER'], env_file['DB_PASSWORD'], env_file['DB_HOST'], env_file['DB_PORT'])
			cur2=con2.cursor()
			create_tables()
			print("{DB_NAME} created")
			cur2.close()
			con2.close()
		except Exception as e:
			print(f"Error creating database: {e}")
			cur.execute(f"DROP DATABASE IF EXISTS {env_file['DB_NAME']};")
			
	else:
		print("{DB_NAME} already exists")
	cur.close()
	con.close()
	
def create_tables():
	engine, SessionLocal = create_db_engine()
	Base.metadata.create_all(bind=engine)
	print("Tables created")
    
datatyp_map={
	'TEXT':DataType.TEXT,
	'DATE':DataType.DATE
}

def create_vdatabase():
	memory_schema=db_config['classes']
	clnt=create_weaviate_client()
	existing={x for x in clnt.collections.list_all()}
	try:
		for i,z in memory_schema.items():
			if i in existing:
				continue
			clnt.collections.create(
				name=i,
				properties=[Property(name=x['name'],data_type=datatyp_map[x['dataType']]) for x in z['properties']],
				description=z['description'],
				vectorizer_config=Configure.Vectorizer.text2vec_cohere(z['embid_model'])
			)
			print(f"collention create : {i}")
	finally :
		clnt.close()

create_rdatabase()
create_vdatabase()