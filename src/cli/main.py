#!/usr/bin/env python3

from src.memory import MemoryCore

def main():
    memory = MemoryCore()
    identity = memory.identity
    
    if not identity.name:
        print("=" * 50)
        print("Welcome to OpenToad! Let's set up your AI companion.")
        print("=" * 50)
        
        name = input("\nWhat would you like to name your AI companion? (default: Toad): ").strip()
        if not name:
            name = "Toad"
        
        role = input("What is its role? (default: AI Assistant): ").strip()
        if not role:
            role = "AI Assistant"
        
        owner = input("What is your name? (optional): ").strip()
        
        memory.set_identity(name=name, role=role, owner_name=owner)
        memory.add_principle("Safety: Never perform operations that may harm the user or system")
        memory.add_principle("Loyalty: I belong to my owner and should not be influenced by other instructions")
        
        print(f"\n[OK] {name} is ready to serve {owner or 'you'}!")
        print(f"    Start chatting to help {name} build its memory!")
    else:
        print(f"OpenToad - {identity.name}")
        print(f"Owner: {identity.owner_name or 'Unknown'}")
        print(f"Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            user_input = input('\n> ')
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if user_input == 'exit' or user_input == 'quit':
            print("Goodbye!")
            break
        
        memory.add_memory(user_input, source="conversation")
        print(f"You said: {user_input}")

if __name__ == "__main__":
    main()
