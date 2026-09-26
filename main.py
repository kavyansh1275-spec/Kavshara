from brain import Brain
from config import APP_NAME
from voice_interface import VoiceInterface


def print_help():
    print("""
Commands:
  /help      Show this help
  /status    Show Kavshara status
  /remember  Save something to memory
  /voice     Listen and reply by voice
  /access    Show desktop permission status
  /revoke    Revoke desktop access
  /exit      Quit Kavshara
""")


def main():
    brain = Brain()
    voice = VoiceInterface(brain)

    print(f"{APP_NAME} — Hinglish Voice + Coding Assistant")
    print("Bolo, type karo, ya /voice use karo. Main coding mein help karungi.")
    print("Type /help for commands.\n")

    if not brain.provider.is_available():
        print("Ollama reachable nahi hai. Ollama start karke Kavshara dobara run karo.\n")

    while True:
        try:
            user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye! Take care.")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command == "/voice":
            result = voice.voice_command(speak_response=True)
            if result.get("status") == "success":
                print("You (voice) > " + result["heard"])
                print("Kavshara > " + result["response"])
            else:
                print("Voice error > " + result.get("error", "No speech detected."))
            continue

        if command == "/access":
            from permissions import get_permissions
            print(get_permissions())
            continue

        if command == "/revoke":
            from permissions import revoke_desktop_access
            print(revoke_desktop_access())
            continue

        if command == "/exit":
            print("Bye! Take care.")
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
