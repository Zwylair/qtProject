import os
import copy
import random
import shutil
import pathlib
import zipfile
from fastapi import FastAPI
from pydantic import BaseModel
from web_managing import get_round_info, test_checking
from settings import *
import db


class ChosenTest(BaseModel):
    name: str
    randomize_rounds: bool
    randomize_answers: bool


def available_tests():
    return [pathlib.Path(fn).stem for fn in os.listdir('tests') if fn.endswith('.mionly')]


def start_test(chosen_test: ChosenTest):
    is_test_from_external_storage = os.path.exists(chosen_test.name)
    test_file_path = chosen_test.name if is_test_from_external_storage else os.path.join('tests', f'{chosen_test.name}.mionly')
    test_root = os.path.join(
        WEB_CACHE_PATH,
        pathlib.Path(chosen_test.name).stem if is_test_from_external_storage else chosen_test.name
    )
    all_rounds = []
    available_rounds = {}
    allowed_round_types = test_checking.VALID_ROUND_TYPES

    if os.path.exists(test_root):
        shutil.rmtree(test_root, ignore_errors=True)

    zipfile.ZipFile(test_file_path).extractall(test_root)

    for root, dirs, files in os.walk(test_root):
        root = os.sep.join(root.split(os.sep)[1:])  # remove 'tests/' from path
        for file in files:
            all_rounds.append(os.path.join(root, file).replace(os.sep, '/'))

    for raw_round in all_rounds:
        raw_round = raw_round.split('/')
        round_type = raw_round[-2]
        raw_round = f'{round_type}/{raw_round[-1]}'

        if round_type not in available_rounds.keys():
            available_rounds[round_type] = [raw_round]
        else:
            available_rounds[round_type].append(raw_round)

    for round_type in copy.deepcopy(available_rounds).keys():
        if round_type not in allowed_round_types:
            available_rounds.pop(round_type)

    total_rounds_count = 0
    for rounds in available_rounds.values():
        total_rounds_count += len(rounds)

    db.STORAGE = db.Storage(
        chosen_test_name=chosen_test.name,
        round_type=None,
        chosen_round=None,
        randomize_rounds=chosen_test.randomize_rounds,
        randomize_answers=chosen_test.randomize_answers,
        available_rounds=available_rounds,
        allowed_round_types=allowed_round_types,
        total_rounds_count=total_rounds_count,
        last_submitted_round=None,
        points=0,
        max_points=0,
        opened_rounds_count=0,
        test_root=test_root,
    )

    return next_round()


def next_round() -> str:
    storage = db.STORAGE

    if not storage.available_rounds:
        storage.round_type = None
        storage.chosen_round = None
        return finish_testing()

    if storage.randomize_rounds:
        round_type = random.choice(list(storage.available_rounds.keys()))
        rounds = storage.available_rounds[round_type]
        chosen_round = random.choice(rounds)
        storage.available_rounds[round_type].remove(chosen_round)
    else:
        round_type = list(storage.available_rounds.keys())[0]
        chosen_round = storage.available_rounds[round_type][0]
        storage.available_rounds[round_type].remove(chosen_round)

    if not storage.available_rounds[round_type]:
        storage.available_rounds.pop(round_type)

    storage.round_type = round_type
    storage.chosen_round = chosen_round
    storage.opened_rounds_count += 1

    return f'/{round_type}.html'


def finish_testing() -> str:
    return '/testing_ended.html'


def setup(app: FastAPI):
    app.get('/db/next_round')(next_round)
    app.get('/db/get/available_tests')(available_tests)
    app.post('/db/start_test')(start_test)

    get_round_info.setup(app)
    test_checking.setup(app)
