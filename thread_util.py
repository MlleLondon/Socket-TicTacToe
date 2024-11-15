import threading

def create_thread(target):
    """
    Crée un thread pour exécuter une fonction donnée.

    :param target: La fonction à exécuter dans le thread.
    """
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
