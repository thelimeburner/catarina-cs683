import glob
import os
import re
from joblib import dump
from typing import Dict

import pandas as pd
import numpy as np
from sklearn import ensemble, metrics, model_selection


PREDICT_KEY = 'win_prop'

_BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MODELS_PATH = os.path.join(_BASE_PATH, 'data/models')
FEATURES_PATH = os.path.join(_BASE_PATH, 'data/features')


def read(files) -> Dict[str, pd.DataFrame]:

    # Organize multiple runs into the respective players
    players = {}
    for f in files:
        player_name = re.match(r"^.*?([A-Za-z]+)_.*$", os.path.basename(f)).group(1)
        players.setdefault(player_name, []).append(f)

    # Concatenate all the data into just one training set
    training_sets = {}
    for player, data in players.items():
        print("Player {} fo`und, with {} files".format(player, len(data)))
        df = pd.concat(
            [pd.read_csv(file_path) for file_path in data], 
            axis=0, 
            ignore_index=True)
        training_sets[player] = df

    return training_sets


# TODO gridsearchcv and different models test?
def _chosen_model():
    return ensemble.RandomForestRegressor(n_estimators=10)


def learn(data: pd.DataFrame) -> ensemble.RandomForestRegressor:
    # Run the selected model architecture through a light amount of testing so we
    # can have some decent expectation on performance
    train, test = model_selection.train_test_split(data, test_size=0.2)
    train_X, train_y = train.drop([PREDICT_KEY], axis=1), train[PREDICT_KEY]
    test_X, test_y = test.drop([PREDICT_KEY], axis=1), test[PREDICT_KEY]

    regressor = _chosen_model()
    regressor.fit(train_X, train_y)
    # TODO is pandas index being treated as a feature?

    predicted_y = regressor.predict(test_X)
    mse = metrics.mean_squared_error(test_y, predicted_y)
    print("Regressor expected prediction mse: ", mse)

    # Return a model which fully utilizes the training data
    full_X, full_y = data.drop([PREDICT_KEY], axis=1), data[PREDICT_KEY]
    full_regressor = _chosen_model()
    full_regressor.fit(full_X, full_y)    

    return full_regressor


def save(model, save_file) -> None:
    dump(model, save_file)


if __name__ == "__main__":
    features_dir = glob.glob("{}/**/*.csv".format(FEATURES_PATH), recursive=True)
    os.makedirs(MODELS_PATH, exist_ok=True)

    player_data = read(features_dir)
    for player, dataframe in player_data.items():
        model = learn(dataframe)
        save(model, "{}/{}.joblib".format(MODELS_PATH, player))
        print("{} done.".format(player))
