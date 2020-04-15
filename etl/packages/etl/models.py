import datetime
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import ForeignKey, exists, and_
from sqlalchemy.orm import relationship

from etl import database, errors


class Query:

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.session = None

    def check_session(self):
        if self.session is None:
            raise errors.ProgrammingError(
                'Need to provide a session. Call self.with_session(session)'
            )

    def exists(self, **kws):
        self.check_session()
        for i, (k, v) in enumerate(kws.items()):
            check = (getattr(self.model_cls, k) == v)
            if i == 0:
                q = check
            else:
                q &= check
        return self.session.query(exists().where(q)).scalar()

    def get(self, key):
        self.check_session()
        return self.session.query(self.model_cls).get(key)

    def get_or_create(self, key, **kws):
        self.check_session()
        obj = self.get(key)
        created = obj is None
        if created:
            obj = self.model_cls(**kws)
            self.session.add(obj)
        return obj, created

    def exists_or_create(self, **kws):
        self.check_session()
        created = not self.exists(**kws)
        obj = None
        if created:
            obj = self.model_cls(**kws)
            self.session.add(obj)
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

    def filter(self, **kws):
        self.check_session()
        clause = self.filter_clause(**kws)
        return self.session.query(self.model_cls).filter(clause)

    def with_session(self, session=None, **kws):
        if session is None:
            session = database.db_session(**kws)
        self.session = session
        return self

    def __call__(self, session=None):
        return self.with_session(session)


class Meta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        # Reason for using a semi-private here was to follow
        # the SQLAlchemy pattern where all attributes except metadata which
        # binds inconsistently.
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
    user_ext_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    user_events = relationship("GitHubIssueEvent", back_populates='event_user')
    user_issues = relationship("GitHubIssue", back_populates='issue_user')
    dw_row_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_row_updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class GitHubRepo(Base):
    __tablename__ = 'github_repo'
    repo_id = Column(String, primary_key=True)
    repo_name = Column(String)
    repo_organization_name = Column(String)
    dw_row_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_row_updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class GitHubIssue(Base):
    __tablename__ = 'github_issue'
    issue_ext_id = Column(Integer, primary_key=True)
    issue_state = Column(String)
    issue_comments = Column(Integer)
    issue_events = relationship("GitHubIssueEvent", back_populates='event_issue')  # noqa
    issue_created_at = Column(DateTime)
    issue_closed_at = Column(DateTime)
    issue_updated_at = Column(DateTime)
    issue_user_ext_id = Column(Integer, ForeignKey('github_user.user_ext_id'))
    issue_user = relationship("GitHubUser", back_populates="user_issues")
    issue_is_pull_request = Column(Boolean)
    issue_events_url = Column(String)
    issue_events_last_loaded_at = Column(DateTime)
    dw_row_created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dw_row_updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class GitHubIssueEvent(Base):
    __tablename__ = 'github_issue_event'
    event_ext_id = Column(Integer, primary_key=True)
    event_issue_ext_id = Column(Integer, ForeignKey('github_issue.issue_ext_id'))  # noqa
    event_issue = relationship("GitHubIssue", back_populates="issue_events")
    event_created_at = Column(DateTime)
    event_label = Column(String)
    event = Column(String)
    event_user_ext_id = Column(Integer, ForeignKey('github_user.user_ext_id'))
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
