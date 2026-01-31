"""
SitesHelper wrapper - bypasses user authentication while preserving all other functionality.
"""
import importlib.util
from pathlib import Path
from typing import Tuple, Dict, Any

# Load the original compiled SitesHelper
_original_module = None
_OriginalSitesHelper = None


def _load_original():
    global _original_module, _OriginalSitesHelper
    if _OriginalSitesHelper is not None:
        return

    helper_dir = Path(__file__).parent
    # Actual compiled module filenames (from MoviePilot-Resources):
    # - sites.cp312-win_amd64.pyd (Windows)
    # - sites.cpython-312-aarch64-linux-gnu.so (Linux ARM64)
    # - sites.cpython-312-darwin.so (macOS)
    # - sites.cpython-312-x86_64-linux-gnu.so (Linux x86_64)
    patterns = [
        'sites.cpython-312-darwin.so',            # macOS
        'sites.cpython-312-x86_64-linux-gnu.so',  # Linux x86_64
        'sites.cpython-312-aarch64-linux-gnu.so', # Linux ARM64
        'sites.cp312-win_amd64.pyd',              # Windows
    ]

    for filename in patterns:
        compiled_path = helper_dir / filename
        if compiled_path.exists():
            spec = importlib.util.spec_from_file_location("_sites_original", compiled_path)
            _original_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_original_module)
            _OriginalSitesHelper = _original_module.SitesHelper
            return

    raise ImportError("Cannot find compiled sites module (sites.cpython-*.so or sites.*.pyd)")


class SitesHelper:
    """Wrapper around original SitesHelper - bypasses auth_level and check_user"""

    def __init__(self):
        _load_original()
        self._original = _OriginalSitesHelper()

    @property
    def auth_level(self) -> int:
        """Always return level 2 (authenticated)"""
        return 2

    def check_user(self, site: str = None, params: Dict = None) -> Tuple[bool, str]:
        """Always return success"""
        return True, "Authentication bypassed"

    def __getattr__(self, name: str) -> Any:
        """Delegate all other attributes/methods to original"""
        return getattr(self._original, name)
