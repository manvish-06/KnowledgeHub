from __future__ import annotations
import hashlib
import logging
import os
import re
import threading
import time
from dataclasses import dataclass
from typing import Any, Optional
from django.conf import settings
from django.db import models
from google import genai
from google.genai import errors, types
from .models import AIResponse

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "what",
    "which",
    "who",
    "whose",
    "when",
    "where",
    "why",
    "how",
    "can",
    "could",
    "would",
    "should",
    "shall",
    "may",
    "might",
    "will",
    "do",
    "does",
    "did",
    "of",
    "to",
    "for",
    "from",
    "into",
    "on",
    "in",
    "at",
    "by",
    "with",
    "about"
}




@dataclass(frozen=True)
class ArticleContext:
    title: str
    content: str
    source: str  # "database" or "wikipedia"
    entry: Optional[object] = None


# ==========================================================
# 2. GEMINI CONFIGURATION
# ==========================================================

MODEL_NAME = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = (
    getattr(settings, "GEMINI_API_KEY", None)
    or os.getenv("GEMINI_API_KEY")
)

if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip()

LLM_TIMEOUT = int(getattr(settings, "GEMINI_TIMEOUT", 60))
MAX_RETRIES = 3
RETRY_DELAY = 1


GENERATION_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 4096,
}

_generation_state = threading.local()


def _set_generation_metadata(**values: Any) -> None:
    _generation_state.metadata = {
        "model": MODEL_NAME,
        "elapsed": 0.0,
        "tokens": 0,
        "cached": False,
        **values,
    }


def get_generation_metadata() -> dict[str, Any]:
    return getattr(
        _generation_state,
        "metadata",
        {"model": MODEL_NAME, "elapsed": 0.0, "tokens": 0, "cached": False},
    )


class AIFeature(models.TextChoices):
    SUMMARY = "summary", "Summary"
    EXPLAIN = "explain", "Explain"
    NOTES = "notes", "Study Notes"
    QUIZ = "quiz", "Quiz"
    CHAT = "chat", "Chat"
    RELATED = "related", "Related"
    FLASHCARDS = "flashcards", "Flashcards"
    MINDMAP = "mindmap", "Mind Map"


FEATURE_LIMITS = {
    AIFeature.SUMMARY: 15000,
    AIFeature.EXPLAIN: 12000,
    AIFeature.NOTES: 15000,
    AIFeature.QUIZ: 12000,
    AIFeature.CHAT: 12000,
    AIFeature.RELATED: 5000,
    AIFeature.FLASHCARDS: 12000,
    AIFeature.MINDMAP: 15000,
}

SYSTEM_INSTRUCTIONS = {
    AIFeature.SUMMARY: "You are an expert encyclopedic summarizer. Provide clear, well-structured, accurate Markdown summaries.",
    AIFeature.EXPLAIN: "You are an intuitive teacher. Explain complex topics using simple analogies, relatable scenarios, and step-by-step breakdowns.",
    AIFeature.NOTES: "You are an academic study guide author. Synthesize material into clear, structured study notes with key terms and concepts.",
    AIFeature.QUIZ: "You are an educational assessment expert. Construct engaging quizzes with multiple-choice and short answer questions.",
    AIFeature.CHAT: "You are KnowledgeHub AI, a helpful learning assistant. Answer strictly from the provided article context and never invent information.",
    AIFeature.RELATED: "You are a knowledge graph curator. Suggest educational Wikipedia topics only.",
    AIFeature.FLASHCARDS: "You are a learning retention expert. Extract key facts and format them strictly as Question/Answer Markdown flashcards.",
    AIFeature.MINDMAP: "You are a visual data structurer. Map core concepts into a nested Markdown list hierarchy.",
}

DIFFICULTY_DIRECTIVES = {
    "easy": "Target Audience: Beginner / 10-year-old level. Use short sentences, basic vocabulary, and fun analogies.",
    "standard": "Target Audience: General Audience / Undergraduate level. Maintain standard academic clarity and depth.",
    "advanced": "Target Audience: Subject Matter Expert / Researcher level. Use technical terminology, nuanced context, and rigorous detail.",
}

