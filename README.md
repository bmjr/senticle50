# Senticle 50

> This project contains the report and programmatic resources that together formed my disseration submission for the *BSc Computer Science Degree* at the **University Of Birmingham (Class of 2018)**.

Senticle50 is a real time system for the predicition of opinion via tweets, with the report enclosed in this project explaining how the System was applied to the discourse around the "Brexit Twitter Debate"

## System Setup

> As the system is no longer publically hosted you will have to enter your own DB credentials. Details of the database schema can be found in the Django models so if you still wish to run this locally the following instructions can be followed. 

### Running the system locally

#### Prequisites:
* Python 3.X
* PIP
* NodeJS
* VirtualEnv for PIP

#### Virtual Environment Setup
```
cd brexit

python3 -m venv python-virtualenv

. ./python-virtualenv/bin/activate

pip3 install -r requirements.txt

npm i

python manage.py collectstatic --noinput -c --settings=brexit.settings.production

python brexit/scripts/Setup.py
```

#### Run the system

```
python manage.py runserver --settings=brexit.settings.production
```

view site from: http://127.0.0.1:8000/
## Example System Operational Command examples.

```
python manage.py Tokenize -h --settings=brexit.settings.production
python manage.py Tokenize --since=2016-01-01 --until=2019-01-01 --overwrite --settings=brexit.settings.production

python manage.py ClassifyBatch -h --settings=brexit.settings.production
python manage.py ClassifyBatch --since=2017-01-01 --until=2017-02-02 --config=brexit_stance_superior_labelling_config.json --settings=brexit.settings.production

python manage.py Stream --settings=brexit.settings.production
```

## License
This project is licensed under the MIT license - see the [LICENSE.md](LICENSE.md) file for details.
