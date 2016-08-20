# CHIRP Radio Command Center

Web interface for running commands in [chirpradio-machine](https://github.com/chirpradio/chirpradio-machine/).

## Requirements

- Python 2.7
- Latest version of chirpradio-machine

## Installation

```
mkvirtualenv chirp
pip install -r requirements.txt
```

Now change to the directory where chirpradio-machine was cloned, and run

```
python setup.py develop
```

Make sure to follow the instructions in the [Installation section of the chirpradio-machine README](https://github.com/chirpradio/chirpradio-machine/#installation).


## Running

Inside the command-center directory, run

```
python main.py
```

Then open [localhost:8000](http://localhost:8000) in your browser.

## Testing

```
nosetests -v
```
