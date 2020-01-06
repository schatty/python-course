#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------

from itertools import product, combinations
from collections import Counter


def hand_rank(hand):
    """Returns numeric value of the hand. """
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
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


def get_suite(card):
    """Get suite from card. """
    return card[1]


def get_rank(card):
    """Get numeric value of the card. """
    r = card[0]
    d = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
    if r in "TJQKA":
        return d[r]
    return int(r)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    return sorted([get_rank(c) for c in hand], reverse=True)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suite = get_suite(hand[0])
    return sum([get_suite(c) == suite for c in hand]) == len(hand)


def straight(ranks, k=5):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    def pair(c1, c2):
        if (c2 - c1) == 1:
            return '1'
        return '0'

    neighbours = ''.join([pair(ranks[i], ranks[i+1]) for i in range(len(ranks)-1)])
    return neighbours.find("1"*k) != -1    


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    cnt = Counter(ranks)
    best_rank = 0
    for k, v in cnt.items():
        if v ==  n and k > best_rank:
            best_rank = k
    return best_rank


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    cnt_ranks = Counter(ranks)
    cnt_repeats = Counter(cnt_ranks.values())
    if not (2 in cnt_repeats.keys()):
        return None
    return [r for r in cnt_ranks if cnt_ranks[r] == 2]


def compare_rank_info(info, best_rank):
    """Returns True if info is better than best_rank. """
    if best_rank is None:
        return True
    # If got two flushes pick one with straight property
    if info[0] == best_rank[0] == 5:
        return straight(info[1], 4) and not  straight(best_rank[1], 4)
    elif info[0] == best_rank[0] == 6:
        if info[1] > best_rank[1]:
            return True
        elif info[1] == best_rank[1]:
           return info[2] > best_rank[2]
    # In case of Kind select one with the highest ranks
    elif info[0] == best_rank[0] == 7:
        if sum(info[1:]) > sum(best_rank[1:]):
            return True
    return info[0] > best_rank[0]


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    best_rank = None
    bhand = None
    for hand5 in combinations(hand, 5):
        rank_info = hand_rank(hand5)
        if compare_rank_info(rank_info, best_rank):
            best_rank = rank_info
            bhand = hand5
    return bhand


def hand_options(hand, joker):
    if joker not in hand:
        return []
    ranks = list(map(str, range(2, 10))) + ['T', 'J', 'Q', 'K', 'A']
    suites = ['C', 'S'] if joker == '?B' else ['H', 'W']
    joker_replacements = list(map(lambda x: ''.join(x), product(ranks, suites)))
    hands = []
    for wildcard in joker_replacements:
        if wildcard not in hand:
            new_hand = hand[:]
            new_hand.remove(joker)
            new_hand.append(wildcard)
            hands.append(new_hand)
    return hands


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    if "?B" in hand and "?R" in hand:
        hands = []
        hands_b = hand_options(hand, '?B')
        for hb in hands_b:
            hands += hand_options(hb, '?R')
    elif "?B" in hand:
        hands = hand_options(hand, '?B')
    elif "?R" in hand:
        hands = hand_options(hand, '?R') 
    else:
        return best_hand(hand)

    # The same logic but on all joker-hands
    best_rank = None
    bhand = None
    for hand in hands:
        for hand5 in combinations(hand, 5):
            rank_info = hand_rank(hand5)
            if compare_rank_info(rank_info, best_rank):
                best_rank = rank_info
                bhand = hand5
    return bhand
    

def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
