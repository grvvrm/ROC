# coding: utf-8
import hypothesis as hp
import matplotlib.pyplot as plt
import numpy as np


def read_frame(frame_label):
    start_label = 0
    end_label = 0
    frame_label = frame_label.strip().split('_')
    if len(frame_label) == 1:
        return 0

    for idx, label in enumerate(frame_label):
        if int(label) != 1:
            start_label = idx
            break
    for idx, label in reversed(list(enumerate(frame_label))):
        if int(label) != 1:
            end_label = idx
            break
    return end_label - start_label



def read_graph(filename):
    command = ''
    data = []
    g = {}
    with open(filename) as f:
        for line in f.readlines():
            data.append(line)

    for line in data:
        if len(line.strip()) == 0:
            continue
        if line.find('command') != -1:
            command = line.strip()
            g[command] = {}
        else:
            _ldata = line.strip().split('\t')
            if len(_ldata) == 1:
                if _ldata[0] not in g[command]:
                    g[command][_ldata[0]] = {'final': 1}
                continue
            f_node = _ldata[0].strip()
            s_node = _ldata[1].strip()
            word = _ldata[2].strip()
            _wdata = _ldata[3].split(',')
            graph_cost = _wdata[0].strip()
            acoustic_cost = _wdata[1].strip()
            frame_no = len(_wdata[2].split('_'))
            word_len = read_frame(_wdata[2])
            if f_node not in g[command]:
                g[command][f_node] = {s_node: [], 'final': 0}
            g[command][f_node][s_node] = [word, graph_cost, acoustic_cost, frame_no, word_len]
    return g


def read_best_path(filename):
    bp = {}
    data = []
    with open(filename) as f:
        for line in f.readlines():
            data.append(line)

    for line in data:
        line_in_list = line.strip().split(' ')
        file = line_in_list[0]
        path = line_in_list[1:]
        bp[file] = path
    return bp


def wordmap(wordfile):
    data = []
    with open(wordfile) as f:
        for line in f.readlines():
            data.append(line.strip().split(' ')[0])

    word2int = {word: idx for idx, word in enumerate(data)}
    int2word = {idx: word for idx, word in enumerate(data)}
    return word2int, int2word


def check_command(actual_t, hyp, decode_t = []):
    t_gt = 'T'
    for word in actual_t:
        if word.strip() == '0':
            t_gt = 'F'

    actual_word = []
    for word in actual_t:
        if len(word.strip()) != 0 and (word.strip() != '1' and word.strip() != '0'):
            actual_word.append(word.strip())

    decode_word = []
    for word in decode_t:
        if len(word.strip()) != 0:
            decode_word.append(word.strip())

    if t_gt == 'T':
        if len(actual_word) != len(decode_word):
            if hyp == 'P':
                #print(actual_word, decode_word)
                t_gt = 'F'
        else:
            for idx, word in enumerate(actual_word):
                if decode_word[idx] != word:
                    if hyp == 'P':
                        #print(actual_word, decode_word)
                        t_gt = 'F'
    return t_gt


def probability_pfa_pd(gt, hyp):
    TP = 0.0
    TN = 0.0
    FP = 0.0
    FN = 0.0
    for key in gt.keys():
        if gt[key] == 'T':
            if hyp[key] == 'P':
                TP += 1
            if hyp[key] == 'N':
                FN += 1
        if gt[key] == 'F':
            if hyp[key] == 'P':
                FP += 1
            if hyp[key] == 'N':
                TN += 1

    print(FP, TN, TP, FN)
    pfa = FP/(TN+FP)
    pd = TP/(TP+FN)

    #pfa = n_fa/n_t
    #pd = n_a/n_t

    return pfa, pd


def read_text(textfile, hyp):
    text = {}
    with open(textfile) as f:
        for line in f.readlines():
            line_in_list = line.strip().split(' ')
            text[line_in_list[0]] = line_in_list[1:]

    gt = {}
    for key in text.keys():
        actual_t = text.get(key)
        if best_path.get(key) is None:
            print(key)
            continue
        # print(best_path.get(key), int2wd)
        decode_t = [int2wd[int(x)].strip() for x in best_path.get(key)]
        value = check_command(actual_t, hyp[key], decode_t)
        # print(key, value)
        gt[key] = value
    return text, gt


def print_hy(textfile, best_path, hyp, ac, wd2int, int2wd, print_hyp='false'):
    text, gt = read_text(textfile, hyp)
    if print_hyp == 'true':
        with open('hyp.txt', 'w') as f:
            for key in hyp.keys():
                f.write('{}\t{}\t{}\t{}\t{}\t{} \n'.format(key, ' '.join(text.get(key)[:-1]), ' '.join([int2wd[int(x)].strip() for x in best_path.get(key)]), gt.get(key), hyp.get(key), ac.get(key)))

    # pfa = no of legal / given no of incorrect
    #  pd = no of legal / given on of correct
    pfa, pd = probability_pfa_pd(gt, hyp)
    return pfa, pd


if __name__ == '__main__':
    graph = read_graph('lattic_specifier.txt')
    best_path = read_best_path('9.tra')
    wd2int, int2wd = wordmap('words.txt')
    hyp, ac, min, max= hp.hypothesis(graph, best_path, 1, 40, 'true')

    print(min, max)
    pfa = []
    pd = []
    for threshold in np.arange(min, max, 0.1):
        hyp, ac = hp.hypothesis(graph, best_path, 1, threshold)
        _pfa, _pd = print_hy('test_filt.txt', best_path, hyp, ac, wd2int, int2wd, 'false')
        pfa.append(_pfa)
        pd.append(_pd)

    print(len(pfa), len(pd), pfa, pd)
    plt.plot(pfa, pd, 'ro')
    plt.xlabel('pfa')
    plt.ylabel('pd')
    #plt.plot(pfa)
    plt.show()

    #print(hyp)
