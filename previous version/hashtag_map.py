from flask.templating import render_template
import matplotlib.pyplot as plt
from plots import generate_list
import networkx as nx
from collections import Counter
from pyvis.network import Network
import os

def generateHashtagList(column, keyword, fromDate, toDate):
    hashtag_list = generate_list(column, keyword, fromDate, toDate)
    return hashtag_list

def get_weights(hashtag, hashtag_list):
    return round(hashtag_list.count(hashtag) / len(hashtag_list), 3)

def createTopTenHashtagGraph(keyword, fromDate, toDate):
    hashtag_graph = nx.Graph()
    hashtag_graph.add_node(keyword, pos=(30, 4))
    hashtag_list = generateHashtagList("hashtags", keyword, fromDate, toDate)
    
    hashtag_dict = {}
    for hashtag in hashtag_list:
        if hashtag in hashtag_dict:
            hashtag_dict[hashtag] += 1
        else:
            hashtag_dict[hashtag] = 1
    topTenHashtags = Counter(hashtag_dict).most_common(10)
    i = 2
    j = 0
    for hashtag in topTenHashtags:
        if not hashtag_graph.has_node(hashtag):
            hashtag_graph.add_node(str(hashtag), pos=(j, i))
            hashtag_graph.add_edge(str(keyword), str(hashtag), weight=int(get_weights(hashtag, topTenHashtags)))
            if i == 0:
                i = 2
            else:
                i -= 1
            j += 10
    pos=nx.get_node_attributes(hashtag_graph,'pos')
    labels = nx.get_edge_attributes(hashtag_graph,'weight')
    # nx.draw(hashtag_graph, pos, with_labels=True)
    # nx.draw_networkx_edge_labels(hashtag_graph, pos, edge_labels=labels)
    nt = Network('500px', '500px')
    nt.from_nx(hashtag_graph)
    # nt.enable_physics(True)
    nt.save_graph('tree.html')
    os.replace("tree.html", "../product/templates/tree.html")
    # plt.savefig("./hashtag_tree")
