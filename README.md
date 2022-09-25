# Humangram
Humangram is a social proof of humanity plugin for
[HUMAN protocol](https://www.humanprotocol.org/).
The idea behind it is "if someone has an active social
account for a few years, chances of that account being a
bot are less."

Humangram consists of a Telegram bot and an API. The
Telegram bot helps users prove their social activity on
Telegram messenger. The API helps smart contracts fight
bots by providing humanity score with time-based
signature as proof of source.

## Workflow
Here is an overall view of how Humangram works:

![workflow](images/workflow.jpg)
* User interacts with Telegram bot
* Telegram bot interacts with the database
* Token manager manages API access
* API reads data from the database
* Private key signs API responses to prove the source
* Contract reads signed data and can check authenticity

## Live Demo
Telegram bot: [@humangram_bot](https://t.me/humangram_bot)

API base address: https://humangram.ddns.net/

API master key: `blahblahblah`

API test token: `3w3uiejcv8buvrs8gj4s1qfpvkmkyd2c`

API public key:
```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBGMt4jUBEADZE6zBi8/BciTvzrXG3VCyC8IaBQaUnWgz4jT5S9yfj38yIGiR
kXGZTS3wK+BPzve2zgSTpmdO4njgLJsFNa4MgP0cKXvKUU/Lv/lliY+adiAOE+gb
wWFw8nB7ofIGwN/LOTezC3QQQ8k78nXZ2aZZBUkfwwjmDzkRJdqdvzoOejA7BUxt
znQ6e9kzNaZej2Ihx5QVH+TR1nIpAyPmu60+T05rPpF/IOZRl2b0nRKHB4lgybyB
TKXaqYe1Mq9KIEGyYcntEGGHwDb3ivV/fiU78nMGPcWPiXwT+xbgZttRwdB81gJU
ZB+4HUsc3bw1OnckuGIscpFwjJeaTJvGRR77i/BNZ72IYK2cAlNOl5u6yapdXz8A
etw2zVO0OF7650PusKOpIuPyC+FpiIbKXL3arV523yNib2gTPAYNlPuBfija4+pn
i0U9Kex+nI+D2CfQGYOjdn9qUnEgBjje8Pd1hKFdDcLeaP2CFXJSsS+aQAx8+/3K
Q7weirv6gui/PtMjHpqvzmXI8Rw23ZUWXq6k79u7iuG8WVXmY8pPaKt13a3R//Dp
ogcnVpggnRnGqVexQLYggXov8L7E+2eqFOBb8C6dJ2tcCuGa7i3XZwYa4nHVl3V7
5jYs7qs/5CwTGa2n1VmWUGubfkKQgeT8V8VG1OOkp5LOJGo17u35a3wd/wARAQAB
tCFIdW1hbmdyYW0gKHRlc3QpIDx0ZXN0QHRlc3QudGVzdD6JAkoEEwEIADQFAmMt
4jkCGw4ECwkIBwUVCAkKCwUWAgMBAAIeARYhBD/Aqum8bNwxceS8uoO9ZF8AZZtD
AAoJEIO9ZF8AZZtDknsP/0mbP4Bh64spykYgUvQdOVTGsOgxW7ys0/03tLj1vx3E
sDzZUL1Hur4+szGM/3ac3D3Uk2m+mRcThCN37XLKWd9x1S0k9QMYikzVHt6FKx3h
hGbCcYqYcmFRjOrBb+27Vl0Jg6ovXZONSH0fZBq3LD2s03aFqgnpXtai7h/HyMYP
A+mNHNeeVdm8DGj9JJvK1OeJRxzcHJao+4OsDH8Bk4KON7cSC+iGJyl68vDW20xy
PwyqngYMIAeLJf+ZoWIiU6vKVVkR8bp+VRpSGUhnevSXmCajohGMRcHLg7/q7o0W
IcOqjjNLkcrogg0xS/IPOx29RB6d4pNFqa/fYxFmP4wHLkGPHHBpzToik02ozD6j
HEwhGPDciXM/Bhj4CfFrlnupQyhbgl4NLMvVUwpCBVus01pibReigNkiyE/EdD4p
zyVC7vLR57v4FHNhEKo5bhb8eIeK9rWEDXczVSfYgR80phtVUD8mGOUzPxWVGIeG
mwj19ijT6zg6XLzRbrywjcmhUnjdkKF0/KPCZ/Nd3jExim5QXr241Bvzd0pU/8KX
+NDHpxeEiE3RwgB/EVtR5uR0v9E2xIjKtnkkqo95t55ng//XL5QnqIzCE/mWag36
e/qfIKsRGM1f4c0l6gHeXuj5ebJcDtnXzG/SMtxEe/oCXubn83Q/egllJkfjVU7W
=NIdU
-----END PGP PUBLIC KEY BLOCK-----
```

## Humanity Proof Score
Each user can earn humanity proof score by performing
several tasks. Currently, there are 4 optional tasks.
Scoring for each task can be modified in the config file.
Smart contracts and other verifiers may decide the
minimum acceptable score by themselves.

### Task 1 - Share phone number
By sharing their phone number, users get a one-time
score point set by `score_phone_number` in config file.
This task can be done only once by each user. Phone
numbers are not shared with verifiers.

Note that if a malicious user deletes his/her Telegram
account and signs up again in order to cheat, he/she 
can't get additional scores via sharing the same 
phone number.

### Task 2 - Forward an old message
Any user can forward a message which had been sent by
himself/herself in the past. The time of the original
message is read by the bot, and the user will receive
one score point for each `score_point_per_x_days` days
(configurable in the config file). 

Users can forward as many messages as they want to the bot.
Only the oldest message will earn them score points. The
time of the oldest message so far is saved, so if another
even older message is received in the future, the user
will only earn the difference.

### Task 3 - Proof of channel/supergroup ownership
If someone owns a popular channel/supergroup, chances of
him/her being a bot is less. Users can earn one score
point for each `score_point_per_x_members` members
(configurable in the config file). Only the admin of the
channel/supergroup can prove ownership. The minimum
recommended value for `score_point_per_x_members` is
201, because admins can add the first 200 members from
their contact list or by @usernames.

Note that each channel/supergroup can be used only once
and only by a single user. If a user has multiple
channels/supergroups, only the one with the highest
members count. The maximum members for each user is saved
and if a channel/supergroup with higher members is added
in the future, the user will only earn the difference.

### Task 4 - Getting vouched for humanity
Users can increase their score by asking other proved
humans to vouch for them. **When user A vouches for user
B, user A loses `score_voucher` score points, and user B
earns the same `score_voucher` score points.** The
amount for `score_voucher` is configurable in the config
file. This mechanism prevents the creation of vouching
clusters by malicious users.

Note than each user can vouch for each other user only
once and only if he/she can afford losing `score_voucher`
score points. Vouching requires explicit confirmation
by the voucher to prevent accidental clicks/taps.


## Quick Setup
Set up your own Humangram bot + API by following these
steps:

1) Go to [My Telegram](https://my.telegram.org/)
   and get a pair of `api_id` and `api_hash`.
2) Make a bot via [@BotFather](https://t.me/BotFather).
3) Make and activate a `venv` and install
   [requirements.txt](/requirements.txt).
4) Generate a private/public key pair (if you don't have
   one already) by issuing the command
   `python3 crypto.py <name> <email> <comment>`.
