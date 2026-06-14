import os
from google import genai
from google.genai import types

def generate_text_with_gemini(prompt: str, api_key: str = None) -> str:
    """
    最新の google-genai SDK を使用して Gemini モデルでテキストを生成します。
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is not set in environment or arguments.")

    client = genai.Client(api_key=key)
    
    # ユーザー指定の最新モデルを使用 (gemini-flash-latest または gemini-2.5-flash 等)
    model = "gemini-flash-latest"
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    # 必要に応じて Google 検索グラウンディングなどのツールを追加可能
    tools = [
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
        ),
        tools=tools,
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            response_text += text
            
    return response_text
