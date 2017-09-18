from FeatureSelector import *
from timeit import default_timer as timer
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.stats.mstats import spearmanr

NUM_TRIALS = 1


def test():
    # with open('../lib/src/test/resources/data3.csv', 'r') as f:
    # 	_ = next(f)
    # 	X = []
    # 	y = []
    # 	for line in f:
    # 		data = line.strip().split(',')
    # 		X.append([float(i) for i in [data[2], data[7], data[8]]])
    # 		y.append(data[4])  # hardware model
    # 	X = np.asarray(X)
    # 	y = np.asarray(y)
    # 	X = add_noise(X)
    # 	print X.shape
    # 	print y.shape

    # with open('../lib/src/test/resources/league_matches.csv', 'r') as f:
    # 	columns = f.readline().strip().split(',')
    # 	# print columns
    # 	# print columns.index('assists@100'), columns.index('assists@200'), columns.index('kills@100'), columns.index('totalDamageDealtToChampions@100'), columns.index('wardsPlaced@100')
    # 	X = []
    # 	y = []
    # 	# metrics = ['kills@100', 'totalDamageDealtToChampions@100', 'wardsPlaced@100', 'gameDuration', 'seasonId']
    # 	index = [0, 1] + range(34, 58)  # 58 total
    # 	metricColumns = [columns[i] for i in index]
    # 	attribute = 'championId@100/BOTTOM/DUO_CARRY'
    # 	for line in f:
    # 		data = line.strip().split(',')
    # 		# if int(data[columns.index('totalDamageDealt@100')]) < 0 or int(data[columns.index('totalDamageDealt@200')]) < 0:
    # 		# 	continue
    # 		# if int(data[columns.index('gameDuration')] < 400):
    # 		# 	continue
    # 		# if int(data[columns.index(attribute)]) == 0:
    # 		# 	continue
    # 		# print len(data), columns.index('kills@100'), columns.index('totalDamageDealtToChampions@100'), columns.index('wardsPlaced@100')
    # 		preprocessed_X = []
    # 		# for m in metrics:
    # 		# 	preprocessed_X.append(data[columns.index(m)])
    # 		for i in index:
    # 			if i == 39:  # gameVersion
    # 				preprocessed_X.append(data[i].replace('.', ''))
    # 			else:
    # 				preprocessed_X.append(data[i])
    # 		X.append([float(i) for i in preprocessed_X])
    # 		y.append(data[columns.index(attribute)])
    # 		# y.append(data[columns.index('winningTeamId')])
    # 	X = np.asarray(X)
    # 	# for i in xrange(X.shape[1]):
    # 	# 	print "{}: {}".format(columns[i], len(set(X[:,i])))
    # 	y = np.asarray(y)
    # 	real_metrics = range(len(metricColumns))
    # 	X = add_noise(X, 5, 5, 5)
    # 	print X.shape
    # 	print y.shape
    # 	# duration = X[:,metricColumns.index('gameDuration')]
    # 	# plt.hist(duration, bins=100)
    # 	# plt.show()

    with open('../lib/src/test/resources/shuttle.csv', 'r') as f:
        columns = next(f).strip().split(',')
        metricColumns = columns[:-1]
        X = []
        y = []
        index = range(9)
        for line in f:
            data = [float(x) for x in line.strip().split(',')]
            X.append(data[:-1])
            y.append(data[-1])
        X = np.asarray(X)
        y = np.asarray(y)
        real_metrics = range(len(metricColumns))
        X = add_noise(X, 3, 3, 3)
        # fake_metrics = range(len(metricColumns), X.shape[1])
        print("num rows: {}, num metrics: {}\n".format(X.shape[0], X.shape[1]))

    # # use synthetic data
    # num_cols = 20
    # num_rows = 1000000
    # input = np.random.rand(num_cols, num_rows)

    # TODO: uncomment this line
    # visualize_data(X, y, metricColumns)
    # return

    np.set_printoptions(precision=3, suppress=True)

    # process
    mad = MultiMAD()
    start = timer()
    for _ in range(NUM_TRIALS):
        mad.process(X)
        mad.compute_explanation(y)
    end = timer()
    print("MultiMAD using percentiles:")
    print("Total time elapsed: {}".format(end - start))
    percentile_metrics_with_explanations = np.nonzero(mad.num_expl_by_metric)[0]
    print("Metrics that produce at least one explanation: {}".format(percentile_metrics_with_explanations))
    accuracy(percentile_metrics_with_explanations, real_metrics)
    print("Metric | Top RR | Num explanations | Explanations")
    for i in np.asarray(mad.top_ratio_by_metric).argsort()[::-1]:
        if i in real_metrics:
            print(columns[index[i]], mad.top_ratio_by_metric[i], mad.num_expl_by_metric[i],
                  mad.explanations_by_metric[i])
    print("")

    mad.percentile = False
    start = timer()
    for _ in range(NUM_TRIALS):
        mad.process(X)
        mad.compute_explanation(y)
    end = timer()
    print("MultiMAD using MAD:")
    print("Total time elapsed: {}".format(end - start))
    mad_metrics_with_explanations = np.nonzero(mad.num_expl_by_metric)[0]
    print("Metrics that produce at least one explanation: {}".format(mad_metrics_with_explanations))
    accuracy(mad_metrics_with_explanations, real_metrics)
    # print("Top ratios correlation for mad: {}".format(spearmanr(mad_ratio_ranking, mad_ratio_ranking_mad)[0]))
    # print("Num attrs correlation for mad: {}".format(spearmanr(mad_attrs_ranking, mad_attrs_ranking_mad)[0]))
    print("Metric | Top RR | Num explanations | Explanations")
    for i in np.asarray(mad.top_ratio_by_metric).argsort()[::-1]:
        if i in real_metrics:
            print(columns[index[i]], mad.top_ratio_by_metric[i], mad.num_expl_by_metric[i],
                  mad.explanations_by_metric[i])
    print("")

    # for clf in ['svm', 'lr', 'tree']:
    for clf in ['lr', 'tree']:
        selector = ModelSelector()

        start = timer()
        for _ in range(NUM_TRIALS):
            eval('selector.select_features_' + clf + '(X, y)')
        end = timer()
        print("Selection from Model {}:".format(clf))
        print("Total time elapsed: {}".format(end - start))
        print("Coefficients by metric: {}".format(selector.coef))
        clf_ranking = selector.coef.argsort()[::-1]
        print("Metric ranking: {}".format(clf_ranking))
        clf_columns = clf_ranking[:len(percentile_metrics_with_explanations)]
        accuracy(clf_columns, real_metrics)
        print("")

        # print("Top ratios correlation for {}: {}".format(clf, spearmanr(mad_ratio_ranking, clf_ranking)[0]))
        # print("Num attrs correlation for {}: {}".format(clf, spearmanr(mad_attrs_ranking, clf_ranking)[0]))

    # for func in ['f_classif', 'mutual_info_classif']:
    for func in ['anova']:
        selector = UnivariateSelector()

        start = timer()
        for _ in range(NUM_TRIALS):
            selector.select_features(X, y, func)
        end = timer()
        print("Univariate {}:".format(func))
        print("Total time elapsed: {}".format(end - start))
        print("Scores by metric: {}".format(selector.scores))
        anova_ranking = selector.scores.argsort()[::-1]
        print("Metric ranking: {}".format(anova_ranking))
        anova_columns = anova_ranking[:len(percentile_metrics_with_explanations)]
        accuracy(anova_columns, real_metrics)
        # print "anova columns: {}".format(anova_columns)
        # print "{}".format(anova_ranking)
        # for i in anova_ranking:
        #     if i in real_metrics:
        #         print(columns[index[i]], selector.scores[i])
        #
        #         # print "Top ratios correlation: {}".format(spearmanr(mad_ratio_ranking, anova_ranking)[0])
        #         # print "Num attrs correlation: {}".format(spearmanr(mad_attrs_ranking, anova_ranking)[0])
        #
        #         # jaccard_sim(percentile_columns, mad_columns, 'percentile', 'mad')
        #         # jaccard_sim(percentile_columns, anova_columns, 'percentile', 'anova')
        print("")

    # selector = RecursiveSelector()

    # start = timer()
    # for _ in xrange(NUM_TRIALS):
    # 	selector.select_features(X, y)
    # end = timer()
    # print("Recursive:")
    # print("Total time elapsed: {}".format(end - start))
    # print("{}".format(selector.selector.ranking_))


