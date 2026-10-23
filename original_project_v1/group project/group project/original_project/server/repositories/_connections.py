"""Connection helper shared by the repositories."""

from contextlib import contextmanager


@contextmanager
def connection_scope(db, connection=None):
    """Yield a connection to run SQL against.

    When ``connection`` is provided, the caller owns the transaction and this
    helper simply yields it unchanged. When it is ``None``, a new connection is
    opened through ``db.connection()``, which commits on success, rolls back on
    error, and always closes the connection.

    This lets a Service run several repository operations inside one
    transaction (for example, order creation) without the repositories having
    to know anything about the transaction lifecycle.
    """
    if connection is not None:
        yield connection
        return
    with db.connection() as conn:
        yield conn
