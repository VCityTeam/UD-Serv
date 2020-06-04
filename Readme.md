# UD-Serv

UD-Serv is a collection of server-side tools for converting and analysing urban data.

Note: for the client-side components [refer to UD-Viz](https://github.com/VCityTeam/UD-Viz/).

## Available tools

### API_Enhanced_City
The goal of the 
[API **Enhanced City**](https://github.com/MEPP-team/UD-Serv/blob/master/API_Enhanced_City) 
is to handle, and serve through [web services](https://en.wikipedia.org/wiki/Web_service), 
various types of city related data in the context of 
[UD-SV (Urban Data Services and Vizualisation)](https://github.com/VCityTeam/UD-SV). 

The API currently offers [web service](https://en.wikipedia.org/wiki/Web_service) 
access to few following types of resources :
- Documents (file and metadata)
- Guided tours (sequences of documents with additional texts)
- Links between documents and other (city) objects
- User accounts and rights

### ExtractCityData

#### Introduction

This tool allows to process a
[3DCityDB](https://www.3dcitydb.org/3dcitydb/3dcitydbhomepage/) database to create
a materialized view on buildings of the database containing their id, their geometry
and optionnally their year of construction and year of demolition.

#### Use

Activate venv if you created one:
`. venv/bin/activate`

You can run `python extract_city_data.py -h` to display help about this tool.

`extract_city_data.py` takes one mandatory argument and one optionnal argument.

The first one is a configuration file for the database such as `ExtractCityData/db_config.yml`:

```
PG_HOST: <server hosting your db>
PG_USER: <your db user name>
PG_PORT: <port>
PG_PASSWORD: <user password>
PG_NAME: <database name>
MATERIALIZED_VIEW_NAME: <name of the output materialized view>
```

You must fill these information. *Note: `MATERIALIZED_VIEW_NAME` must start with
a letter.*

It also takes an optionnal argument : `-t` or `--temporal`. If set, the materialized
view will also contain the years of constructions and years of demolitions of the
buildings.

*Note: Once created, the view can be refreshed using `REFRESH MATERIALIZED VIEW name`.
More information
 [here](https://www.postgresql.org/docs/9.3/static/sql-refreshmaterializedview.html)*

#### Design

We had the choice between using a view, a materialized view or a new table
(possibly in a new database) to store the output result.

We didn't choose a view because the output needs to be persitent in order to be
used by another program ([py3dtiles](https://github.com/MEPP-team/py3dtiles)).

We chose a materialized view over a new table because the update process is easier
and because we didn't want to modify the database schema of our 3DCityDB database.
In addition,
[it is implemented in PostGIS since v9.3](https://www.postgresql.org/docs/9.4/static/sql-creatematerializedview.html).
