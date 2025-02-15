# galadriel
galadriel is a Test Management System

A simple but yet straight to the point and functional Test Management System, which inherits inspiration from testlink and other existing tools.

# badges
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=leandrorojas_galadriel&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=leandrorojas_galadriel)

 ## requirements
* reflex 0.6.8
* reflex-local-auth 0.2.2
* PyYAML 6.0.2
* atlassian-python-api 3.41.16

## first run
* clone the repo: ```git clone https://github.com/leandrorojas/galadriel.git```
* create an virtual environment, i.e.: ```python -m venv .venv/```
* activate the venv ```source .venv/bin/activate```
* install prerequisietes ```pip install -r requirements.txt```
* comment these lines on the galadriel.py:
    ```
    seed = install.seed
    if (seed.is_first_run() == True):
        seed.seed_db()
        seed.set_first_run()
    ```
### configuring jira
* make a copy or rename the file ```rename_me_to_galadriel.yaml``` to ```galadriel.yaml```
* 

* execute the command ```reflex db init```
* uncomment the lines
* execute the command ```reflex run```
* done!

## galadriel needs you
Feel free to turn it into the perfect community product. The request is that you commit your changes to this repo for everyone to enjoy them.

Built with Reflex, built to work.

If you want to contribute, galadriel currently needs:
* unit tests
* code optimization/reusability

