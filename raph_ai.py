
from google import genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json

#Class that structures code feedback output
class CodeFeedback(BaseModel):
    success: bool=Field(description="Whether the code works correctly or not.")
    reason: str = Field(description="Why the code works correctly or not.")

load_dotenv("generative_ai_keys.env")

#Access key from ENV file
gemini_key=os.getenv("gemini_key")
client = genai.Client(api_key=gemini_key)

max_attempts=2
query="Write a Python for loop that goes from 99 to 0 and prints out each odd number."
query="Write a JavaScript program that effeciently finds primes from 1 to 10000"
code_output=""
success=False

def main():
    #Program tries to solve a problem until it succeeds
    for attempt in range(1,max_attempts+1):
        print("Generating code to solve query...")
        print(query)

        #Conversation used to generate code
        code_generation_conversation_history=[]
        code_generation_conversation_history.append({"role": "model", "content": "You are a coding assistant. Only output code and do not output English explanations."})
        code_generation_conversation_history.append({"role":"user","content":query})

        response = client.interactions.create(
            model="gemini-3-flash-preview",
            input=code_generation_conversation_history
        )
        code_output=response.outputs[-1].text
        print(code_output)
        print("Checking if code works...")
        
        #Conversation used to check if code works. This conversation takes the query and the code and checks if the code solves the query.

        code_review_conversation_history=[]
        code_review_conversation_history.append({"role": "model", "content": "You are a coding reviewer. Verify if code works corectly or not and why."})
        code_review_conversation_history.append({"role":"user","content":f"Does the output correctly complete the query. Query:{query} \n Output:{code_output}"})
        print(code_review_conversation_history)

        #Provide feedback with CodeFeedback model
        response = client.interactions.create(
            model="gemini-3-flash-preview",
            input=code_review_conversation_history,
            response_format=CodeFeedback.model_json_schema(),
        )
        json_response=json.loads(response.outputs[-1].text)
        print(json_response)

        #If the code works, then exit the loop
        if json_response["success"]==True:
            print("Code works")
            success=True
            break
        #Otherwise, try again
        else:
            print("Code does not work")
        break

    if success:
        print("Solved Query",end="\n\n")
        print(f"Query: {query}")
        print(f"Output: {code_output}")
    else:
        print("Failed to solve Query",end="\n\n")
        print(f"Query: {query}")

if __name__=="__main__":
    main()