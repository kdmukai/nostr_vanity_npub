# Nostr Vanity `npub` Generator

Will brute-force search for a given `npub` target prefix:

```bash
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

## Search is exponential!
I can't do the probability math, but searching for a target string that's 6-chars long is exponentially harder than finding one that's 5-chars long. And then a target string that's 7-chars long is exponentially harder than 6. And so on.

At 8 or 9+ characters you're going to need a *considerable* amount of work to yield a match. Days? Weeks?

## Search is random!
You may have found a 5-character `npub` in 200s but the exact same 5-character target could take you 10x longer on the next run. It's just like bitcoin mining; the probabilities are one thing but there are no guarantees about your luck in any given run.

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

## Installation
Requires python3.6+

Clone this repo or just copy the [vanity_npub.py](vanity_npub.py) script to your machine.

Install [python-nostr](https://github.com/jeffthibault/python-nostr) dependency:
```
pip3 install python-nostr
```

## Performance
On an M1 Macbook Pro:
```
100.5s: Tried 1,000,000 npubs so far
200.9s: Tried 2,000,000 npubs so far
300.6s: Tried 3,000,000 npubs so far
400.8s: Tried 4,000,000 npubs so far
500.9s: Tried 5,000,000 npubs so far
```

## Valid npub/bech32 chars
```
023456789acdefghjklmnpqrstuvwxyz
```
