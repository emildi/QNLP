###############################################################################
###############################################################################
"""Example usage:

from QNLP import *
vsm_verbs = VectorSpaceModel.VectorSpaceModel("file.txt")
vsm_verbs.sort_tokens_by_dist("verbs")
vsm_verbs.assign_indexing()
"""
###############################################################################
###############################################################################

import QNLP.proc.process_corpus as pc
import QNLP.encoding.gray as gr
from os import path
import numpy as np
import networkx as nx

class VSM_pc:
    def __init__(self):
        self.pc = pc
    
    def tokenize_corpus(self, corpus, proc_mode=0, stop_words=True):
        """
        Rewrite of pc.tokenize_corpus to allow for tracking of basis word 
        positions in list to improve later pairwise distance calculations.
        """

        token_sents = self.pc.nltk.sent_tokenize(corpus) #Split on sentences
        token_words = [] # Individual words
        tags = [] # Words and respective tags
        
        for s in token_sents:
            tk = self.pc.nltk.word_tokenize(s)
            if stop_words == False:
                tk = self.pc.remove_stopwords(tk, self.pc.sw)
            token_words.extend(tk)
            tags.extend(self.pc.nltk.pos_tag(tk))

        if proc_mode != 0:
            if proc_mode == 's':
                s = self.pc.nltk.SnowballStemmer('english', ignore_stopwords = not stop_words)
                token_words = [s.stem(t) for t in token_words]
            elif proc_mode == 'l':
                wnl = self.pc.nltk.WordNetLemmatizer()
                token_words = [wnl.lemmatize(t) for t in token_words]

        tagged_tokens = self.pc.nltk.pos_tag(token_words)

        nouns = self._get_token_position(tagged_tokens, self.pc.tg.Noun)
        verbs = self._get_token_position(tagged_tokens, self.pc.tg.Verb)

        count_nouns = { k:(v.size,v) for k,v in nouns.items()}
        count_verbs = { k:(v.size,v) for k,v in verbs.items()}

        return {'verbs':count_verbs, 'nouns':count_nouns, 'tk_sentence':token_sents, 'tk_words':token_words}

    def _get_token_position(self, tagged_tokens, token_type):
        """ Tracks the positions where a tagged element is found in 
        the tokenised corpus list. Useful for comparing distances.
        If the key doesn't initially exist, it adds a list with a 
        single element. Otherwise, extends the list with the new 
        token position value.
        """
        token_dict = {}
        for pos, token in enumerate(tagged_tokens):
            if pc.tg.matchables(token_type, token[1]):
                if isinstance(token_dict.get(token[0]), type(None)):
                    token_dict.update( { token[0] : np.array([pos])} )
                else:
                    token_dict.update( { token[0] : np.append(token_dict.get(token[0]), pos) } )
        return token_dict

###############################################################################
###############################################################################

class VectorSpaceModel:
    """
    Use vector space model of meaning to determine relative order of tokens in basis (see disco papers).
    Plan:

    -   1. Populate set of tokens of type t in corpus; label as T; O(n)
    -   2. Choose n top most occurring tokens from T, and define as basis elements of type t; 2 <= n <= |T|; O(n)
    -   3. Find relative (pairwise) distances between these tokens, and define as metric; n(n-1)/2 -> O(n^2)
    -   4. Sort tokens by distance metric; O(n*log(n))
    -   5. Assign tokens integer ID using Gray code mapping of sorted index; O(n)

    After the aboves steps the elements are readily available for encoding using the respective ID. Tokens that appear
    relatively close together will be closer in the sorted list, and as a result have a smaller number of bit flips of difference
    which can be used in the Hamming distance calculation later for similarity of meanings.
    """
    def __init__(self, corpus_path="", mode=0, stop_words=True):
        self.pc = VSM_pc()
        self.tokens = self.load_tokens(corpus_path, mode, stop_words)
        self.encoder = gr.GrayEncoder()
        self.distance_dictionary = None
        self.encoded_tokens = None

###############################################################################
###############################################################################

    def load_tokens(self, corpus_path, mode=0, stop_words=True):
        " 1. Wraps the calls from process_corpus.py to tokenize. Returns None if path is "
        if path.exists(corpus_path):
            return self.pc.tokenize_corpus( pc.load_corpus(corpus_path), mode, stop_words)
        else:
            return None

###############################################################################
###############################################################################

    def sort_basis_helper(self, token_type, num_elems):
        basis_dict = {token_type : {} }
        #consider Counter.most_common(num_elems)
        for counter, elem in enumerate(sorted(self.tokens[token_type].items(), key=lambda x : x[1], reverse = True)):
            if counter == num_elems:
                break
            basis_dict[token_type].update({elem[0] : elem[1]})
        return basis_dict

