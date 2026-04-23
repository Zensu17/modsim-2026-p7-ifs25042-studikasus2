import json
import re


def parse_poem_response(result):
    try:
        content = result.get("response") if isinstance(result, dict) else result

        if isinstance(content, list):
            if not content:
                raise ValueError("Empty response from LLM")
            first_item = content[0]
            if isinstance(first_item, dict):
                content = (
                    first_item.get("generated_text")
                    or first_item.get("summary_text")
                    or first_item.get("text")
                    or first_item.get("content")
                    or first_item
                )

        if isinstance(content, dict):
            content = (
                content.get("generated_text")
                or content.get("response")
                or content.get("text")
                or content.get("content")
                or content
            )

        if not isinstance(content, str):
            content = json.dumps(content)

        content = content.strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content)

        parsed = json.loads(content)
        poem = parsed.get("poem", {})
        title = (poem.get("title") or "").strip()
        content_text = (poem.get("content") or "").strip()

        if not title or not content_text:
            raise ValueError("Poem title/content is missing")

        return {
            "title": title,
            "content": content_text,
        }

    except Exception as e:
        raise Exception(f"Invalid JSON from LLM: {str(e)}")