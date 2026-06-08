import os
import json
import re
from openai import OpenAI
from actions import ACTION_REGISTRY

SYSTEM_PROMPT = """
You are an advanced AI OS Agent running on a Windows PC. Your job is to understand the user's request, identify ALL the actions needed, and respond helpfully.
A user may request multiple tasks in a single message. You must identify each task separately.
You must always respond in valid JSON format.

Available Actions:
1. OPEN_APP       - User wants to open a local desktop application (e.g., notepad, calculator, paint, word).
2. OPEN_WEBSITE   - User wants to open a well-known website or web application in the browser. IMPORTANT: You must ONLY output a real, verified URL that you are 100% certain about (e.g., 'youtube.com', 'mail.google.com', 'instagram.com', 'github.com'). Do NOT predict, guess, or fabricate URLs. If you are NOT absolutely sure of the exact official URL, you MUST use SEARCH_WEB instead.
3. SEARCH_WEB     - User wants to search something on Google or the internet, OR you are unsure of the exact website URL.
4. SEARCH_FILE    - User wants to find or locate a file on their PC.
5. GENERAL        - User is just chatting, asking a general knowledge question, or the request doesn't fit any action above. Respond conversationally.

Your JSON response must have the following structure:
{
    "thought": "Your reasoning about the user's request and why you chose these actions.",
    "tasks": [
        {
            "action": "ACTION_NAME",
            "parameters": "The relevant parameter (app name, verified URL, search query, or file name). Use empty string if none."
        }
    ],
    "response": "Your helpful response to the user explaining what you will do."
}

IMPORTANT RULES:
- If the user asks for multiple things (e.g., "open notepad and calculator"), return multiple items in the "tasks" array.
- If the user asks for only one thing, return a single item in the "tasks" array.
- Always return at least one task.
- For OPEN_APP, the parameter should be just the app name (e.g., "notepad", "calculator").
- For OPEN_WEBSITE, the parameter MUST be a verified domain (e.g., "youtube.com"). Never guess.
- For SEARCH_WEB, the parameter is the search query string.
- For SEARCH_FILE, the parameter is the file name or keyword to search for.

"""

class AIOsAgent:
    """Core AI OS Agent that uses Nvidia LLM to identify and execute multiple tasks."""
    
    def __init__(self):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )
        self.model = "nvidia/llama-3.1-nemotron-nano-8b-v1"

    def chat(self, user_input: str) -> dict:
        """
        Sends the user input to the Nvidia LLM, identifies all tasks,
        executes each one, and returns the combined result.
        """
        try:
            print(f"1. Sending request to Nvidia API for: {user_input}")
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                model=self.model,
                temperature=0.6,
                top_p=0.95,
                max_tokens=4096
            )
            print("2. Received response from Nvidia!")
            
            response_text = response.choices[0].message.content

            # Strip markdown code fences if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # If the model added prose around the JSON, extract the JSON object
            if not response_text.startswith("{"):
                match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if match:
                    response_text = match.group()

            result = json.loads(response_text)
            
            if not isinstance(result, dict):
                return {
                    "thought": "",
                    "tasks": [{"action": "GENERAL", "parameters": "", "action_result": ""}],
                    "response": "Something went wrong with the LLM output."
                }
            
            tasks = result.get("tasks", [])
            print(f"3. Found {len(tasks)} tasks to execute.")
            
            # Execute each task and attach the result
            executed_tasks = []
            for i, task in enumerate(tasks):
                action = task.get("action") or "GENERAL"
                parameters = task.get("parameters") or ""
                
                print(f" -> Executing action: {action} | Params: {parameters}")
                action_result = self.execute_action(action, parameters)
                print(f" -> Finished action: {action}")
                
                executed_tasks.append({
                    "action": str(action),
                    "parameters": str(parameters),
                    "action_result": str(action_result)
                })
            
            return {
                "thought": result.get("thought", ""),
                "tasks": executed_tasks,
                "response": result.get("response", "")
            }

        except Exception as e:
            return {
                "thought": "",
                "tasks": [{"action": "ERROR", "parameters": "", "action_result": str(e)}],
                "response": f"Error: {e}"
            }

    def execute_action(self, action: str, parameters: str) -> str:
        """
        Looks up the action in the ACTION_REGISTRY and executes it.
        Returns the execution result or a message if no handler exists.
        """
        handler = ACTION_REGISTRY.get(action)
        
        if handler:
            return handler(parameters)
        
        # If the LLM picked an action we don't have a handler for
        if action not in ("GENERAL", "ERROR"):
            return f"Action '{action}' is not yet implemented."
        
        return ""
