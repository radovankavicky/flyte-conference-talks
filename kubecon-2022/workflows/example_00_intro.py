"""Flyte Intro: Tasks and Workflows.

These examples will use the penguins dataset:
https://allisonhorst.github.io/palmerpenguins/

Using the pypi package:
https://pypi.org/project/palmerpenguins/
"""

from typing import Tuple

import pandas as pd
from palmerpenguins import load_penguins
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from flytekit import task, workflow


TARGET = "species"
FEATURES = [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]


@task
def get_data() -> pd.DataFrame:
    """
    🧱 A task is the fundamental building block and basic unit of compute.
    You can think of these as strongly typed dockerized python functions.
    """
    return load_penguins()[[TARGET] + FEATURES].dropna()


@task
def split_data(
    data: pd.DataFrame, test_size: float, random_state: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    return train_test_split(data, test_size=test_size, random_state=random_state)


@task
def train_model(data: pd.DataFrame, hyperparameters: dict) -> LogisticRegression:
    return LogisticRegression(**hyperparameters).fit(data[FEATURES], data[TARGET])


@task
def evaluate(model: LogisticRegression, data: pd.DataFrame) -> float:
    return float(accuracy_score(data[TARGET], model.predict(data[FEATURES])))


@workflow
def training_workflow(
    hyperparameters: dict = {"C": 0.1, "max_iter": 5000},
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[LogisticRegression, float, float]:
    """
    🔀 Workflows are the core abstraction for composing tasks together into
    meaningful applications. These are statically compiled execution graphs.
    """

    # get and split data
    data = get_data()
    train_data, test_data = split_data(
        data=data, test_size=test_size, random_state=random_state
    )

    # train model on the training set
    model = train_model(data=train_data, hyperparameters=hyperparameters)

    # evaluate the model
    train_acc = evaluate(model=model, data=train_data)
    test_acc = evaluate(model=model, data=test_data)

    # return model with results
    return model, train_acc, test_acc


if __name__ == "__main__":
    # You can run workflows locally, it's just Python 🐍!
    print(f"{training_workflow()}")