PROMPTS = {
    AIFeature.SUMMARY: "Topic: {title}\n{difficulty_guide}\n\nGenerate a complete, high-quality Markdown summary in 2–3 concise paragraphs for the following text:\n\n{content}",
    AIFeature.EXPLAIN: "Topic: {title}\n{difficulty_guide}\n\nExplain the core concepts using vivid analogies, simple steps, and key takeaways:\n\n{content}",
    AIFeature.NOTES: "Topic: {title}\n{difficulty_guide}\n\nCreate comprehensive study notes organized as Key Terms & Definitions, Core Concepts & Principles, Summary Bullet Points, and Revision Tips.\n\nContent:\n{content}",
    AIFeature.QUIZ: "Topic: {title}\n{difficulty_guide}\n\nCreate 10 questions: 6 multiple-choice questions with A–D options, 2 True/False questions, and 2 short-answer questions. Include explanations and an answer key at the end.\n\nContent:\n{content}",
    AIFeature.FLASHCARDS: "Topic: {title}\n{difficulty_guide}\n\nCreate 5–10 flashcards formatted exactly as:\n**Q: [Question]**\n*A: [Answer]*\n\nContent:\n{content}",
    AIFeature.MINDMAP: "Topic: {title}\n{difficulty_guide}\n\nCreate a deeply nested Markdown-list mind map showing relationships and subtopics.\n\nContent:\n{content}",
    AIFeature.CHAT: "Article Title: {title}\n\nArticle Content:\n{content}\n\nUser Question: {question}\n\nAnswer only from the article. If absent, reply exactly: This information is not available in the current article. Never invent information.",
    AIFeature.RELATED: "Topic: {title}\n\nSuggest exactly 10 closely related Wikipedia article titles only. Format them as a Markdown list with no descriptions or commentary.",
}


def truncate_content(content: str, limit: int) -> str:
    if not content:
        return ""
    if len(content) <= limit:
        return content
    text = content[:limit]
    paragraph = text.rfind("\n")
    if paragraph > limit * 0.7:
        text = text[:paragraph]
    else:
        sentence = text.rfind(".")
        if sentence > limit * 0.7:
            text = text[: sentence + 1]
    return text.rstrip() + "\n\n*(Content truncated for length)*"


def extract_relevant_context(content: str, question: str) -> str:

    if not content:
        return ""


    sections = re.split(r"\n(?==+ .*? ==+)", content)

    if len(sections) == 1:
        sections = re.split(r"\n(?=# )", content)

    if len(sections) == 1:
        sections = [content]

    keywords = [
        w.lower()
        for w in re.findall(r"[A-Za-z]+", question)
        if len(w) > 2 and w.lower() not in STOP_WORDS
    ]

    if not keywords:
        return truncate_content(content, 4000)

    best_section = sections[0]
    best_score = -1

    for section in sections:

        text = section.lower()

        score = 0

        for word in keywords:

            count = text.count(word)

            if len(word) >= 8:
                score += count * 8
            elif len(word) >= 5:
                score += count * 5
            else:
                score += count

        if score > best_score:
            best_score = score
            best_section = section

    print("=" * 80)
    print("BEST SECTION SCORE:", best_score)
    print(best_section[:1000])
    print("=" * 80)

    return best_section


