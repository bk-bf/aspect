"""Copyright header linter test for aspect_navigation."""

from ament_copyright.main import main
import pytest


@pytest.mark.skip(reason='Copyright headers will be added once template is finalised.')
@pytest.mark.copyright
@pytest.mark.linter
def test_copyright():
    """Check that all source files carry an Apache 2.0 copyright header."""
    rc = main(argv=['.', 'test'])
    assert rc == 0, 'Found errors'
