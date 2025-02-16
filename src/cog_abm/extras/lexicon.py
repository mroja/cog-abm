import random

from tools import *
from itertools import groupby
from collections import deque


class Syllable:
	
	allowed_syllables = ["a", "b", "c", "d", "e", "f", "g"]
	
	def __init__(self, content):
		self.content = content
	
	
	def __eq__(self, other):
		return self.content == other.content


	def __str__(self):
		return str(self.content)
	

	@staticmethod
	def set_allowed_syllables(new_set):
		Syllable.allowed_syllables = new_set
		
		
	@staticmethod
	def get_random():
		return Syllable(random.choice(Syllable.allowed_syllables))
		

class Word(object):
	
	max_len = 5
	
	def __init__(self, syllables):
		self.syllables = syllables
		
	def __eq__(self, other):
		if other is None:
			return False
		#if isinstance(other, Word):
		return self.syllables == other.syllables
		#return False
	
	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return "".join([str(s) for s in self.syllables])
	
	def __repr__(self):
		return str(self)
	
	@staticmethod
	def set_max_len(n):
		Word.max_len = n
		
	@staticmethod
	def get_random():
		i = random.randint(1,Word.max_len)
		return Word([Syllable.get_random() for _ in xrange(i)])
		#return repr([Syllable.get_random() for i in range(i)])
		
		
	@staticmethod
	def get_random_not_in(words):
		w = Word.get_random()
		while w in words:
			w = Word.get_random()
		return w
	
	
	def __hash__(self):
		return hash(str(self))



class Lexicon(object):
	
	delta_inc = 0.1
	delta_inh = 0.1
	delta_dec = 0.1
	s = 0.5	#initial strength
	
	#L = C x F x [0.0, 1.0]
	def __init__(self, base = None):
		if base is None:
			base = {}
		self.base = base
		self.F = set()	# words

	
	
	def add_element(self, category, word = None, weight = None):
		if weight is None:
			weight = Lexicon.s
		
		if word is None:
			word = Word.get_random_not_in(self.F)
		
		if word not in self.F:
			self.F.add(word)
		
		self.base[(category, word)] = weight
		return word
		
	
	def _find_best(self, choser):
		rval = (None, None)
		if len(self.base) == 0:
			return rval
		
		maxx = -float('inf')
		for k, v in self.base.iteritems():
			if choser(k) and v>maxx:
				maxx, rval = v, k
		
		return rval
	
	
	def word_for(self, category):
		return self._find_best(lambda k:k[0] == category)[1]
	
	
	def category_for(self, word):
		return self._find_best(lambda k:k[1] == word)[0]
		
	
	def decrease(self, category, word):
		w = self.base.pop((category, word)) - Lexicon.delta_dec
		if w>0.:
			self.base[(category, word)] = w
		# ther is possibility that some unused word will stay in self.F
		# FIX THIS ^^^^^ ?


	def _decreaser(self, choser):

		remove = deque()
		update = deque()
		
		for k, v in self.base.iteritems():
			if choser(k):
				w = v - Lexicon.delta_inh
				if w>0.:
					update.append((k, w))
				else:
					remove.append(k)
		
		for k in remove:
			del self.base[k]
		
		for k, v in update:
			self.base[k] = v
		
		
	def inc_dec_categories(self, category, word):
		w = self.base.pop((category, word)) + self.delta_inc
		self._decreaser(lambda k: k[1] == word)
		self.base[(category, word)] = w
	
	def inc_dec_words(self, category, word):
		w = self.base.pop((category, word)) + self.delta_inc
		self._decreaser(lambda k: k[0] == category)
		self.base[(category, word)] = w
		
	def increase_pair_decrease_other(self, category, word):
		w = self.base.pop((category, word)) + self.delta_inc
		self._decreaser(lambda k: k[1] == word)
		self._decreaser(lambda k: k[0] == category)
		self.base[(category, word)] = min(w, 1.)

	def known_words(self):
		known = set()
		for _, w in self.base.iterkeys():
			known.add(w)
		return known
	
	def __str__(self):
		
		return "Lexicon:"+\
			"\t".join(["(\"%s\":%s)"%(w, [(c, s) for (c, w), s in list(g)]) \
		for w, g in groupby(self.base.iteritems(), key=lambda (k, v):k[1])])
		
		
