# galadriel
galadriel is a Test Management System

A simple but yet straight to the point and functional Test Management System, which inherits inspiration from testlink and other existing tools.

See what galadriel does and how she is built in [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/leandrorojas/galadriel)

# badges
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=leandrorojas_galadriel&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=leandrorojas_galadriel)

 ## requirements
* reflex 0.8.1
* reflex-local-auth 0.3.0
* PyYAML 6.0.2
* requests 2.32.3

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
    ### configuring Jira
    * copy ```copy_me_into_galadriel.yaml``` into ```galadriel.yaml```
    * get a Jira token for your account by following the official Atlassian documentation: [Manage API tokens for your Atlassian account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
    * fill in the yaml configuration, the yaml file has sameple dummy data:
        * _url_: the url of your jira instance, i.e.: _https://instance.atlassian.net_
        * _user_: your Jira username, i.e: _yourmail@server.com_
        * _token_: the token you got above
        * _project_: the Jira project key in which the issues will be created, i.e: _TEST_
        * _issue_type_: the issue types that will be created i.e: _Bug_
        * _done_status_: the status in which the _issue_type_ is considered as Done by Jira

        <u>Note</U>: galadriel does not validate on the Jira objects existence, yet.

* execute the command ```reflex db init```
* uncomment the lines
* execute the command ```reflex run```
* done, enjoy galadriel

## galadriel needs you
Feel free to turn it into the perfect community product. The request is that you commit your changes to this repo for everyone to enjoy them.

Built with Reflex, built to work.

If you want to contribute, galadriel currently needs:
* unit tests
* code optimization/reusability

