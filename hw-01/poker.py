"""
Implement function best_hand, which takes poker hand of 7 cards
and returns the best (w.r.t. hand_rank) hand of 5 cards. Each
card has suit and rank.

Suits: (clubs, C), (spades, S), (hearts, H), (diamonds, D)
Ranks: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), (jack, J), (queen, Q), (king, K), (ace, A)

Examples:
	AS = ace of spades
	TH = ten of hearts
	3C = three of clubs

Problem
Implement function best_wild_hand, which takes as input hand of 7 cards
and returns best hand of 5 cards. A hand might include joker. Jokers can
replace card of any suit of the same color. The deck has 2 jokers. Black
joker '?B' can be used as club or spades of any rank, red joker '?R' can
be used as any of hearts and diamonds.
The first function has been implemented and signatures for others are given, 
itertools will be in hand, impelmentation of any auxulary functions are welcome.
"""

from collections import Counter
from itertools import combinations


rank2num = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                '8': 8, '9': 9, '10': 10, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}


def hand_rank(hand):
    """Return hand's value. """
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return 8, max(ranks)
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему""" 
    return sorted(map(lambda x: rank2num[x[0]], hand))


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    return all(map(lambda x: x[1] == hand[0][1], hand[1:]))


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    return all(map(lambda i: ranks[i] == ranks[i+1]-1, range(len(ranks))[:-1]))


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    cnt = Counter(ranks)
    if n not in cnt.values():
        return None
    ind = list(cnt.values()).index(n)
    return list(cnt.keys())[ind]


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    cnt = Counter(ranks)
    if sorted(cnt.values()) != [1, 2, 2]:
        return None
    items = sorted(cnt.items(), key=lambda x: -x[1])
    return items[0][0], items[1][0]


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    print("Best hand: ", hand)
    combs = list(combinations(hand, 5))
    values = list(map(hand_rank, combs))
    print("Combinations: ")
    for i in range(len(combs)):
        print(combs[i], values[i])
    print("Returning: ", max(combs, key=hand_rank))
    return max(combs, key=hand_rank) 


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    return


def test_best_hand():
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')

if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
