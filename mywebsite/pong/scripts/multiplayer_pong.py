import json, time, threading

# TODO: Needs to be async so it doesn't interupt the whole server
def start_game():
    thread_id = threading.get_ident()
    print(f"[ID: {thread_id}] in start_game()")
    while True:
        print(f"[ID: {thread_id}] in game loop")
        time.sleep(1)
    return 