from brain import Brain
from config import APP_NAME
from permissions import request_desktop_access
from voice_interface import VoiceInterface


def print_help():
    print("""
Commands:
  /help      Show this help
  /status    Show Kavshara status
  /remember  Save something to memory
  /voice     Listen to one voice command
  /access    Show desktop permission status
  /revoke    Revoke desktop access
  /exit      Quit Kavshara
""")


def main():
    brain = Brain()

    print(f"{APP_NAME} V1")
    print("Local-first AI assistant")
    print("Type /help for commands.\n")

    if not brain.provider.is_available():
        print("Warning: Ollama is not reachable.")
        print("Start Ollama, then run Kavshara again.\n")

    while True:
        try:
            user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command == "/access":
            from permissions import get_permissions
            print(get_permissions())
            continue

        if command == "/revoke":
            from permissions import revoke_desktop_access
            print(revoke_desktop_access())
            continue

        if command == "/voice":
            interface = VoiceInterface(brain)
            result = interface.voice_command(speak_response=True)
            if result.get("status") == "success":
                print("You (voice) > " + result["heard"])
                print("Kavshara > " + result["response"])
            else:
                print("Voice error > " + result.get("error", "No speech detected."))
            continue

        if command == "/exit":
            print("Goodbye.")
            break

        if command == "/help":
            print_help()
            continue

        if command == "/status":
            print(brain.status())
            continue

        if command.startswith("/remember "):
            print(brain.remember(user_input[len("/remember "):]))
            continue

        try:
            print(f"Kavshara > {brain.respond(user_input)}")
        except Exception as exc:
            print(f"Kavshara error > {exc}")


if __name__ == "__main__":
    main()
