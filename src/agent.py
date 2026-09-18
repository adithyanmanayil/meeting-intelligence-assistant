from src.llm import generate
from src.prompts import RAG_PROMPT, EMAIL_PROMPT
from src.rag import MeetingRAG


class MeetingAgent:
    """Routes user requests to the appropriate meeting workflow."""

    def __init__(self):
        self.rag = MeetingRAG()

    def _route(self, request: str) -> str:
        text = request.lower()

        email_words = [
            "send email",
            "send an email",
            "email",
            "mail",
            "follow-up",
            "follow up",
        ]

        question_words = [
            "what",
            "who",
            "when",
            "where",
            "which",
            "how",
            "why",
        ]

        if any(word in text for word in email_words):
            return "email"

        if "?" in request or any(
            text.startswith(word + " ") for word in question_words
        ):
            return "question"

        return "ambiguous"

    def handle(self, request: str) -> dict:
        route = self._route(request)

        if route == "ambiguous":
            return {
                "type": "clarification",
                "response": (
                    "Could you clarify what you want to do? "
                    "You can ask a question about a meeting or "
                    "request a follow-up email."
                ),
            }

        results = self.rag.search(request, k=1)

        context = "\n\n".join(
            f"[Source: {result['source']}]\n{result['text']}"
            for result in results
        )

        if route == "question":
            prompt = RAG_PROMPT.format(
                context=context,
                question=request,
            )

            return {
                "type": "answer",
                "response": generate(prompt),
                "sources": [result["source"] for result in results],
            }

        prompt = EMAIL_PROMPT.format(
            context=context,
            request=request,
        )

        return {
            "type": "email",
            "response": generate(prompt),
            "sources": [result["source"] for result in results],
        }