5) Rename [sample_config.py](/sample_config.py) to
   `config.py` and fill in the values.
6) Install **postgresql** and create `humangram` database.
7) Import [schema.sql](/schema.sql) to the database.
8) Run `python3 bot.py`.
9) Run `python3 api.py` in parallel (same `venv`).

## API Endpoints
Here is a list of API endpoints with live preview.

#### Get signed score:
`/get_score/<token>/<telegram_id>`
[[view online](https://humangram.ddns.net/get_score/3w3uiejcv8buvrs8gj4s1qfpvkmkyd2c/75149591)]

#### Get token quota:
`/get_quota/<token>`
[[view online](https://humangram.ddns.net/get_quota/3w3uiejcv8buvrs8gj4s1qfpvkmkyd2c)]

#### Generate a new token:
`/generate_token/<master_key>/<quota>`
[[view online](https://humangram.ddns.net/generate_token/blahblahblah/100)]

#### Add quota for a token:
`/add_quota/<master_key>/<token>/<quota>`
[[view online](https://humangram.ddns.net/add_quota/blahblahblah/3w3uiejcv8buvrs8gj4s1qfpvkmkyd2c/100)]

## Security Notes
* Run the API behind a reverse proxy such as Nginx using
a domain with SSL enabled. Without SSL, URLs will be sent
in plain text letting man in the middle steal tokens.
* Double-check permissions for the config file as it
contains your signing private key. The authenticity of
the whole system directly depends on that private key! 
