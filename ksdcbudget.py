#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index
import math

class KsdcBudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

        self.spent = 0

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        # Calculate clicks in each position this round
        clicks_0 = round(30 * math.cos(math.pi * t / 24) + 50)
        clicks = []
        clicks.append(clicks_0)
        num_slots = len(history.round(t-1).clicks)
        for j in range(1, num_slots):
            clicks.append(clicks_0 * (0.75 ** j))

        # Fill in utilities
        utilities = []
        for j in range(0, num_slots):
            if j != num_slots - 1:
                second_highest_bid = history.round(t-1).bids[j+1][1]
                utilities.append(clicks[j] * (self.value - second_highest_bid))
            else:
                utilities.append(clicks[j] * (self.value - 0))
        
        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        # TODO: Fill this in.
        # Keep track of money spent
        if self.id in history.round(t-1).occupants:
            index = history.round(t-1).occupants.index(self.id)
            self.spent += history.round(t-1).bids[index+1][1]

        click_1 = round(30 * math.cos(math.pi * t / 24) + 50)
        if min_bid >= self.value:
            bid = self.value
        if slot == 0:
            bid = self.value
        else:
            click_j = click_1 * (0.75 ** slot)
            click_jminus = click_j / 0.75
            if self.spent >= 0.5 * self.budget and t <= 24:
                bid = 0
            elif t > 12 and t < 36:
                bid = min(1/50 * self.budget, self.value - ((click_j / click_jminus) * (self.value - min_bid)))
            else:
                bid = self.value - ((click_j / click_jminus) * (self.value - min_bid))        

        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


