import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# We use this model because it runs very fast on standard CPUs
# and it is only about 90MB in size. We load it globally once.
MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

def get_embedding(text):
    """Produces a vector embedding for the given text."""
    # Convert text to a vector array. We do not trim the text anymore 
    # to make sure we don't miss deep details.
    return model.encode(text, convert_to_numpy=True)

def build_index(chunks):
    """Builds and returns a FAISS Flat L2 index from a list of strings."""
    # If there is nothing to index, return nothing
    if not chunks:
        return None
    
    # Generate vectors for every piece of text we have
    embeddings = np.array([get_embedding(chunk) for chunk in chunks])
    
    # Get the size of the vectors so we can setup FAISS database
    dimension = embeddings.shape[1]
    
    # Setup a local vector database that works on CPU
    index = faiss.IndexFlatL2(dimension)
    
    # Put all our text vectors inside the database
    index.add(embeddings)
    
    return index
