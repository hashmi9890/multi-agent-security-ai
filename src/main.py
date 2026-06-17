from src.workflows.basic_workflow import run_research_workflow
from src.persistent_memory import PersistentMemory


memory = PersistentMemory()


def main():
    print("=== Multi-Agent Security System (Persistent Memory Enabled) ===")
    print("Type 'exit' to quit.")
    print("Type 'reset' to clear memory.\n")

    while True:
        user_input = input("User > ")

        if user_input.lower() == "exit":
            break

        if user_input.lower() == "reset":
            memory.clear()
            print("✅ Memory cleared.\n")
            continue

        result = run_research_workflow(user_input)

        print("\nResult:\n")
        print(result)
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()