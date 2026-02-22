def normalize_llm_content(content):
    """
    Ensures LLM content is always saved as a string.
    Handles Gemini multi-part responses safely.
    """

    if content is None:
        return ""

    if isinstance(content, str):
        return content

    # Gemini / LangChain tool blocks
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                texts.append(block["text"])
            else:
                texts.append(str(block))
        return "\n".join(texts)

    # Fallback
    return str(content)