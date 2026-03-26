"""pep257 docstring linter test for aspect_control."""

from ament_pep257.main import main
import pytest


@pytest.mark.linter
@pytest.mark.pep257
def test_pep257():
    """Check PEP 257 docstring compliance."""
    rc = main(argv=['.', 'test'])
    assert rc == 0, 'Found code style errors / warnings'
