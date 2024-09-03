# Doctor's AI Receptionist

This project is a Streamlit application designed to act as an AI receptionist for a doctor. The AI receptionist can handle emergency situations and take messages for the doctor, providing immediate assistance to patients while they wait for the doctor to arrive.

## Features

- **Emergency Handling**: The AI guides the patient through describing their emergency and provides instructions based on a vector search.
- **Message Taking**: The AI can take messages for the doctor and confirm receipt.
- **Location Processing**: The AI asks for the patient's location to provide accurate information to the doctor.

## Setup Instructions

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or above
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/omkar806/AI_Receptionist
cd AI_Receiptionist_Doctor
```
### Install Required Packages
```bash
python -m venv venv # Use python3 for mac
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
### Set Up Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```
### Run the Application
```bash
streamlit run app.py
```

### Upsert Data to Pinecone Vector Database
- To upsert the symptom and solution data to the Pinecone vector database, uncomment and run the following code snippet in vector_database.py:
```bash
for ds in dataset_var:
    embedding = create_embeddings(ds['symptom'])
    index.upsert(
    vectors=[
        {"id": ds['solution'], "values": embedding},
    ],
    namespace="ai-receptionist-namespace-1"
    )   
    print(ds['symptom'], ds['solution'])
```



