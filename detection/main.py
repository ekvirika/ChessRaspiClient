import threading
from lichess_handling import Lichess
from move_detection import MD
import queue


def main():
    bq = queue.Queue()
    lichess_instance = Lichess( bq)  # Pass the lock and queue to Lichess
    md_instance = MD(bq)
    # Create threads for Lichess and Move Detection
    lichess_thread = threading.Thread(target=lichess_instance.run_lichess_handling)
    move_detection_thread = threading.Thread(target=md_instance.run_move_detection)

    # Start both threads
    lichess_thread.start()
    move_detection_thread.start()

    # Optional: Join threads to ensure they run concurrently
    lichess_thread.join()
    move_detection_thread.join()
    

if __name__ == "__main__":
    main()
