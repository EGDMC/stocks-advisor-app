import sys
import threading
import itertools
import time

class Spinner:
    """A simple spinner class for command line progress indication"""
    
    def __init__(self, message=""):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.stop_running = False
        self.spin_thread = None
        self.message = message

    def spin(self):
        while not self.stop_running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')

    def start(self):
        self.stop_running = False
        self.spin_thread = threading.Thread(target=self.spin)
        self.spin_thread.start()

    def stop(self):
        self.stop_running = True
        if self.spin_thread is not None:
            self.spin_thread.join()
        sys.stdout.write('\r')
        sys.stdout.flush()

def with_spinner(message="Loading..."):
    """Decorator to add a spinner to a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            spinner = Spinner(message)
            spinner.start()
            try:
                result = func(*args, **kwargs)
                spinner.stop()
                return result
            except Exception as e:
                spinner.stop()
                raise e
        return wrapper
    return decorator