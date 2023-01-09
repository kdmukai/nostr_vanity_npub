"""
    Nostr vanity pubkey generator

    https://github.com/kdmukai/nostr_vanity_npub
"""
import datetime
from threading import Event, Lock, Thread
from typing import List, Optional
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

class ThreadsafeFileOutput:
    def __init__(self, path: str):
        self.path = path
        self._lock = Lock()

    def write(self, output: str):
        with self._lock:
            with open(self.path, "a+") as file:
                file.write(output)

class BruteForceThread(Thread):
    def __init__(self, targets: List[str], bonus_targets: List[str], threadsafe_counter: Optional[ThreadsafeFileOutput], threadsafe_file_output: ThreadsafeFileOutput, event: Event, include_end: bool = False):
        super().__init__(daemon=True)
        self.targets = targets
        self.bonus_targets = bonus_targets
        self.threadsafe_counter = threadsafe_counter
        self.threadsafe_file_output = threadsafe_file_output
        self.event = event
        self.include_end = include_end

    def handle_match(self, target: str, private_key: PrivateKey):
        output = f"{target} | {int(self.threadsafe_counter.cur_count):,} | {(time.time() - start):0.1f}s\n{private_key.public_key.bech32()}\n{private_key.bech32()}\n"
        print(output, flush=True)
        if self.threadsafe_file_output:
            self.threadsafe_file_output.write(output)

    def run(self):
        i = 0
        while not self.event.is_set():
            i += 1
            pk = PrivateKey()
            npub = pk.public_key.bech32()[5:]   # Trim the "npub1" prefix

            # First check the bonus targets
            for target in self.bonus_targets:
                if npub[:len(target)] == target or (self.include_end and npub[-1*len(target):] == target):
                    # Found one of our bonus targets!
                    self.handle_match(target, pk)

            # Now check our main targets
            for target in self.targets:
                if npub[:len(target)] == target or (self.include_end and npub[-1*len(target):] == target):
                    # Found our match!
                    self.handle_match(target, pk)

                    # Set the shared Event to signal to the other threads to exit
                    self.event.set()
                    break

            # Nothing matched
            if i % 1e4 == 0:
                # Accumulate every 1e4...
                self.threadsafe_counter.increment(1e4)
                if self.threadsafe_counter.cur_count % 1e6 == 0:
                    # ...but update to stdout every 1e6
                    print(f"{str(datetime.datetime.now())}: Tried {int(self.threadsafe_counter.cur_count):,} npubs so far", flush=True)
            continue
            



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
    parser.add_argument('targets', type=str,
                        help="The string(s) you're looking for (comma-separated, no spaces)")

    # Optional arguments
    parser.add_argument('-b', '--bonus_targets',
                        default="",
                        dest="bonus_targets",
                        help="Additional targets to search for, but does not end execution when found (comma-separated, no spaces)")

    parser.add_argument('-e', '--include-end',
                        action="store_true",
                        default=False,
                        dest="include_end",
                        help="Also search the end of the npub")

    parser.add_argument('-j', '--jobs',
                    default=2,
                    type=int,
                    dest="num_jobs",
                    help="Number of threads (default: 2)")

    parser.add_argument('-o', '--output-file',
                    default=None,
                    dest="output_file",
                    help="Path to output file (default: None)")


    args = parser.parse_args()
    targets = args.targets.lower().split(",")
    bonus_targets = args.bonus_targets.lower().split(",") if args.bonus_targets else []
    include_end = args.include_end
    num_jobs = args.num_jobs
    output_file = args.output_file

    print(targets)
    print(bonus_targets)

    for target in targets + bonus_targets:
        for i in range(0, len(target)):
            if target[i] not in bech32.CHARSET:
                print(f"""ERROR: "{target[i]}" is not a valid character (not in the bech32 charset)""")
                print(f"""\tbech32 chars: {"".join(sorted(bech32.CHARSET))}""")
                exit()
    
    if max([len(t) for t in targets]) >= 6:
        print(
            "This will probably take a LONG time!\n\n" + \
            "\tTip: CTRL-C to abort.\n\n"
        )

    start = time.time()
    threadsafe_counter = ThreadsafeCounter()
    threadsafe_file_output = ThreadsafeFileOutput(output_file) if output_file is not None else None
    event = Event()

    threads = []
    for i in range(0, num_jobs):
        brute_force_thread = BruteForceThread(targets, bonus_targets, threadsafe_counter=threadsafe_counter, threadsafe_file_output=threadsafe_file_output, event=event, include_end=include_end)
        brute_force_thread.start()
        threads.append(brute_force_thread)
    
    print(f"Initialized {num_jobs} threads")

    print(f"{str(datetime.datetime.now())}: Starting")

    # Block until the first thread exits; after one thread finds a match, it will set the
    #   Event and all threads will exit.
    threads[0].join()            
