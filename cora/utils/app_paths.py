import os
import sys


def is_frozen():
    """True when running from a PyInstaller bundle (e.g. CORA.app)."""
    return getattr(sys, 'frozen', False)


def user_data_dir():
    """Directory for data CORA writes at runtime.

    A bundled app cannot write next to its own executable: the .app lives in
    /Applications (and is read-only when run straight from the DMG), and
    writing inside the bundle would invalidate its signature. When frozen we
    use the platform's per-user location instead. When running from a source
    checkout the project directory is kept, so development behaviour is
    unchanged.
    """
    if not is_frozen():
        return project_dir()

    if sys.platform == 'darwin':
        base = os.path.expanduser('~/Library/Application Support')
    elif sys.platform == 'win32':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
    else:
        base = os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share')

    path = os.path.join(base, 'CORA')
    os.makedirs(path, exist_ok=True)
    return path


def project_dir():
    """Root of the source checkout."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def bundled_resource_dir():
    """Directory holding read-only files shipped with the app."""
    return getattr(sys, '_MEIPASS', project_dir())


def user_path(*parts):
    """Path inside the writable user data directory."""
    return os.path.join(user_data_dir(), *parts)
