# coding: utf-8


def hypothesis(g, best_path, scale, threshold, min_max='false'):
    hy = {}
    acoustic_cost = {}
    cost = []

    min = 100000.0
    max = -100000.0
    for key in g.keys():
        if key not in best_path.keys():
            #print(key)
            continue

        cost = []
        bp = best_path.get(key)
        s_g = g.get(key)

        nx_bp_no = 0
        n_node = '0'

        if key not in acoustic_cost.keys():
            acoustic_cost[key] = {'weights': [], 'initial': 0, 'final': 0}

        for f_node in sorted(s_g.keys()):



            #print(key, f_node, n_node)



            for s_node in sorted(s_g[f_node].keys()):
                if s_node == 'final' :
                    print(s_g[f_node][s_node])
                    if s_g[f_node][s_node] == 1:
                        acoustic_cost[key]['final'] += 1
                    continue

                if f_node == '0':
                    acoustic_cost[key]['initial'] += 1

                if f_node != n_node:
                    continue

                if len(bp) <= nx_bp_no:
                    continue

                value = s_g[f_node][s_node]

                #print(_bp, value)

                if min_max == 'true':
                    if float(value[2]) < min:
                        min = float(value[2])
                    if float(value[2]) > max:
                        max = float(value[2])

                if value[0] == bp[nx_bp_no]:
                    cost.append([value[0], float(value[2])])
                    if float(value[2]) > threshold:
                        hy[key] = 'N'
                    n_node = s_node
                    nx_bp_no += 1

        acoustic_cost[key]['weights'] = cost
        if key not in hy.keys():
            hy[key] = 'P'
    if min_max == 'true':
        return hy, acoustic_cost, min, max
    else:
        return hy, acoustic_cost
            
            
            
            
            
                 
                 
                 
                 
                 

                 
                 


                 
                 
                 

                 
                 