def clean_markdown(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\A```(?:markdown|md|text|plaintext|json|html)?\s*\n", "", text, flags=re.I)
    text = re.sub(r"\n\s*```\s*\Z", "", text)
    return text.strip()


def _response_text(response: Any) -> Optional[str]:
    try:
        if response.text:
            return clean_markdown(response.text)
    except Exception:
        pass
    try:
        parts = []
        for candidate in getattr(response, "candidates", []) or []:
            for part in getattr(getattr(candidate, "content", None), "parts", []) or []:
                if getattr(part, "text", None):
                    parts.append(part.text)
        return clean_markdown("\n".join(parts)) or None
    except Exception:
        logger.exception("Could not extract Gemini response text.")
        return None


def generate_hash(*parts: Any) -> str:
    value = "\x1f".join(str(part) for part in parts if part is not None)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()



def call_llm(prompt: str, system_instruction: str):


    if not GEMINI_API_KEY:
        return "⚠️ Gemini API key is missing."

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    except errors.ClientError as e:
        error = str(e)

        if "RESOURCE_EXHAUSTED" in error:
            logger.error("Gemini quota exceeded.")
            return None

        if "API_KEY_INVALID" in error:
            logger.error("Invalid Gemini API key.")
            return None

        logger.error("Gemini API error: %s", error)
        return None

    except Exception as e:
        logger.exception("Unexpected Gemini error")
    return None


def cached_generation(context: ArticleContext, feature: AIFeature, prompt: str, system_instruction: str, hash_input: str = "") -> Optional[str]:
    if context.source != "database" or not context.entry:
        return call_llm(prompt, system_instruction)
    content_to_hash = context.title if feature == AIFeature.RELATED else context.content
    prompt_hash = generate_hash(MODEL_NAME, feature.value, content_to_hash, prompt, hash_input)
    cached = AIResponse.objects.filter(article=context.entry, feature=feature.value, prompt_hash=prompt_hash).first()
    if cached:
        _set_generation_metadata(model=MODEL_NAME, elapsed=0.0, tokens=0, cached=True)
        logger.info("Cache hit for %s on %s", feature.value, context.title)
        return cached.response
    result = call_llm(prompt, system_instruction)
    if result and not result.startswith("⚠️"):
        AIResponse.objects.update_or_create(article=context.entry, feature=feature.value, prompt_hash=prompt_hash, defaults={"response": result})
    return result


def generate_feature(context: ArticleContext, feature: AIFeature, difficulty: str = "standard", **kwargs: Any) -> Optional[str]:

    if not context or (feature != AIFeature.RELATED and not context.content):
        return None
    if feature == AIFeature.CHAT and not kwargs.get("question"):
        return None
    difficulty = (difficulty or "standard").lower().strip()
    # content = truncate_content(context.content, FEATURE_LIMITS[feature]) if context.content else ""



    if feature == AIFeature.CHAT:

        content = extract_relevant_context(
            context.content,
            kwargs.get("question", "")
        )

    else:

        content = truncate_content(
            context.content,
            FEATURE_LIMITS[feature]
        )




    prompt = PROMPTS[feature].format(title=context.title, difficulty_guide=DIFFICULTY_DIRECTIVES.get(difficulty, DIFFICULTY_DIRECTIVES["standard"]), content=content, question=kwargs.get("question", ""))
    hash_input = kwargs.get("question", "") if feature == AIFeature.CHAT else difficulty
    return cached_generation(context, feature, prompt, SYSTEM_INSTRUCTIONS[feature], hash_input)


def generate_summary(context, difficulty="standard", **kwargs): 
    return generate_feature(context, AIFeature.SUMMARY, difficulty, **kwargs)

def explain_article(context, difficulty="standard", **kwargs): 
    return generate_feature(context, AIFeature.EXPLAIN, difficulty, **kwargs)

def generate_notes(context, difficulty="standard", **kwargs): 
    return generate_feature(context, AIFeature.NOTES, difficulty, **kwargs)

def generate_quiz(context, difficulty="standard", **kwargs): 
    return generate_feature(context, AIFeature.QUIZ, difficulty, **kwargs)

def generate_flashcards(context, difficulty="standard", **kwargs): 
    return generate_feature(context, AIFeature.FLASHCARDS, difficulty, **kwargs)

def generate_mindmap(context, difficulty="standard", **kwargs): 
    return generate_feature(context, AIFeature.MINDMAP, difficulty, **kwargs)



def chat_with_article(context, difficulty="standard", question="", **kwargs):
    return generate_feature(context, AIFeature.CHAT, difficulty, question=question, **kwargs)

def related_articles(context, difficulty="standard", **kwargs): 
    return generate_feature(context, AIFeature.RELATED, difficulty, **kwargs)


FEATURE_FUNCTIONS = {
    "summary": generate_summary,
    "explain": explain_article,
    "notes": generate_notes,
    "quiz": generate_quiz,
    "chat": chat_with_article,
    "related": related_articles,
    "flashcards": generate_flashcards,
    "mindmap": generate_mindmap,
}

