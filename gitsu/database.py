import datetime 
import logging
from contextlib import contextmanager

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists

from gitsu.conf import settings


ENGINES = {}


def get_db_engine(db_connection_name='default'):
    """ Get an engine for a particular db_connection_name

    Engines are best at module level defined once per application. Unless
    you're doing multiprocessing, then one per thread. This uses module 
    level variable `ENGINES` as a cache. 
    (ref: http://docs.sqlalchemy.org/en/latest/core/connections.html)

    Args:
        db_connection_name (str): key which maps to settings.DATABASES

    Returns:
        Engine: engine

    """
    global ENGINES 
    if db_connection_name not in ENGINES:
        ENGINES[db_connection_name] = create_db_engine(db_connection_name)
    return ENGINES[db_connection_name]


def create_db_engine(db_connection_name='default', **create_engine_kws):
    """ Create a new Engine instance using the settings.DATABASES

    A wrapper to sqlalchemy.create_engine which allows the first argument
    to be a database name from settings.DATABASES

        engine = create_engine('default')

    Notes:
        see http://docs.sqlalchemy.org/en/latest/core/connections.html

    """  
    try:
        conn_kws = settings.DATABASES[db_connection_name]
    except KeyError:
        raise KeyError("database '{}' not one of {}".format(
            db_connection_name, tuple(settings.DATABASES.keys()),
        ))
    
    engine_kws = conn_kws.pop('engine_kws', {})
    engine_kws.update(**create_engine_kws)

    try:        
        connection_pattern = (
            '{engine}://{username}:{password}@{host}:{port}/{database}'
        ).format(**conn_kws)
    except KeyError:
        connection_pattern = (
            '{engine}://{filepath}'
        ).format(**conn_kws)
    print(connection_pattern)
    engine = sqlalchemy.create_engine(connection_pattern, **engine_kws)
    
    if conn_kws.get('read_only', False):
        @sqlalchemy.event.listens_for(engine, 'begin')
        def receive_begin(conn):
            conn.execute('SET TRANSACTION READ ONLY')

    return engine 


def db_session(db_connection_name='default', **kws):
    engine = get_db_engine(db_connection_name)
    Session = sessionmaker(bind=engine)
    return Session(**kws)


@contextmanager
def db_session_context(db_connection_name='default', **kws):
    """Provide a transactional scope around a series of operations."""
    session = db_session(db_connection_name, **kws)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def structure_query_results(query_results, data_structure=None):
    rows = query_results.fetchall()
    if len(rows) == 0:
        raise ValueError('no rows returned')
    columns = query_results.keys()        

    if data_structure is None:
        return rows, columns

    elif data_structure == 'dataframe':
        import pandas as pd 
        return pd.DataFrame(rows, columns=columns)

    elif data_structure == 'recarray':
        import numpy as np
        return np.rec.fromrecords(rows, names=columns)

    elif data_structure == 'objects':
        return [dict(zip(columns, row)) for row in rows]
        
    elif data_structure == 'dict':
        data = {}
        for col in columns:
            data[col] = []

        for row in rows:
            for i, el in enumerate(row):
                data[columns[i]].append(el)
        return data 

    else:
        options = (None, 'dataframe', 'recarray', 'objects')
        raise ValueError(
            "invalid parameter '{}' not one of {}"
            .format(data_structure, options)
        )


def db_execute(        
        query, 
        db_connection_name='default',
        params=None, 
        data_structure=None):
    """ For a particular database execute a query and return the result 
    as a pandas dataframe

    Parameters
        db_connection_name (str): name of the database
        query (str): query to execute
        params (dict): parameters to query with
        data_structure (str): format for the return data
            None: (rows, columns)
            'objects': [{column: row}, ...]
            'dataframe': pd.DataFrame
            'recarray': np.recarray
            'dict': {column0: [rows0], ...}


    Notes:
        Async: note if you're applying asyncronosly, you should pass a new
            connection into the db_connection_name not the string. 

    """
    if isinstance(db_connection_name, sqlalchemy.engine.base.Engine):
        db = db_connection_name
    else:
        db = get_db_engine(db_connection_name)
    
    t0 = datetime.datetime.now()    
    params = params or {}
    rs = db.execute(query, **params)
    data = structure_query_results(rs, data_structure)
    dt = datetime.datetime.now() - t0    
    logging.info("query returned {} rows in {}".format(len(data), dt))

    return data

