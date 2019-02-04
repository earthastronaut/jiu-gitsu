import datetime
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import ForeignKey, exists, and_, or_
from sqlalchemy.orm import relationship

from gitsu import database


def with_default_session(func):
    def func_with_default_session(self, _session=None, *args, **kws):
        if _session is None:
            with database.db_session_context() as session:
                return func(self, _session=session, *args, **kws)
        else:
            return func(self, _session=_session, *args, **kws)
    return func_with_default_session


class Query:

    def __init__(self, model_cls):
        self.model_cls = model_cls

    @with_default_session
    def exists(self, _session=None, **kws):
        for i, (k, v) in enumerate(kws.items()):
            check = (getattr(self.model_cls, k) == v)
            if i == 0:
                q = check
            else:
                q &= check
        return _session.query(exists().where(q)).scalar()

    @with_default_session
    def get(self, key, _session=None):
        return _session.query(self.model_cls).get(key)

    @with_default_session
    def get_or_create(self, key, _session=None, **kws):
        obj = self.get(key, _session=_session)
        created = obj is None
        if created:
            obj = self.model_cls(**kws)
            _session.add(obj)
        return obj, created

    @with_default_session
    def exists_or_create(self, _session=None, **kws):
        created = not self.exists(_session=_session, **kws)
        obj = None
        if created:
            obj = self.model_cls(**kws)
            _session.add(obj)        
        return obj, created

    def filter_clause(self, **kws):
        op_to_attr = {
            'eq': '__eq__',
            'is': 'is_',
            'isnot': 'isnot',
            'ne': '__ne__',
            'like': 'like',
            'ilike': 'ilike',
            'in': 'in_',
            'gt': '__gt__',
            'lt': '__lt__',
        }
        clauses = []
        for field_op, value in kws.items():
            split_field_op = field_op.split('__')
            field = split_field_op[0]

            if len(split_field_op) == 1:                
                op = 'eq'
            elif len(split_field_op) == 2:
                op = split_field_op[1]
            else:
                raise ValueError(
                    'field_op \'{}\' formatted incorrectly'.format(field_op)
                )

            attr = op_to_attr[op]
            operator = getattr(
                getattr(self.model_cls, field),
                attr,
            )
            clauses.append(
                operator(value)
            )
        return and_(*clauses)

    @with_default_session
    def filter(self, _session=None, **kws):
        clause = self.filter_clause(**kws)
        return _session.query(self.model_cls).filter(clause)


class Meta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        cls._query = Query(cls)
        super().__init__(classname, bases, dict_)


Base = declarative_base(
    metaclass=Meta,
)


class GitHubUser(Base):
    """
    CREATE TABLE IF NOT EXISTS public.user (
        user_id INTEGER PRIMARY KEY
        , user_login VARCHAR(64)
    );
    """    
    __tablename__ = 'github_user'
    user_id = Column(Integer, primary_key=True)
    user_ext_id = Column(Integer)
    user_name = Column(String)
    user_events = relationship("GitHubIssueEvent", back_populates='event_user')
    dw_row_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_row_updated_at = Column(DateTime, default=datetime.datetime.utcnow)



class GitHubRepo(Base):
    __tablename__ = 'github_repo'
    repo_id = Column(Integer, primary_key=True)
    repo_name = Column(String)
    repo_organization_name = Column(String)
    dw_row_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_row_updated_at = Column(DateTime, default=datetime.datetime.utcnow)



class GitHubIssue(Base):
    """
    CREATE TABLE IF NOT EXISTS public.issue (
        issue_id INTEGER PRIMARY KEY
        , issue_state VARCHAR(16) NOT NULL
        , issue_comments INTEGER DEFAULT 0
        , issue_created_at TIMESTAMP WITH TIME ZONE NOT NULL
        , issue_closed_at TIMESTAMP WITH TIME ZONE
        , issue_is_pull_request BOOLEAN
        , issue_events_url TEXT
    );
    """   
    __tablename__ = 'github_issue'
    issue_id = Column(Integer, primary_key=True)
    issue_ext_id = Column(Integer)    
    issue_state = Column(String)
    issue_comments = Column(Integer)
    issue_events = relationship("GitHubIssueEvent", back_populates='event_issue')
    issue_created_at = Column(DateTime)
    issue_closed_at = Column(DateTime)
    issue_updated_at = Column(DateTime)
    issue_is_pull_request = Column(Boolean)
    issue_events_url = Column(String)
    issue_events_last_loaded_at = Column(DateTime)
    dw_row_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_row_updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class GitHubIssueEvent(Base):
    """
    CREATE TABLE IF NOT EXISTS public.event (
        event_id INTEGER PRIMARY KEY
        , event VARCHAR(32)    
        , event_issue_id INTEGER REFERENCES public.issue(issue_id)
        , event_actor_id INTEGER REFERENCES public.user(user_id)
        , event_actor_login VARCHAR(64)
        , event_data JSON NULL
    );
    """
    __tablename__ = 'github_issue_event'
    event_id = Column(Integer, primary_key=True)    
    event_ext_id = Column(Integer)
    event_issue_id = Column(Integer, ForeignKey('github_issue.issue_id'))
    event_issue = relationship("GitHubIssue", back_populates="issue_events")

    event_user_id = Column(Integer, ForeignKey('github_user.user_id'))
    event_user = relationship("GitHubUser", back_populates="user_events")
    dw_row_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_row_updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class DataLake(Base):
    """
    CREATE TABLE IF NOT EXISTS public.raw_data (
        key STRING PRIMARY KEY
        value JSON NULL
    )
    """    
    __tablename__ = 'data_lake'
    key = Column(String, primary_key=True)
    schema = Column(String)
    data = Column(JSONB)
    dw_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_etl_at = Column(DateTime)
    dw_etl_job_name = Column(String)
