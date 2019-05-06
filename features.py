import glob
import os
from joblib import dump

import pandas as pd
import numpy as np
from sklearn import ensemble, metrics, model_selection


PREDICT_KEY = 'win_prop'

_BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MODELS_PATH = os.path.join(_BASE_PATH, 'data/models')
FEATURES_PATH = os.path.join(_BASE_PATH, 'data/features')


def read(file_path) -> pd.DataFrame:
    return pd.read_csv(file_path)


def learn(data: pd.DataFrame) -> ensemble.RandomForestRegressor:
    train, test = model_selection.train_test_split(data, test_size=0.2)
    train_X, train_y = train.drop([PREDICT_KEY], axis=1), train[PREDICT_KEY]
    test_X, test_y = test.drop([PREDICT_KEY], axis=1), test[PREDICT_KEY]

    regressor = ensemble.RandomForestRegressor(n_estimators=10)
    regressor.fit(train_X, train_y)

    # TODO is pandas index being treated as a feature?

    predicted_y = regressor.predict(test_X)
    mse = metrics.mean_squared_error(test_y, predicted_y)
    print("Regressor expected prediction mse: ", mse)

    full_X, full_y = data.drop([PREDICT_KEY], axis=1), data[PREDICT_KEY]
    full_regressor = ensemble.RandomForestRegressor(n_estimators=10)
    full_regressor.fit(full_X, full_y)    

    return full_regressor


def save(model, save_file) -> None:
    dump(model, save_file)


if __name__ == "__main__":
    features_dir = glob.glob("{}/*.csv".format(FEATURES_PATH))
    os.makedirs(MODELS_PATH, exist_ok=True)

    for features_path in features_dir:
        name = os.path.basename(features_path).split("_")[0]
        model = learn(read(features_path))
        save(model, "{}/{}.joblib".format(MODELS_PATH, name))
        print("{} done.".format(name))
