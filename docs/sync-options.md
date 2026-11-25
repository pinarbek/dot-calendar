# Syncing notes across devices — the numbers

Researched 25 November 2026, for a decision that has not been taken. Nothing here is built.
Notes still live only on the device that wrote them, which is what the owner chose when the
project started: no accounts, no server, one link.

A live version of this analysis is at
https://claude.ai/code/artifact/052d83f2-d3bb-4a09-8fbd-f321930296d9

## The short answer

Money is not the obstacle. Up to 10,000 monthly active users the cost is zero; at 100,000
it is under five dollars a month. Sign-in is free at any size. What stands in the way is the
account requirement, the complexity, and becoming responsible for other people's data.

## Cost, per month

| Monthly active users | Reads | Writes | Storage | Database | Sign-in |
|---|---|---|---|---|---|
| 100 | 6,000 | 4,000 | 2 MB | free | $0 |
| 1,000 | 60,000 | 40,000 | 20 MB | free | $0 |
| 10,000 | 600,000 | 400,000 | 200 MB | free | $0 |
| 50,000 | 3,000,000 | 2,000,000 | 1 GB | $1.71 | $0 |
| 100,000 | 6,000,000 | 4,000,000 | 2 GB | $4.80 | $0 |

**Assumptions, which matter more than the prices.** A user opens the app 30 times a month,
each open reads 2 documents, they make 40 note edits a month and occupy 20 KB. Notes are
held **one document per user per month**. Store one document per note instead and reads go
up roughly 25-fold, and the table stops being true.

Free quota (Spark): 50,000 reads a day, 20,000 writes a day, 1 GiB stored, 10 GiB egress a
month. Beyond it: $0.03 per 100,000 reads, $0.09 per 100,000 writes, $0.15 per GiB stored,
$0.12 per GiB egress.

**The trap in the free plan:** exceeding the quota does not produce a bill, it **switches the
product off for the rest of the month**. At 10,000 users the write quota is already 67% used,
so anyone at that size needs the paid plan to avoid an outage — a few dollars, but a card on
file from then on.

**Sign-in is genuinely free.** The $0.0055 per user figure that circulates belongs to
*Firebase Authentication with Identity Platform*, which buys MFA, SAML, OIDC and an SLA.
This app needs none of them. Classic Firebase Auth, with Google and Apple sign-in, has no
user cap and no charge.

## Three routes

### A — As it stands

Notes stay on the device. Settings carries a backup code to copy and paste onto the other
device; `restore()` merges rather than overwriting. Costs nothing, works today, has to be
done by hand every time.

### B — A sync code, no accounts (recommended)

The app generates one long random code. Notes live under that code. Enter the same code on
another device and they appear there. No sign-in screen, no email, no personal data.

- The "one link, just open it" premise survives intact: for anyone who never enters a code,
  nothing changes.
- No authentication to write, which removes the largest piece of the work.
- Security rests on the code staying secret. Anyone holding it can read the notes. With a
  long enough code that is safe in practice, but it is not a password.
- Lose the code and the notes are unreachable. There is no recovery.

Three to four working rounds.

### C — Firebase with accounts

Sign in with Google or Apple. Notes attach to the account and appear on every device.
Recovery is possible. This is also the route that makes reminders fire with the app closed.

- Sign-in must stay **optional**, or the app stops being something you spread with a link.
- Notes leave the device. Today they go nowhere, and the README says so.
- Living in Spain, this brings GDPR duties: a privacy notice, deletion on request,
  responsibility as a data controller.

Six to seven working rounds, plus two if reminders should fire while the app is closed.

## What route C costs in work

| Piece | What it delivers | Rounds |
|---|---|---|
| Firebase setup, optional sign-in | Google/Apple sign-in, account UI, four languages | 1 |
| Sync layer | The 12 data sites and 11 save calls behind one layer | 2 |
| Conflict resolution | What happens when two devices edit one note; tombstones so a deleted note does not come back | 1 |
| First sign-in migration | Local notes to the cloud without duplicating them | 1 |
| Security rules, privacy notice | Nobody reads anyone else's notes; the GDPR text | 0.5 |
| Tests | Firebase emulator, so the 178 checks still mean something | 1 |
| *Reminders while closed* | *FCM, scheduler, timezones, device tokens* | *+2* |

A "round" is work finished, tested and deployed in one session — not a person-day. Route B
drops rows one, three and five, and shrinks row two.

## What either route breaks

- **The single-file rule ends.** CLAUDE.md requires `index.html` to stay dependency-free,
  with only Google Fonts loaded from outside. The Firebase SDK breaks that.
- **Notes leave the device.** The clearest promise the app makes today, written in the
  README, stops being true.
- **The tests go blind.** All 178 checks run in a real browser today. Sync cannot be tested
  without an emulator; skip that and the whole area is untested.
- **Offline plus sync is where the bugs live.** What happens to a note written on a plane
  when it meets an edit made elsewhere has to be decided, written down, and tested.

## Recommendation

**B.** It gives what is actually wanted — write on the phone, see it on the computer — while
keeping the two most valuable properties of the project: no accounts and no personal data.
No GDPR burden, no sign-in screen in anyone's way, and nothing to pay at this size.

Route C earns its cost only if one of three things becomes true: reminders must fire with
the app closed, users must be protected from losing their notes, or the app reaches a
serious number of people beyond the owner. None of those hold today.

Both routes start from the same first step — collecting the data layer into one place — so
beginning with B does not close the door on C.

## Sources

- https://firebase.google.com/pricing
- https://blog.logto.io/firebase-authentication-pricing
- https://supertokens.com/blog/firebase-pricing
