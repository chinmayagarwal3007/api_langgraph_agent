import google.generativeai as genai

genai.configure()

model = genai.GenerativeModel("gemini-2.5-flash")


async def generate(prompt: str) -> str:
    # Gemini SDK is sync → run in thread
    import asyncio
    loop = asyncio.get_running_loop()

    def _call():
        return model.generate_content(prompt).text

    return await loop.run_in_executor(None, _call)
