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
from itertools import combinations, product


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
	"""Return list of ranks (numerical value) sorted 
	in increasing order.""" 
	return sorted(map(lambda x: rank2num[x[0]], hand))

def flush(hand):
	"""Return True if all the cards are of the same kind."""
	return all(map(lambda x: x[1] == hand[0][1], hand[1:]))


def straight(ranks):
	"""Return True if sorted ranks create a sequence of 5 cards 
	in increasing order  (strit)""" 
	return all(map(lambda i: ranks[i] == ranks[i+1]-1, range(len(ranks))[:-1]))


def kind(n, ranks):
	"""Return the first tank that appears in a hand n times. 
	Return None if such a rank does not exist."""
	cnt = Counter(ranks)
	if n not in cnt.values():
		return None
	ind = list(cnt.values()).index(n)
	return list(cnt.keys())[ind]


def two_pair(ranks):
	"""Return two ranks from existing pair, in case if pair doest not 
	exist return None"""
	cnt = Counter(ranks)
	if sorted(cnt.values()) != [1, 2, 2]:
		return None
	items = sorted(cnt.items(), key=lambda x: -x[1])
	return items[0][0], items[1][0]


def best_hand(hand):
    """From 7-hand return the best 5-hand. """
    combs = list(combinations(hand, 5))
    values = list(map(hand_rank, combs))
    return max(combs, key=hand_rank) 


def best_wild_hand(hand):
	"""best_hand but with jokers"""
	def get_joker_options(card):
		if card == '?B':
			return ['2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'TC', 'JC', 'QC', 'KC', 'AC', 
					'2S' ,'3S', '4S', '5S', '6S', '7S', '8S', '9S', 'TS', 'JS', 'QS', 'KS', 'AS']
		elif card == '?R':
			return ['2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', 'TH', 'JH', 'QH', 'KH', 'AH',
					'2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', 'TD', 'JD', 'QD', 'KD', 'AD']

	joker_cards = None	
	if '?B' in hand and '?R' in hand:
		hand.remove('?B')
		hand.remove('?R')
		joker_cards = list(product(get_joker_options('?B'), get_joker_options('?R')))
	if '?B' in hand:
		hand.remove('?B')
		joker_cards = [[x] for x in get_joker_options('?B')] 
	if '?R' in hand:
		hand.remove('?R')
		joker_cards = get_joker_options('?R')
	if joker_cards is None:
		return best_hand(hand)

	best_val = (0, 0)
	best_option = None
	for joker_option in joker_cards:
		bhand = best_hand( hand + list(joker_option))
		rank = hand_rank(bhand)
		if rank > best_val:
			best_val = rank
			best_option = bhand

	return best_option
	


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
	assert (hand_rank(sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split())))
		== hand_rank(['7C', 'TC', 'TD', 'TH', 'TS']))
	assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
		== ['7C', '7D', '7H', '7S', 'JD'])
	print('OK')

if __name__ == '__main__':
	test_best_hand()
	test_best_wild_hand()
