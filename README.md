# galadriel
galadriel is a Test Management System

A simple but yet straight to the point and functional Test Management System, which inherits inspiration from testlink and other existing tools.

 ## requirements
* reflex 0.6.7
* reflex-local-auth 0.2.2
* PyYAML 6.0.2
* atlassian-python-api 3.41.16

## install
* clone the repo: ```git clone https://github.com/leandrorojas/galadriel.git```
* create an virtual environment i.e.: ```python -m venv .venv/```
* activate the venv ```source .venv/bin/activate```
* install prerequisietes ```pip install -r requirements.txt```
* execute the command ```reflex db init```
* execute the command ```reflex run```
* done!

### fixing install errors
```TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'```


Feel free to turn it into the perfect community product. The request is that you commit your changes to this repo for everyone to enjoy them.

Built with Reflex, built to work.

If you want to contribute, galadriel currently needs:
* unit tests
* code optimization/reusability