from contextlib import contextmanager

from neo4j import GraphDatabase, READ_ACCESS

from ..definitions import DbContext


class Neo4jUtils:
    @classmethod
    @contextmanager
    def acquire_tx(cls, *, db_context: DbContext):
        driver = GraphDatabase.driver(db_context.host, auth=(db_context.username, db_context.password))
        with driver.session(default_access_mode=READ_ACCESS, database=db_context.database) as session:
            tx = session.begin_transaction()

            try:
                yield tx

            except Exception as e:
                raise

            finally:
                tx.close()
