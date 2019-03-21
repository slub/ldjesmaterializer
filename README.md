# ldjesmaterializer - line-delimited JSON elasticsearch materializer

ldjesmaterializer is a commandline command (Python3 program) that takes line-delimited JSON records and some arguments as input and materializes information from other records (stored in an elasticsearch index) into them.

## Usage

```
ldjesmaterializer

required arguments:
  -elasticsearch-index-name ELASTICSEARCH_INDEX_NAME     the name of the elasticsearch index to use (default: None)
  -elasticsearch-index-type ELASTICSEARCH_INDEX_TYPE     elasticsearch index (document) type to use (default: None)
  -source-field SOURCE_FIELD                             the field name in the (source) record whose value should be used to request the records for materialization (default: None)
  -seed-field SEED_FIELD                                 the field name in the records in the elasticsearch index that should be used to request the records with the seed value for materialization (default: None)
  -materialization-field MATERIALIZATION_FIELD           the field name in the records in the elasticsearch index that contains the information for materialization (default: None)
  -target-field TARGET_FIELD                             the field name in the (target) records that should be used to write the information retrieved from the materialization request to the elasticsearch index (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -elasticsearch-instance-host ELASTICSEARCH_INSTANCE_HOST     hostname or IP address of the elasticsearch instance to use (default: localhost)
  -elasticsearch-instance-port ELASTICSEARCH_INSTANCE_PORT     port of the elasticsearch instance to use (default: 9200)
  -target-field-is-multivalued                                 indicates, whether the target field should be a JSON array (for multiple values) or a JSON object / simple value (for single values); default is false, i.e., the retrieved values will be written into a JSON array (default: False)
```

* example:
    ```
    ldjesmaterializer -elasticsearch-instance-host [HOSTNAME OR IP OF YOUR ELASTICSEARCH INSTANCE] -elasticsearch-instance-port [PORT OF YOUR ELASTICSEARCH INSTANCE] -elasticsearch-index-name [YOUR ELASTICSEARCH INDEX NAME] -elasticsearch-index-type [DOCUMENT TYPE OF THE ELEASTICSEARCH INDEX] -source-field [SOURCE FIELD NAME] -seed-field [SEED FIELD NAME] -materialization-field [MATERIALIZATION FIELD NAME] -target-field [TARGET FIELD NAME]
    ```

## Requirements

[elasticsearch-py](http://elasticsearch-py.rtfd.org/)

### Install requirements

#### Install requirements with pip

1. (optionally) install [pip](https://pip.pypa.io/) for Python 3.x:

    sudo apt-get install python3-pip

2. install requirements with pip:

    sudo -H pip3 install -r requirements.txt
    
#### Install requirements with OS package manager

e.g.
```
apt-get install python-elasticsearch

```

## Run

* install elasticsearch-py
* clone this git repo or just download the ldjesmaterializer.py file
* run ./ldjesmaterializer.py
* for a hackish way to use ldjesmaterializer system-wide, copy to /usr/local/bin

### Install system-wide via pip

* via pip:
    ```
    sudo -H pip3 install --upgrade [ABSOLUTE PATH TO YOUR LOCAL GIT REPOSITORY OF LDJESMATERIALIZER]
    ```
    (which provides you ```ldjesmaterializer``` as a system-wide commandline command)