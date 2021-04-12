"""Split examples into train and test set."""

import argparse, logging, pickle
import numpy as np
import pandas as pd
import sklearn.ensemble
import sklearn.metrics

def learn(xtrain, xtest, ytrain, ytest, max_depth):
  logging.info(f'Start learning model with {max_depth=}')
  clf = sklearn.ensemble.RandomForestClassifier(
    n_estimators=128, max_depth=max_depth, #type: ignore
    class_weight='balanced', n_jobs=-1, verbose=5) #type: ignore
  clf.fit(xtrain, ytrain)

  logging.info('Start testing model')
  fpr, tpr, _ = sklearn.metrics.roc_curve(
    y_true=ytest, y_score=clf.predict_proba(xtest)[:,1]) #type: ignore
  fp = fpr*(~np.array(ytest).sum()) #type: ignore
  tp = tpr*(np.sum(ytest))

  auroc = sklearn.metrics.auc(x=fpr, y=tpr)

  y_score = clf.predict_proba(xtest)[:, 1] #type: ignore
  ap = sklearn.metrics.average_precision_score(y_true=ytest, y_score=y_score) #type: ignore
  
  return dict(clf=clf, fpr=fpr, tpr=tpr, tp=tp, fp=fp, auroc=auroc, ap=ap)
  
if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('xtrain_filepath', help='Filepath where xtrain is stored.')
  p.add_argument('xtest_filepath', help='Filepath where ytrain is stored.')
  p.add_argument('ytrain_filepath', help='Filepath where xtest is stored.')
  p.add_argument('ytest_filepath', help='Filepath where ytest is stored.')
  p.add_argument('output_filepath', help='Filepath where performance is stored')
  p.add_argument('--max-depth', default=None, type=int)
  args = p.parse_args()

  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s') 
  logging.info('Start reading xtrain')
  xtrain = pd.read_pickle(args.xtrain_filepath)
  logging.info('Start reading xtest')
  xtest = pd.read_pickle(args.xtest_filepath)
  logging.info('Start reading ytrain')
  ytrain = np.load(args.ytrain_filepath)
  logging.info('Start reading ytest')
  ytest = np.load(args.ytest_filepath)  
  
  result = learn(xtrain, xtest, ytrain, ytest, args.max_depth)
  
  with open(args.output_filepath, 'wb') as file:
    pickle.dump(result, file)
  