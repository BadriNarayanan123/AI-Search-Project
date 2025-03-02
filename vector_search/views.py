import pinecone
from pinecone import Pinecone, ServerlessSpec
import torch
from sentence_transformers import SentenceTransformer
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Summary
from .serializers import SummarySerializer
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Summary
from .serializers import SummarySerializer
from .forms import SummaryForm
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Load Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

PINECONE_API_KEY = "pcsk_6opxAT_CATniGf9sdiAn2LUTzqGU2qy8Stdvqr52eP4CWFkBt5dTb6ycXuXz6fASvSMR59"
PINECONE_INDEX_NAME = "summary-search-modified"

pc = Pinecone(api_key=PINECONE_API_KEY)
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,  # Adjust based on your model's output dimension
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(PINECONE_INDEX_NAME)

# Generate Embeddings
def generate_embedding(text):
    try:
        embedding = model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# API: Search for Similar Summaries
import json  # ✅ Import JSON to ensure correct serialization

@api_view(["POST"])
def search(request):
    query = request.data.get("query")
    embedding = generate_embedding(query)

    if embedding is None:  # ✅ Handle NoneType error
        return Response({"error": "Failed to generate embedding for query."}, status=400)

    try:
        results = index.query(vector=embedding, top_k=5, include_metadata=True)

        print("Raw Pinecone Response:", results)  # ✅ Debugging step

        if results is None or "matches" not in results:
            return Response({"error": "No matching results found."}, status=404)

        #Convert Pinecone response to JSON-safe format
        formatted_results = {
            "matches": [
                {
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {})  # Handle missing metadata
                }
                for match in results.get("matches", [])
            ]
        }

        return Response(json.loads(json.dumps(formatted_results)))  # ✅ Ensure valid JSON response

    except Exception as e:
        print(f"Pinecone Query Error: {e}")
        return Response({"error": "Failed to query Pinecone database."}, status=500)



# ✅ Store summaries per user
@api_view(["POST"])
def summarize(request):
    text = request.data.get("text")
    category = request.data.get("category", "General")

    if not text:
        return Response({"error": "Text is required"}, status=400)

    embedding = generate_embedding(text)
    
    if embedding is None:
        return Response({"error": "Failed to generate embedding"}, status=400)

    try:
        summary = Summary.objects.create(
            user=request.user,
            text=text,
            embedding_id="id_" + str(Summary.objects.count() + 1),
            category=category
        )

        # Debugging: Print values before inserting into Pinecone
        print(f"Storing in Pinecone: ID={summary.embedding_id}, Text={text}, Category={category}")

        index.upsert([
            (summary.embedding_id, embedding, {"text": text, "category": category})
        ])

        return Response({"message": "Stored successfully", "summary_id": summary.id})
    
    except Exception as e:
        print(f"Error storing in Pinecone: {e}")
        return Response({"error": "Failed to store summary"}, status=500)


# ✅ Enable filtering by category & date
@login_required
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_summaries(request):
    sort_order = request.GET.get("sort", "desc")

    summaries = Summary.objects.filter(user=request.user)

    if sort_order == "asc":
        summaries = summaries.order_by("created_at")
    else:
        summaries = summaries.order_by("-created_at")

    serializer = SummarySerializer(summaries, many=True)
    return Response(serializer.data)


# ✅ Render UI: Dashboard with Summaries
@login_required
def dashboard(request):
    csrf_token = get_token(request)  # Get CSRF token for frontend

    if request.method == "POST":
        text = request.POST.get("text")
        category = request.POST.get("category", "General")

        embedding = generate_embedding(text)
        if embedding:
            summary = Summary.objects.create(
                user=request.user,
                text=text,
                embedding_id="id_" + str(Summary.objects.count() + 1),
                category=category
            )
            index.upsert([(summary.embedding_id, embedding, {"text": text, "category": category})])
            return redirect("dashboard")  # Refresh page after storing

    summaries = Summary.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "vector_search/dashboard.html", {"summaries": summaries, "csrf_token": csrf_token})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "vector_search/register.html", {"form": form})

def get_search_summary(request):
    if request.method == "GET":
        search_term = request.GET.get('search_query','')
        summaries = Summary.objects.filter(text__icontains = search_term)
        return render(request, "vector_search/dashboard.html", {"summaries": summaries})
