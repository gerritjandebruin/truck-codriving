"""Split examples into train and test set."""

import argparse, logging, pickle

import numpy as np
import pandas as pd
import sklearn.model_selection

def get_split(X: pd.DataFrame, y: np.ndarray, test_size: float, random_state=1):
  logging.info('Start splitting')
  xtrain, xtest, ytrain, ytest = sklearn.model_selection.train_test_split(
    X, y, test_size=test_size, random_state=random_state, stratify = y
  )
  logging.info('Finished splitting')
  return xtrain, xtest, ytrain, ytest
  
if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('features_filepath', help='Filename of features')
  p.add_argument('targets_filepath', help='Filename of targets')
  p.add_argument('xtrain_filepath', help='Filepath where xtrain will be stored.')
  p.add_argument('xtest_filepath', help='Filepath where ytrain will be stored.')
  p.add_argument('ytrain_filepath', help='Filepath where xtest will be stored.')
  p.add_argument('ytest_filepath', help='Filepath where ytest will be stored.')
  p.add_argument('--test_size', type=float, default=.1)
  args = p.parse_args()

  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

  X = pd.read_pickle(args.features_filepath)
  y = np.load(args.targets_filepath)
  
  xtrain, xtest, ytrain, ytest = get_split(X, y, args.test_size)
  
  xtrain.to_pickle(args.xtrain_filepath)
  xtest.to_pickle(args.xtest_filepath)
  np.save(args.ytrain_filepath, ytrain)
  np.save(args.ytest_filepath, ytest)
  