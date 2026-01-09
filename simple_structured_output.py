
from google import genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json

class CodeFeedback(BaseModel):
    success: bool=Field(description="Whether the code works correctly or not.")
    reason: str = Field(description="Why the code works correctly or not.")

load_dotenv("generative_ai_keys.env")

gemini_key=os.getenv("gemini_key")
print(gemini_key)
client = genai.Client(api_key=gemini_key)

#https://jpcaparas.medium.com/ralph-wiggum-explained-the-claude-code-loop-that-keeps-going-3250dcc30809

def main():
    code_review_conversation_history=[]
    code_review_conversation_history.append({"role": "model", "content": "You are a coding reviewer. Verify if code works corectly or not and why."})
    code_review_conversation_history.append({"role":"user","content":f"Does this Python Code work correctly: System.out.println('Hello World);"})

    response = client.interactions.create(
        model="gemini-3-flash-preview",
        input=code_review_conversation_history,
        response_format=CodeFeedback.model_json_schema(),
    )

    json_response=json.loads(response.outputs[-1].text)
    print(json_response)

if __name__=="__main__":
    main()