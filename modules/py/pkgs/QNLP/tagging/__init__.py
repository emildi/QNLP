name = "tagging"
import nltk
import sys
import numpy as np

from collections import Counter
from nltk.corpus import stopwords

from QNLP.tagging.word_types import Noun
from QNLP.tagging.word_types import Verb
from QNLP.tagging.word_types import Sentence

import QNLP.tagging.tag_file

__all__ = ["word_types","tag_file"]

"""
Reduces the nltk/spacy types to simplified types defined above
"""    
def matchables(classType, tag):
    if isinstance(classType, Noun) or classType is Noun:
        return tag in ["NN","NNS","NNP","NNPS","NOUN", "PROPN"]
    elif isinstance(classType, Verb) or classType is Verb:
        return tag in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ","VERB"]
    else:
        return False        
