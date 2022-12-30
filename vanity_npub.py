"""
    Nostr vanity pubkey generator

    https://github.com/kdmukai/nostr_vanity_npub
"""
from threading import Event, Lock, Thread
from nostr.key import PrivateKey



class ThreadsafeCounter:
    """
        Copied from SeedSigner
    """
    def __init__(self, initial_value: int = 0):
        self.count = initial_value
        self._lock = Lock()
    
    @property
    def cur_count(self):
        # Reads don't require the lock
        return self.count

    def increment(self, step: int = 1):
        # Updates must be locked
        with self._lock:
            self.count += step
    
    def set_value(self, value: int):
        with self._lock:
            self.count = value



class BruteForceThread(Thread):
    def __init__(self, target: str, threadsafe_counter: ThreadsafeCounter, event: Event, include_end: bool = False):
        super().__init__(daemon=True)
        self.target = target
        self.threadsafe_counter = threadsafe_counter
        self.event = event
        self.include_end = include_end
        self.pk = None


    def run(self):
        i = 0
        while not self.event.is_set():
            i += 1
            pk = PrivateKey()
            npub = pk.public_key.bech32()[5:]   # Trim the "npub1" prefix

            if npub[:len(target)] != target and (include_end is False or (include_end and npub[-1*len(target):] != target)):
                if i % 1e5 == 0:
                    # Accumulate every 1e5...
                    self.threadsafe_counter.increment(1e5)
                    if self.threadsafe_counter.cur_count % 1e6 == 0:
                        # ...but update to stdout every 1e6
                        print(f"Tried {int(self.threadsafe_counter.cur_count):,} npubs so far", flush=True)
                continue
            
            print(f"\n{i:,} | {(time.time() - start):0.1f}s | npub1{npub}")
            self.pk = pk
            self.event.set()
            break



if __name__ == "__main__":
    import argparse
    import time
    from threading import Event
    from nostr import bech32


    parser = argparse.ArgumentParser(
        description="********************** Nostr vanity pubkey generator **********************\n\n" + \
            "Search for `target` in an npub such that:\n\n" + \
            "\tnpub1[target]acd023...",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Required positional arguments
    parser.add_argument('target', type=str,
                        help="The string you're looking for")

    # Optional arguments
    parser.add_argument('-e', '--include-end',
                        action="store_true",
                        default=False,
                        dest="include_end",
                        help="Also search the end of the npub")

    parser.add_argument('-j', '--jobs',
                    default=4,
                    type=int,
                    dest="num_jobs",
                    help="Number of threads (default: 4)")

    args = parser.parse_args()
    target = args.target.lower()
    include_end = args.include_end
    num_jobs = args.num_jobs

    for i in range(0, len(target)):
        if target[i] not in bech32.CHARSET:
            print(f"""ERROR: "{target[i]}" is not a valid character (not in the bech32 charset)""")
            print(f"""\tbech32 chars: {"".join(sorted(bech32.CHARSET))}""")
            exit()
    
    if len(target) >= 6:
        # 
        print(
            "This will probably take a LONG time!\n\n" + \
            "\tTip: CTRL-C to abort.\n\n"
        )

    start = time.time()
    threadsafe_counter = ThreadsafeCounter()
    event = Event()

    threads = []
    for i in range(0, num_jobs):
        brute_force_thread = BruteForceThread(target, threadsafe_counter=threadsafe_counter, event=event, include_end=include_end)
        brute_force_thread.start()
        threads.append(brute_force_thread)
    
    print(f"Initialized {num_jobs} threads")

    print("Working...")

    # Block until the first thread exits; after one thread finds a match, it will set the
    #   Event and all threads will exit.
    threads[0].join()            

    for thread in threads:
        if threads[i].pk is not None:
            print(f"""\n\t{"*"*76}\n\tPrivate key: {threads[i].pk.bech32()}\n\t{"*"*76}\n""")
            exit(0)
