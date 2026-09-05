import os
import sys
import time
import ollama
from rich.console import Console

# Initialize Rich Console
console = Console()

MODEL_NAME = "Pandappa_AI"
SYSTEM_PROMPT = {
    'role': 'system',
    'content': 'You are Pandappa AI, a real-time, highly intelligent AI assistant built to act like Gemini. You give ultra-fast, direct, accurate, and concise answers.'
}

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_header():
    clear_screen()
    banner = """
    [bold cyan]============================================================[/bold cyan]
    [bold magenta]                  P A N D A P P A   A I                  [/bold magenta]
    [bold yellow]       Real-Time Ultra-Fast Local Engine (Offline)          [/bold yellow]
    [bold cyan]============================================================[/bold cyan]
    [dim]Commands: 'exit' to quit | 'clear' to reset screen | 'reset' to clear memory[/dim]
    """
    console.print(banner)

def check_engine():
    """Checks if local Ollama server is active"""
    try:
        ollama.list()
        return True
    except Exception:
        return False

def fast_chat_engine():
    display_header()

    with console.status("[bold green]Starting Pandappa AI Neural Engine...", spinner="dots"):
        time.sleep(0.5)
        if not check_engine():
            console.print("\n[bold red][ERROR] Pandappa AI Engine is Offline![/bold red]")
            console.print("[yellow]Run 'ollama serve &' in Termux before launching.[/yellow]\n")
            sys.exit(1)

    console.print("[bold green]✔ Engine Status: ONLINE (Max CPU Acceleration Enabled)[/bold green]\n")

    # Conversation Memory Buffer
    messages = [SYSTEM_PROMPT.copy()]

    while True:
        try:
            user_input = console.input("\n[bold green]You ➔ [/bold green]").strip()

            if not user_input:
                continue

            command = user_input.lower()

            if command in ["exit", "quit"]:
                console.print("\n[bold magenta]Pandappa AI:[/bold magenta] Powering down. Have a great day!\n")
                break

            if command == "clear":
                display_header()
                continue

            if command == "reset":
                messages = [SYSTEM_PROMPT.copy()]
                console.print("[yellow]System Memory Reset Done.[/yellow]")
                continue

            # Append User Message to Memory
            messages.append({'role': 'user', 'content': user_input})

            console.print("\n[bold magenta]Pandappa AI ➔ [/bold magenta]", end="")

            # Stream response
            full_response = ""
            
            stream = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                stream=True,
                options={
                    "num_thread": 8,        # Uses CPU cores
                    "temperature": 0.6,     # Fast generation balance
                    "num_ctx": 2048         # Context window size
                }
            )

            # Direct terminal output to avoid Rich tag parsing bugs on token chunks
            for chunk in stream:
                # Support both dict and object access across different `ollama` library versions
                token = chunk.get('message', {}).get('content', '') if isinstance(chunk, dict) else chunk.message.content
                sys.stdout.write(token)
                sys.stdout.flush()
                full_response += token

            sys.stdout.write("\n")
            sys.stdout.flush()

            # Save AI Response to Context History
            messages.append({'role': 'assistant', 'content': full_response})

        except KeyboardInterrupt:
            console.print("\n\n[bold red]Session interrupted safely.[/bold red]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Engine Error: {e}[/bold red]\n")
            break

if __name__ == "__main__":
    fast_chat_engine()
