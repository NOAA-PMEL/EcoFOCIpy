#
"""Tools for versioning."""


def get_version():
    """Get EcoFOCIpy's version.

    Either get it from package metadata, or get it using version control information if
    a development install.
    """
    try:
        from setuptools_scm import get_version
        return get_version(root='../..', relative_to=__file__,
                           version_scheme='post-release')
    except (ImportError, LookupError):
        try:
            from importlib.metadata import version, PackageNotFoundError
        except ImportError:  # Can remove when we require Python > 3.7
            from importlib_metadata import version, PackageNotFoundError

        try:
            return version(__package__)
        except PackageNotFoundError:
            return 'Unknown'
