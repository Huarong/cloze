#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase, main
import sys

sys.path.append('../../')

from n_gram.n_gram_model import NGramModel

class NGramModelTest(TestCase):
    def setUp(self):
        self.n_gram = NGramModel()

    def test_extract_Q(self):
        words = self.n_gram.extract_Q("801) You , of course , saw that _____ in the street was an accomplice.")
        self.assertEqual(words, (801, 'that', 'in'))
        words = self.n_gram.extract_Q("871) His secret was a shameful one , and he could not bring himself to _____ it.")
        self.assertEqual(words, (871, 'to', 'it'))
        words = self.n_gram.extract_Q("1030) Then I walked across to the window , hoping that I might catch some glimpse of the country-side , but an oak _____ , heavily barred , was folded across it.")
        self.assertEqual(words, (1030, 'oak', ","))
        words = self.n_gram.extract_Q("811) He had a very dark , _____ face , and a gleam in his eyes that comes back to me in my dreams.")
        self.assertEqual(words, (811, ',', "face"))
        words = self.n_gram.extract_Q("831) Sherlock Holmes's _____ was soon fulfilled , and in a dramatic fashion.")
        self.assertEqual(words, (831, "'s", "was"))
        words = self.n_gram.extract_Q("993) We laid him upon the drawing-room _____ , and having dispatched the sobered Toller to bear the news to his wife , I did what I could to relieve his pain.")
        self.assertEqual(words, (993, "drawing-room", ","))


    def test_extract_A(self):
        option = self.n_gram.extract_A("    a) mechanism")
        self.assertEqual(option, ('a', 'mechanism'))
        option = self.n_gram.extract_A("    e) apparition")
        self.assertEqual(option, ('e', 'apparition'))

if __name__ == '__main__':
    main()