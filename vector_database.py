from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
load_dotenv()
import os
from dataset import dataset_var
from create_embeddings import create_embeddings


pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

index_name = "ai-receptionist"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    )

#Creating a vector index
index = pc.Index(index_name)


def vector_search_v1(emergency_description):
    emergency_embedding = create_embeddings(emergency_description)
    query_results = index.query(
    namespace="ai-receptionist-namespace-1",
    vector=emergency_embedding,
    top_k=1,
    include_values=True
    )
    answers=  ""
    answers += query_results.get('matches','')[0].get('id')
    return answers
    # return "Perform CPR: Place your hands on the center of the chest and push hard and fast at a rate of 100-120 compressions per minute. After every 30 compressions, give 2 rescue breaths."

#inserting the data['symptoms'] into the pinecone 

# for ds in dataset_var:
#     embedding = create_embeddings(ds['symptom'])
#     index.upsert(
#     vectors=[
#         {"id": ds['solution'], "values": embedding},
#     ],
#     namespace="ai-receptionist-namespace-1"
#     )   
#     print(ds['symptom'] , ds['solution'])


