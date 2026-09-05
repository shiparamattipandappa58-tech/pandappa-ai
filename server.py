import ollama
import os
import sys
import time
import threading
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown

# Initialize Rich Console for Gemini/ChatGPT-style UI
console = Console()

MODEL_NAME = "Pandappa_AI"

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
            sys.exit()

    console.print("[bold green]✔ Engine Status: ONLINE (Max CPU Acceleration Enabled)[/bold green]\n")

    # System instruction & Conversation Memory Buffer
    messages = [
        {
            'role': 'system',
            'content': 'You are Pandappa AI, a real-time, highly intelligent AI assistant built to act like Gemini. You give ultra-fast, direct, accurate, and concise answers.'
        }
    ]

    while True:
        try:
            user_input = console.input("\n[bold green]You ➔ [/bold green]").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                console.print("\n[bold magenta]Pandappa AI:[bold magenta] Powering down. Have a great day!\n")
                break

            if user_input.lower() == "clear":
                display_header()
                continue

            if user_input.lower() == "reset":
                messages = [messages[0]]
                console.print("[yellow]System Memory Reset Done.[/yellow]")
                continue

            # Append User Message to Memory
            messages.append({'role': 'user', 'content': user_input})

            console.print("\n[bold magenta]Pandappa AI ➔ [/bold magenta]", end="")

            # Ultra-Fast Low Latency Streaming Call
            start_time = time.time()
            full_response = ""

            # Directly Stream Tokens from Local Memory Thread
            stream = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                stream=True,
                options={
                    "num_thread": 8,        # Uses all 8 CPU Cores of your Mobile
                    "temperature": 0.6,     # Fast token generation speed
                    "num_ctx": 2048         # Optimized Context Window for instant response
                }
            )

            for chunk in stream:
                token = chunk['message']['content']
                console.print(f"[cyan]{token}[/cyan]", end="", flush=True)
                full_response += token

            console.print("\n")
            
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
