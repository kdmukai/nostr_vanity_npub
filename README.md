# Nostr Vanity `npub` Generator

Python-based brute-force search for a given vanity `npub` target.


## Example 1
```
python3 vanity_npub.py h0dl
```

Searches for an `npub` that starts with:

npub1 <b>h0dl</b> 023acd...

On success, it will print:
```
371,748 | 37.2s | npub1h0dl0dkjp884wz3wd30ucvfvdfvfdzp626hlvp68v0lfngnscdjsuy8yqm

        ****************************************************************************
        Private key: nsec1uu85rpk7sw2u2vrr6s9vlyvt4u58tcnluelm48a3fuytytvt4lnsa7pe0e
        ****************************************************************************
```

This reports the number of `npubs` it brute-force generated in order to find one with a matching prefix, the elapsed time in seconds, the successful `npub`, and its associated private key/`nsec`.


## Example 2
Search for "h0dl" at the beginning or the end of the `npub`:
```
python3 vanity_npub.py -e h0dl
> 1,026,042 | 103.0s | npub1y3ukxwznzysahdpnhrzgntal8kvmmd7uhx3k6klzzvaemm6nmwdse9h0dl
```

## Example 3
Search for "h0dl" or "sat0shi":
```
# Exits on whichever one it finds first
python3 vanity_npub.py h0dl,sat0shi
```

## Example 4
Spend a lot of time searching for "nakam0t0", but along the way note any "h0dler" or "h0rnet" bonus matches:
```
python3 vanity_npub.py nakam0t0 -b h0dler,h0rnet
```

## Usage
```
usage: vanity_npub.py [-h] [-b BONUS_TARGETS] [-e] [-j NUM_JOBS] targets

********************** Nostr vanity pubkey generator **********************

Search for `target` in an npub such that:

        npub1[target]acd023...

positional arguments:
  targets               The string(s) you're looking for (comma-separated, no spaces)

optional arguments:
  -h, --help            show this help message and exit
  -b BONUS_TARGETS, --bonus_targets BONUS_TARGETS
                        Additional targets to search for, but does not end execution when found (comma-separated, no spaces)
  -e, --include-end     Also search the end of the npub
  -j NUM_JOBS, --jobs NUM_JOBS
                        Number of threads (default: 2)
```

## Limitations
`npub`s can only include characters from the bech32 list:
```
023456789acdefghjklmnpqrstuvwxyz
```

You'll get an error if you enter a vanity target that includes an unsupported character.
```
python vanity_npub.py bitcoin
> ERROR: "b" is not a valid character (not in the bech32 charset)
>         bech32 chars: 023456789acdefghjklmnpqrstuvwxyz
```

---


## Search is exponential!
I can't do the probability math, but searching for a target string that's 6-chars long is exponentially harder than finding one that's 5-chars long. And then a target string that's 7-chars long is exponentially harder than 6. And so on.

At 8 or 9+ characters you're going to need a *considerable* amount of work to yield a match. Days? Weeks?


## Search is random!
You may have found a 5-character `npub` in 200s but the exact same 5-character target could take you 10x longer on the next run. It's just like bitcoin mining; the probabilities are one thing but there are no guarantees about your luck in any given run.

Also note that you can stop a vanity `npub` search and restart it later. You're not wasting any work; it'll just keep searching new random `npub`s when you resume.


## Performance
A 5-char vanity target could easily take tens of millions of tries. The script outputs an update at each million `npub`s tried so you can get a sense of what your brute force speed is like.

It's also to your advantage to add additional `targets` or `bonus_targets`. Each extra term only adds minimal additional effort; you're already doing the work to generate a random `npub` so you may as well check it for more than one possible match.

The biggest speed gain is to just open multiple terminal sessions and run an instance of `vanity_npub.py` in each one. Each instance will add more burden on the CPU but they don't seem to impact each others' performance much, as long as your CPU isn't completely slammed.

The built-in attempt to leverage multithreading using the `-j` command line option yielded only modest gains. Perhaps future improvements could make this more effective.

M1 Macbook Pro showed no benefit from multithreading (j=1 or j=2) at around 104s/mil tries. Slowed down beyond j=2.
```
# -j 1 or -j 2
1876.9s: Tried 18,000,000 npubs so far
1981.2s: Tried 19,000,000 npubs so far (105s / mil)
2085.5s: Tried 20,000,000 npubs so far (104s / mil)
2189.9s: Tried 21,000,000 npubs so far (104s / mil)
```

An older 8-core Ryzen 7 ran slightly faster at j=2 at around 160s/mil. Slowed down beyond j=2.



## Is this secure?
Quick version: No, you shouldn't blindly trust any private key generator you found online.

Long version: Assuming the pk calcs are trustworthy, it won't matter if two people search for the same vanity prefix. For example:

```
python3 vanity_npub.py hfsp
> 365,386 | 36.3s | npub1hfspw0hcddc9k058ap4frvsexlykqzw3k2cun9430hxdvg8z9evqp5wfc8
>
>         ****************************************************************************
>         Private key: nsec1d7smkrh9z8pn28lv6vm5ad736ms44wx84z405hsph6q7v3vqju0qqum9ak
>         ****************************************************************************

python3 vanity_npub.py hfsp
> 792,574 | 80.0s | npub1hfsp4ue6z0ykvjg99df6s2nvw7xzw9677wx70ydhdqegatf0qkcs4yqht7
>
>         ****************************************************************************
>         Private key: nsec1949kx7knea9tcug9906u0l787vkxuha0yymh0vuu9x8xqmqvalaqk6lutn
>         ****************************************************************************
```

The `npub` is 58-characters long (not including the "npub1" prefix). That is more than enough randomness to make it effectively impossible for any two people to yield the exact same complete `npub` when searching for the same vanity prefix.

---

## Installation
Requires:
* python3.6+
* git

Clone this repo:
```
git clone https://github.com/kdmukai/nostr_vanity_npub.git
cd nostr_vanity_npub
```

Clone the [python-nostr](https://github.com/jeffthibault/python-nostr) dependency:
```
git clone https://github.com/jeffthibault/python-nostr.git
pip install -e python-nostr
```
