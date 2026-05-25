import json
from groq import Groq

SYSTEM_PROMPT = """
You are an advanced AI OS Agent running on Windows. Your job is to understand the user's request, identify the correct action, and respond helpfully.
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
    "thought": "Your internal reasoning about what the user wants and why you chose this action.",
    "action": "The action name (must be one of the available actions listed above)",
    "parameters": "Any relevant parameters extracted from the prompt (e.g., app name, file path, search query). Use empty string if none.",
    "response": "Your helpful response to the user explaining what you will do or answering their question."
}
"""

class AIOsAgent:
    """Core AI OS Agent that uses Groq LLM to identify actions and respond."""
    
    def __init__(self):
        self.client = Groq()
        self.model = "llama-3.3-70b-versatile"

    def chat(self, user_input: str) -> dict:
        """
        Sends the user input to the Groq LLM and returns a structured response
        with the identified action.
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
                return {"thought": "", "action": "GENERAL", "parameters": "", "response": "Something went wrong with the LLM output."}
            
            return {
                "thought": result.get("thought", ""),
                "action": result.get("action", "GENERAL"),
                "parameters": result.get("parameters", ""),
                "response": result.get("response", "")
            }

        except Exception as e:
            return {"thought": "", "action": "ERROR", "parameters": "", "response": f"Error: {e}"}