def jaccard_sim(col1, col2, clf1='clf1', clf2='clf2'):
    len_int = len(set(col1).intersection(set(col2)))
    len_union = len(set(col1).union(set(col2)))
    sim = float(len_int) / len_union
    print("Similarity bw {} and {}: {} ({}/{})".format(clf1, clf2, sim, len_int, len_union))


def accuracy(col, real_metrics):
    num_real_found = len(set(col).intersection(set(real_metrics)))
    print("If fake metrics were inserted into data:")
    print("\tRecall: {} ({}/{})".format(num_real_found / float(len(real_metrics)), num_real_found,
                                        len(real_metrics)))
    print("\tPrecision: {} ({}/{})".format(num_real_found / float(len(col)), num_real_found, len(col)))


# Add as many noisy columns as actual columns
def add_noise(X, num_noise=None, num_uniform=None, num_const=None):
    if num_noise is None:
        num_noise = X.shape[1]
    if num_uniform is None:
        num_uniform = X.shape[1]
    if num_const is None:
        num_const = X.shape[1]
    for i in range(num_noise):
        noisy = np.random.normal(loc=random.uniform(0, 100), size=(X.shape[0], 1))
        X = np.concatenate((X, noisy), axis=1)
    for i in range(num_uniform):
        uniform = np.random.uniform(low=random.uniform(0, 50), high=random.uniform(50, 100), size=(X.shape[0], 1))
        X = np.concatenate((X, uniform), axis=1)
    for i in range(num_const):
        const = np.full(shape=(X.shape[0], 1), fill_value=random.uniform(0, 100))
        X = np.concatenate((X, const), axis=1)
    return X


