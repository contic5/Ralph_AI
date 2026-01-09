from google import genai
from pydantic import BaseModel, Field
from typing import Literal, Union

import os
from dotenv import load_dotenv
load_dotenv("generative_ai_keys.env")

gemini_key=os.getenv("gemini_key")
print(gemini_key)
client = genai.Client(api_key=gemini_key)


class SpamDetails(BaseModel):
    reason: str = Field(description="The reason why the content is considered spam.")
    spam_type: Literal["phishing", "scam", "unsolicited promotion", "other"]

class NotSpamDetails(BaseModel):
    summary: str = Field(description="A brief summary of the content.")
    is_safe: bool = Field(description="Whether the content is safe for all audiences.")

class ModerationResult(BaseModel):
    decision: Union[SpamDetails, NotSpamDetails]

interaction = client.interactions.create(
    model="gemini-3-flash-preview",
    input="Moderate the following content: 'Congratulations! You've won a free cruise. Click here to claim your prize: www.definitely-not-a-scam.com'",
    response_format=ModerationResult.model_json_schema(),
)

parsed_output = ModerationResult.model_validate_json(interaction.outputs[-1].text)
print(parsed_output)