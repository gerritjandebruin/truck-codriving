"""Obtain best parameters for classifier."""

import argparse, logging, pickle
import numpy as np
import pandas as pd
import sklearn.ensemble
import sklearn.metrics
import sklearn.model_selection

def gridsearch(
  xtrain: pd.DataFrame, 
  xtest: pd.DataFrame, 
  n_jobs_clf: int, 
  n_jobs_cv: int
    ):
  clf = sklearn.ensemble.RandomForestClassifier(
    class_weight='balanced', n_jobs=n_jobs_clf, verbose=100, random_state=1, #type: ignore
    n_estimators=128 #type: ignore
  )
  gridsearch_clf = sklearn.model_selection.GridSearchCV(
    estimator=clf, #type: ignore
    param_grid={'max_depth': [1, 2, 4, 8, 16, 32, 64, 64, None]}, #type: ignore
    scoring=['average_precision', 'roc_auc'], #type: ignore
    n_jobs=n_jobs_cv, #type: ignore
    refit='roc_auc', #type: ignore
    verbose=100, #type: ignore
    return_train_score=True, #type: ignore
  )

  gridsearch_clf.fit(xtrain, xtest) #type: ignore

  return gridsearch_clf
  
if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('xtrain_filepath', help='Filepath where xtrain is stored.')
  p.add_argument('ytrain_filepath', help='Filepath where xtest is stored.')
  p.add_argument(
    'output_filepath', help='Filepath where result should be stored.')
  p.add_argument(
    '--n_jobs_clf', help='Number of cores per clf.', default=-1, type=int)
  p.add_argument(
    '--n_jobs_cv', help='Number of models simultaneous.', default=1, type=int)
  args = p.parse_args()

  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

  logging.info('Start reading xtrain')
  xtrain = pd.read_pickle(args.xtrain_filepath)
  logging.info('Start reading ytrain')
  ytrain = np.load(args.ytrain_filepath)
  
  logging.info('Do gridsearch')
  result = gridsearch(
    xtrain, ytrain, n_jobs_clf=args.n_jobs_clf, n_jobs_cv=args.n_jobs_cv)
  
  logging.info('Store result')
  with open(args.output_filepath, 'wb') as file:
    pickle.dump(result, file)
  