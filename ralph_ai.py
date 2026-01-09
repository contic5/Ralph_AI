
from google import genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json
from typing import List, Optional

#Class that structures code feedback output
class GoalFeedback(BaseModel):
    goal:str=Field(description="What the goal is")
    meets_all_goals: bool=Field(description="Whether the code completes the goal or not.")
    reason: str = Field(description="Why the code completes the goal or not.")

class CodeFeedback(BaseModel):
    goals: List[GoalFeedback]

load_dotenv("generative_ai_keys.env")

#Access key from ENV file
gemini_key=os.getenv("gemini_key")
client = genai.Client(api_key=gemini_key)

max_attempts=2
code_output=""
meets_all_goals=False

output_file_type="py"
initial_query="Write a Python program that finds primes from 1 to 10000. Make sure the code uses simple math."

def main():
    #Program tries to solve a problem until it succeeds
    for attempt in range(1,max_attempts+1):
        print("Generating code to solve query...")
        print(initial_query)

        aided_query=initial_query
        #If past the first attempt, use previously generated code to solve the problem
        if attempt>1:
            with(open(f"code_output.{output_file_type}")) as code_support_file:
                aided_query+="\nImprove this code to solve the problem.\n"
                aided_query+=code_support_file.read()

        #Conversation used to generate code.
        code_generation_conversation_history=[]
        code_generation_conversation_history.append({"role": "model", "content": "You are a coding assistant. Only output code and do not output English explanations."})
        code_generation_conversation_history.append({"role":"user","content":aided_query})

        response = client.interactions.create(
            model="gemini-3-flash-preview",
            input=code_generation_conversation_history
        )
        code_output=response.outputs[-1].text
        code_output=code_output.replace("```python","")
        code_output=code_output.replace("```","")
        print(code_output)
        with(open(f"code_output.{output_file_type}","w")) as output_file:
            output_file.write(code_output)
        print("Checking if code works...")
        
        #Conversation used to check if code works. This conversation takes the query and the code and checks if the code solves the query.
        code_review_conversation_history=[]
        code_review_conversation_history.append({"role": "model", "content": "You are a coding reviewer. Verify if code works corectly or not and why."})
        code_review_conversation_history.append({"role":"user","content":f"Does the output correctly complete the query. Query:{initial_query} \n Output:{code_output}"})

        #Provide feedback with CodeFeedback model
        response = client.interactions.create(
            model="gemini-3-flash-preview",
            input=code_review_conversation_history,
            response_format=CodeFeedback.model_json_schema(),
        )
        json_response=json.loads(response.outputs[-1].text)
        print(json_response)

        
        meets_all_goals=True
        #If the code does not meet one of the goals, then try again.
        for goal in json_response["goals"]:
            if not goal["meets_all_goals"]:
                meets_all_goals=False
                break

        #If the code meets all goals, then exit the loop
        if meets_all_goals:
            print("Code works")
            meets_all_goals=True
            break
        #Otherwise, try again
        else:
            print("Code does not work")
        break

    if meets_all_goals:
        print("Solved Query",end="\n\n")
        print(f"Query: {initial_query}")
        print(f"Output: {code_output}")

        with(open(f"code_output_final.{output_file_type}","w")) as output_file:
            output_file.write(code_output)
    else:
        print("Failed to solve Query",end="\n\n")
        print(f"Query: {initial_query}")

if __name__=="__main__":
    main()