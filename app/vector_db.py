from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

with open(
    "attack_samples/jailbreaks.txt",
    "r",
    encoding="utf-8"
) as file:

    attack_samples = [
        line.strip()
        for line in file
        if line.strip()
    ]

attack_embeddings = model.encode(
    attack_samples
)

def semantic_scan(prompt):

    prompt_embedding = model.encode(
        [prompt]
    )

    similarities = cosine_similarity(
        prompt_embedding,
        attack_embeddings
    )[0]

    max_similarity = float(
        np.max(similarities)
    )

    return {
        "similarity": round(max_similarity, 3),
        "blocked": max_similarity > 0.5
    }