###############################################################################
###############################################################################

    def define_basis(self, num_basis = {"verbs": 8, "nouns":8}):
        """ 2. Specify the number of basis elements in each space. 
        Dict holds keys of type and values of number of elements to request."""

        if self.tokens == None:
            return
        basis = {}
        for t in ("nouns", "verbs"):
            basis.update( self.sort_basis_helper(t, num_basis[t]) )
        return basis

###############################################################################
###############################################################################

    def sort_tokens_by_dist(self, tokens_type, graph_type = nx.DiGraph, dist_metric = lambda x,y : np.abs(x[:, np.newaxis] - y) ):
        " 3. & 4."
        tk_list = list(self.tokens[tokens_type].keys())
        dist_dict = {}
        # pairwise distance calc
        for c0,k0 in enumerate(tk_list[0:-1]):
            for k1 in tk_list[c0:]:
                if k0 != k1:
                    a = self.tokens[tokens_type][k0][1]
                    b = self.tokens[tokens_type][k1][1]
                    from IPython import embed; embed()
                    dist_dict[(k0,k1)] = list(map(np.unique, dist_metric(a,b)))[0]
                    #sorted([ dist_metric(i,j) for i in self.tokens[tokens_type][k0][1] for j in self.tokens[tokens_type][k1][1] ])

        self.distance_dictionary = dist_dict

        """ Maps the tokens into a fully connected digraph, where each token 
        is a node, and the weighted edge between them holds their 
        respective distance. In the event of multiple distances between 
        two node, assumes the minimum of the list.
        """
        token_graph = self._create_token_graph(dist_dict, graph_type)
        """ Using the token graph, a Hamiltonian path (cycle if [0] 
        connected to [-1]) is found for the graph, wherein the ordering gives
        the shortest path connecting each node, visited once. This gives a 
        sufficiently ordered list for the encoding values.
        """
        ordered_tokens = self._get_ordered_tokens(token_graph)
        self.encoded_tokens = {i:-1 for i in ordered_tokens}
        return ordered_tokens

###############################################################################

    def _create_token_graph(self, token_dist_pairs, graph_type=nx.DiGraph):
        """
        Creates graph using the (basis) tokens as nodes, and the pairwise 
        distances between them as weighted edges. Used to determine optimal 
        ordering of token adjacency for later encoding.
        """
        # Following: https://www.datacamp.com/community/tutorials/networkx-python-graph-tutorial

        assert( callable(graph_type) )

        token_graph = graph_type()

        for tokens_tuple, distances in token_dist_pairs.items():
            # Prevent multiple adds. Should be no prob in any case
            if not token_graph.has_node(tokens_tuple[0]):
                token_graph.add_node(tokens_tuple[0])
            if not token_graph.has_node(tokens_tuple[1]):
                token_graph.add_node(tokens_tuple[1])
            
            # If multigraph allowed, add multiple edges between nodes. 
            # If not, use the min distance.
            if graph_type == nx.MultiGraph:
                if len(distances) > 1:
                    for d in distances:
                        token_graph.add_edge(tokens_tuple[0], tokens_tuple[1], attr_dict={'distance': d, 'weight': d})
                else:
                    token_graph.add_edge(tokens_tuple[0], tokens_tuple[1], attr_dict={'distance': distances, 'weight': distances})               
            else:
                d_val = np.min(distances) if len(distances)>1 else distances
                token_graph.add_edge(tokens_tuple[0], tokens_tuple[1], attr_dict={'distance': d_val, 'weight': d_val})
                if graph_type == nx.DiGraph:
                    token_graph.add_edge(tokens_tuple[1], tokens_tuple[0], attr_dict={'distance': d_val, 'weight': d_val})

        return token_graph            

###############################################################################

    def _get_ordered_tokens(self, token_graph : nx.DiGraph):
        #Must be a directed graph
        assert( isinstance(token_graph, nx.DiGraph) )
        #Must be fully connected
        assert( nx.tournament.is_strongly_connected(token_graph) )

        return nx.tournament.hamiltonian_path(token_graph)

###############################################################################

    def _calc_token_order_distance(self, token_order_list):
        sum_total = []
        for idx in range(1, len(token_order_list)):
            # May be ordered either way
            v0 = self.distance_dictionary.get( ( token_order_list[idx-1], token_order_list[idx] ) )
            v1 = self.distance_dictionary.get( ( token_order_list[idx], token_order_list[idx-1] ) )
            if v0 == None:
                sum_total.append( np.min(v1) )
            else:
                sum_total.append( np.min(v0) )

        return (np.sum(sum_total), sum_total)

###############################################################################
###############################################################################

    def assign_indexing(self):
        """ 5. Encode the ordered tokens using a Gray code based on indexed 
        location. Values close together will have fewer bit flips.
        """
        tk = {}
        for idx,token in enumerate(self.encoded_tokens.keys()):
            self.encoded_tokens.update({token : self.encoder.binToGray(idx) })
        return self.encoded_tokens

###############################################################################
###############################################################################