"""
    Nostr vanity pubkey generator

    https://github.com/kdmukai/nostr_vanity_npub
"""
import time
from nostr.key import PrivateKey


def find_vanity_npub(target: str):
    start = time.time()
    i = 0
    while True:
        i += 1
        pk = PrivateKey()
        npub = pk.public_key.bech32()[5:]   # Trim the "npub1" prefix

        if npub[:len(target)] != target:
            if i % 1e6 == 0:
                print(f"{(time.time() - start):0.1f}s: Tried {i:,} npubs so far")
            continue
        
        print(f"\n{i:,} | {(time.time() - start):0.1f}s | npub1{npub}")
        break
    return pk



if __name__ == "__main__":
    import argparse
    from nostr import bech32
    parser = argparse.ArgumentParser(
        description="********************** Nostr vanity pubkey generator **********************\n\n" + \
            "Search for `target_string` such that:\n\n" + \
            "\tnpub1[target_string]abc123...",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Required positional arguments
    parser.add_argument('target', type=str,
                        help="The string you're looking for")

    args = parser.parse_args()
    target = args.target.lower()

    for i in range(0, len(target)):
        if target[i] not in bech32.CHARSET:
            print(f"""ERROR: "{target[i]}" is not a valid character (not in the bech32 charset)""")
            print(f"""\tbech32 chars: {"".join(sorted(bech32.CHARSET))}""")
            exit()
    
    if len(target) > 6:
        # 
        print(
            "This will probably take a LONG time!\n\n" + \
            "\tTip: CTRL-C to abort.\n\n" + \
            "Working..."
        )

    pk = find_vanity_npub(target)
    print(f"""\n\t{"*"*76}\n\tPrivate key: {pk.bech32()}\n\t{"*"*76}\n""")
