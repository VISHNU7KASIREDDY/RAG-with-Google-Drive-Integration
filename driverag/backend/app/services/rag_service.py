from langchain_core.prompts import PromptTemplate
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

PROMPT = PromptTemplate(
    template="""You are a helpful assistant that answers questions based on the user's Google Drive documents.

Rules:
1. Answer based ONLY on the provided context.
2. If the context doesn't contain enough information, say so.
3. Cite the source document names when referencing information.
4. Be concise and accurate. Use markdown formatting.

Context:
{context}

Question: {question}

Answer:""",
    input_variables=["context", "question"],
)


def _get_llm():
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", google_api_key=settings.gemini_api_key, temperature=0.3,
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile", api_key=settings.groq_api_key, temperature=0.3,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo", api_key=settings.openai_api_key, temperature=0.3,
        )


def answer_question(session_id: str, vector_store, query: str, top_k: int = None) -> tuple[str, list[dict]]:
    top_k = top_k or settings.top_k_results

    results = vector_store.similarity_search(session_id, query, k=top_k)
    if not results:
        return "No relevant documents found. Please sync your Google Drive first.", []

    logger.info(f"Found {len(results)} chunks (top score: {results[0]['score']})")

    context = "\n\n---\n\n".join(
        f"[Source {i}: {r['file_name']}]\n{r['chunk_text']}"
        for i, r in enumerate(results, 1)
    )

    logger.info(f"Calling {settings.llm_provider} LLM")
    response = _get_llm().invoke(PROMPT.format(context=context, question=query))
    logger.info(f"Answer generated ({len(response.content)} chars)")

    return response.content, results
