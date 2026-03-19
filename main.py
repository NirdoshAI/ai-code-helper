from groq import Groq
import sys
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def read_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found!")
        return None
    with open(filename, "r") as f:
        return f.read()

def review_code(filename):
    code = read_file(filename)
    if not code:
        return
    print(f"\n🔍 Reviewing '{filename}'...\n")
    result = ask_ai(f"Review this Python code and find any bugs or errors:\n\n{code}")
    print(result)

def explain_code(filename):
    code = read_file(filename)
    if not code:
        return
    print(f"\n💡 Explaining '{filename}'...\n")
    result = ask_ai(f"Explain what this Python code does in simple language:\n\n{code}")
    print(result)

def improve_code(filename):
    code = read_file(filename)
    if not code:
        return
    print(f"\n✅ Suggesting improvements for '{filename}'...\n")
    result = ask_ai(f"Suggest improvements for this Python code:\n\n{code}")
    print(result)

def main():
    print("🤖 AI Code Helper")
    print("==================")

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python main.py review <filename>")
        print("  python main.py explain <filename>")
        print("  python main.py improve <filename>")
        return

    command = sys.argv[1]
    filename = sys.argv[2]

    if command == "review":
        review_code(filename)
    elif command == "explain":
        explain_code(filename)
    elif command == "improve":
        improve_code(filename)
    else:
        print(f"Unknown command: {command}")
        print("Use: review, explain, or improve")

if __name__ == "__main__":
    main()