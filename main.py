from agent import AIOsAgent

def main():
    print("=======================================")
    print("       AI OS Agent - Initialized       ")
    print("=======================================")
    print("Type 'exit' or 'quit' to stop the agent.")
    print("Try typing something like 'open apps' to test the safety constraints.")
    
    agent = AIOsAgent()
    
    while True:
        try:
            user_input = input("\n[USER] > ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Shutting down AI OS Agent...")
                break
            
            if not user_input:
                continue
                
            agent.run_step(user_input)
            
        except KeyboardInterrupt:
            print("\nShutting down AI OS Agent...")
            break

if __name__ == "__main__":
    main()
