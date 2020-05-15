# -*- coding: utf-8 -*-
"""compute_versionData_from_py3DFiles.ipynb


@Author : Thibaut Chataing   
@Date : 12/05/2020
# Script for UD-CPOV POC

This script should :
1. Load tileset.json
2. Extract information to compile versions and versionTransitions
3. Create a new tileset.json with the versions and versionTransitions data
"""

# Link the cloud to the script to access the data

# !pip install warlock

import warlock
import json
import os
import pandas as pd
import numpy as np

debug = True
def log(msg):
  if debug:
    print(msg)

"""## 1. Load tileset.json and *.b3dm data
### a. tileset.json
"""

# load data
startDate = 0
endDate = 2999
list_transactions = []
with open('./data/tileset.json') as json_file:
  data = json.load(json_file)
  startDate = data['extensions']['3DTILES_temporal']['startDate']
  endDate = data['extensions']['3DTILES_temporal']['endDate']
  list_transactions = data['extensions']['3DTILES_temporal']['transactions']

  log(f"startDate = {startDate} \nendDate = {endDate}\nlist_transactions = {list_transactions}")

# Format data
transactions = pd.DataFrame(list_transactions, columns=["id", "startDate", "endDate", "source", "destination", "type", "transactions"])

#TODO préciser les types de chaque colonnes

#Auto detect of type
transactions = transactions.convert_dtypes()

#Separate aggregated transactions
transactions_simple = transactions.loc[transactions['transactions'].isna()]
transactions_agg = transactions.loc[transactions['transactions'].notna()]

log(transactions.describe(include=['string', "Int64"]))

"""## 2. Create versions and versionTransitions"""

"""
# Extracte from a DataFrame all the IDs of the batiment that should be present in the version.
# The extraction is based on the transactions (trasnformation of a batiment between two times)
# A version represents a year (ex: 2009, 2012, 2015)
# When a transition start at or before the year and end after we take the source id
# When a transition end at the year we take the destination id
#
# @Param:
#   transaction : DataFrame 
#   millesime : int (year)
# @return: a set of the ids (with unicity)
"""
def get_featuresid(transactions, millesime):
  ret = {"version":set(), "versionTr":set()}

  tr = transactions.loc[(transactions['startDate'] <= millesime) & (transactions['endDate'] > millesime)] # Filter only transactions that start in the millesime or before and end strictly after
  a = get(tr, "source", millesime)
  ret['version'].update(a['version'])
  ret['versionTr'].update(a['versionTr'])

  b = len(ret['version'])
  c = len(ret['versionTr'])
  log(f"simple tr : version= {b} - versionTR= {c}")
  
  tr = transactions.loc[(transactions['startDate'] < millesime) & (transactions['endDate'] == millesime)] # Filter only transactions that start striclty before the millesime  and end at it
  a = get(tr, "destination", millesime)
  ret['version'].update(a['version'])
  ret['versionTr'].update(a['versionTr'])

  log(f"agg tr : version= {len(ret['version']) - b} - versionTR= {len(ret['versionTr']) - c}")
  
  log(f"featuresIds found :  version= {len(ret['version'])} - versionTR= {len(ret['versionTr'])}")
  log(f"Details : {ret}")
  return ret

def get(df, row_name, millesime):
  ret = {'version':set(), 'versionTr':set()} # set for batiment's id and transition's id to have unicity
  for index, row in df.iterrows():
    ret['versionTr'].add(row['id'])
    for s in row[row_name]:
      ret['version'].add(s) #take the source
      
    if row['transactions']==row['transactions']: # separate simple and aggregate transactions (simple has NaN value in the transactions attribut)
      l = row['transactions']
      for tr in l:
        if (tr['startDate'] <= millesime < tr['endDate']) : # filter by security in the transaction aggregated
          ret['versionTr'].add(tr['id'])
          for s in tr['source']:
            ret['version'].add(s)
        elif (tr['startDate'] < millesime == tr['endDate']):
          ret['versionTr'].add(tr['id'])
          for s in tr['destination']:
            ret['version'].add(s)
  return ret



schema_version_path = './data/3DTILES_temporal.version.schema.schema.json'
schema_versionTransition_path = './data/3DTILES_temporal.versionTransition.schema.json'

Version = 0
VersionTransition = 0
with open(schema_version_path) as json_file:
  data = json.load(json_file)
  Version = warlock.model_factory(data) 

with open(schema_versionTransition_path) as json_file:
  data = json.load(json_file)
  VersionTransition = warlock.model_factory(data)

v1 = Version(id="v1",
             name="2009",
             description="Limonest state in 2009 for the concurrent point of view",
             startDate="2009",
             endDate="2010",
             tags=["concurrent"],
             featuresIds=list(get_featuresid(transactions, 2009)['version']))

v2 = Version(id="v2",
             name="2012",
             description="Limonest state in 2012 for the concurrent point of view",
             startDate="2012",
             endDate="2013",
             tags=["concurrent"],
             featuresIds=list(get_featuresid(transactions, 2012)['version']))

v3 = Version(id="v3",
             name="2015",
             description="Limonest state in 2015 for the concurrent point of view",
             startDate="2015",
             endDate="2016",
             tags=["concurrent"],
             featuresIds=list(get_featuresid(transactions, 2015)['version']))

vt_v1_v2 = VersionTransition({"id":"vt1",
                             "name":"v1->v2",
                             "startDate":"2009",
                             "endDate":"2012",
                             "from":"v1",
                             "to":"v2",
                             "description":"Transition between v1 and v2",
                             "type":"realized",
                             "transactionsIds":list(get_featuresid(transactions, 2009)['versionTr'])})

vt_v2_v3 = VersionTransition({"id":"vt2",
                             "name":"v2->v3",
                             "startDate":"2012",
                             "endDate":"2015",
                             "from":"v2",
                             "to":"v3",
                             "description":"Transition between v2 and v3",
                             "type":"realized",
                             "transactionsIds":list(get_featuresid(transactions, 2012)['versionTr'])})

with open('./data/tileset.json') as json_file:
  data = json.load(json_file)

data['extensions']['3DTILES_temporal']['versions'] = [v1, v2, v3]
data['extensions']['3DTILES_temporal']['versionTransitions'] = [vt_v1_v2, vt_v2_v3]

with open('./data/new_tileset.json', "w") as json_file:
  json.dump(data, json_file)

log('done')

"""# TO SOLVE

* Should version has a start and end date or only a moment of existence ?
* What to do with aggregated transition ? for the moment (pop)
"""