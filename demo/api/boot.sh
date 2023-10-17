#!/usr/bin/env bash

export VIRTUAL_ENV=/root/.venv

VENV_EXISTS=false
if [[ -r $VIRTUAL_ENV/pyvenv.cfg ]]; then
  VENV_PYTHON_VERSION=$(sed -n '/^version/ s/[^0-9.]//g p' $VIRTUAL_ENV/pyvenv.cfg)
  GLOBAL_PYTHON_VERSION=$(python --version | sed -n 's/[^0-9.]//g p')
  if [[ $VENV_PYTHON_VERSION == $GLOBAL_PYTHON_VERSION ]]; then
    VENV_EXISTS=true
  fi
fi

if [[ $VENV_EXISTS == false ]]; then
  echo "no valid virtualenv found, creating ..."
  rm -rf $VIRTUAL_ENV
  python -m venv $VIRTUAL_ENV || exit 1
fi

source $VIRTUAL_ENV/bin/activate || exit 1

pip install pipenv || exit 1
pipenv install --dev || exit 1

python model_setup.py || exit 1

uvicorn app:app --host 0.0.0.0 --port 5000 --reload --reload-dir .
