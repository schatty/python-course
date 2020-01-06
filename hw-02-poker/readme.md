## Poker

Implement `best_hand` function that takes poker hand
from 7 cards and returns the best (regarding to the
numeric value from `hand_rank`) hand of 5 cards. Each
card has a suit and a rank.
Suits: (clubs, C), (spades, S), (hearts, H), (diamonds, D)
Ranks: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), jack (J),
       queen (Q), king (K), ace (A)
Example: AS (ace of spades), TH (ten of hearts), 3C (three of clubs)

__Excercise with a *__

Implmement funtion `best_wild_hand`, that takes poker hand
from 7 cards and returns the best (regarding to the
numeric value from hand rank) hand of 5 cards. In this
excercise hand may include joker. Jokers can replace
card with any suite with corresponding color. The deck
has two jokers. Black jocker '?B' can be used as clubs
and spades of any rank, red joker '?R' as any hearts or
diamonds of any rank.
