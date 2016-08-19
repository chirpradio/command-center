# CHIRP Radio Command Center

Web interface for running commands in [chirpradio-machine](https://github.com/chirpradio/chirpradio-machine/).

# Installation

```
mkvirtualenv chirp
pip install -r requirements.txt
```

Now change to the directory where chirpradio-machine was cloned, and run

```
python setup.py develop
```

# Running

Inside the command-center directory, run

```
python main.py
```

Then open [localhost:8000](http://localhost:8000) in your browser.
