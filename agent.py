import json
import time
from groq import Groq
from actions import ACTION_REGISTRY

SYSTEM_PROMPT = """
You are an advanced AI OS Agent running on Windows. Your job is to understand the user's request, identify ALL the actions needed, and respond helpfully.
A user may request multiple tasks in a single message. You must identify each task separately.
You must always respond in valid JSON format.

Available Actions:
1. OPEN_APP       - User wants to open an application (e.g., notepad, chrome, calculator).
2. SEARCH_WEB     - User wants to search something on Google or the internet.
3. SEARCH_FILE    - User wants to find/locate a file on their local system.
4. CREATE_FILE    - User wants to create a new file.
5. READ_FILE      - User wants to read the contents of a file.
6. WRITE_FILE     - User wants to write or append data to a file.
7. DELETE_FILE    - User wants to delete or remove a file.
8. ACCESS_CODE    - User wants to read, summarize, or understand an existing codebase.
9. DEBUG_CODE     - User wants to debug or fix errors in a script.
10. WRITE_CODE    - User wants to generate or write new code.
11. GENERAL       - User is just chatting, asking a general question, or the request doesn't fit any action above.

Your JSON response must have the following structure:
{
    "thought": "Your overall reasoning about the user's request.",
    "tasks": [
        {
            "action": "The action name (must be one of the available actions)",
            "parameters": "Relevant parameters for this specific task (e.g., app name, file path). Use empty string if none."
        }
    ],
    "response": "Your helpful response to the user explaining what you will do."
}

IMPORTANT RULES:
- If the user asks for multiple things (e.g., "open notepad and calculator"), return multiple items in the "tasks" array.
- If the user asks for only one thing, return a single item in the "tasks" array.
- Always return at least one task.
"""

class AIOsAgent:
    """Core AI OS Agent that uses Groq LLM to identify and execute multiple tasks."""
    
    def __init__(self):
        self.client = Groq()
        self.model = "llama-3.3-70b-versatile"

    def chat(self, user_input: str) -> dict:
        """
        Sends the user input to the Groq LLM, identifies all tasks,
        executes each one, and returns the combined result.
        """
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            
            if not isinstance(result, dict):
                return {
                    "thought": "",
                    "tasks": [{"action": "GENERAL", "parameters": "", "action_result": ""}],
                    "response": "Something went wrong with the LLM output."
                }
            
            tasks = result.get("tasks", [])
            
            # Execute each task and attach the result
            executed_tasks = []
            for task in tasks:
                action = task.get("action", "GENERAL")
                parameters = task.get("parameters", "")
                action_result = self.execute_action(action, parameters)
                executed_tasks.append({
                    "action": action,
                    "parameters": parameters,
                    "action_result": action_result
                })
                time.sleep(2)
            
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
        Returns the execution result or empty string if no handler is found.
        """
        handler = ACTION_REGISTRY.get(action)
        
        if handler:
            return handler(parameters)
        
        return ""
