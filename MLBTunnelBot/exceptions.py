class EmptyStatcastDFException(Exception):
    """
    Raised when yesterdays statcast data is empty.
    This can happen if there were no games yesterday,
    or the script was run too early (before statcast has been updated).
    """

    pass
