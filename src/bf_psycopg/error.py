class ValidationFailure(Exception):
    '''
    Validation failed.

    This is an internal exception that is never raised outside of the package.
    This is, it is not part of the public API.

    This is not an error!
    '''