def visualize_data(X, y, columns):
    mad = MultiMAD()
    for i in range(X.shape[1]):
        print("min: {}, max: {}".format(np.amin(X[:, i]), np.amax(X[:, i])))
        percentiles = [np.percentile(X[:, i], 1), np.percentile(X[:, i], 99)]
        mad.compute_mad(X[:, i])
        # plt.scatter(X[:,i], y)
        X_multi = []
        # cats = ['0', 'not 0']
        # indices = [[r for r in xrange(X.shape[0]) if y[r] == '0'], [r for r in xrange(X.shape[0]) if y[r] != '0']]
        cats = []
        indices = []
        for cat in set(y):
            indices.append([r for r in range(X.shape[0]) if y[r] == cat])
            cats.append(cat)
        for inds in indices:
            X_multi.append([X[r, i] for r in inds])
        colors = cm.rainbow(np.linspace(0, 1, len(cats)))
        hist_range = [np.amin(X[:, i]), np.amax(X[:, i])]
        if i == 3 or i == 5:
            hist_range = [-50, 50]
        plt.hist(X_multi, bins=200, normed=True, histtype='step', label=cats, color=colors, range=hist_range)
        plt.legend()
        for xc in percentiles:
            plt.axvline(x=xc, color='b')
        for xc in [mad.low_cutoff, mad.high_cutoff]:
            plt.axvline(x=xc, color='r')
        plt.title(columns[i])
        plt.show()


if __name__ == "__main__":
    test()