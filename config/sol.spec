# sol.spec
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata
from PyInstaller.building.build_main import Analysis, EXE, PYZ
import os, sys
from pathlib import Path

# Configuration
if not hasattr(sys, '_MEIPASS') and '__file__' not in globals():
    __file__ = sys.argv[0]

ROOT_DIR = Path(__file__).absolute().parent.parent
SRC_DIR = ROOT_DIR / 'src'
ASSETS_DIR = ROOT_DIR / 'assets'
APP_NAME = 'Sol'
UPX_DIR = os.environ.get('UPX_DIR', '')


# Data files and metadata
datas = [
    *collect_all('demucs', include_py_files=False)[0],
    *collect_all('streamlit', include_py_files=False)[0],
    *copy_metadata('streamlit'),
    (str(SRC_DIR /'static/*'), 'static'),
    (str(SRC_DIR /'frontend/styles/*.css'), 'frontend/styles'),
    (str(SRC_DIR /'frontend/scripts/*.js'), 'frontend/scripts'),
    (str(SRC_DIR /'main.py'), '.'),
    (str(SRC_DIR /'config.py'), '.'),
    (str(SRC_DIR /'utils.py'), '.'),
    (str(SRC_DIR /'frontend/*.py'), 'frontend'),
]

# Hidden imports
hiddenimports = [
    *collect_submodules('demucs'),
    *collect_submodules('streamlit.runtime'),
    'numpy.core._multiarray_umath',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'torch._classes',
    'torchaudio._extension',
    'soundfile'
]

# Exclusions
excludes = [
    'pandas', 'scipy', 'matplotlib', 'notebook', 'dask',
    'bokeh', 'flask', 'django', 'IPython', 'pip', 'pywin32-ctypes',
    'pyinstaller-hooks-contrib', 'pyinstaller', 'pefile', 'altgraph',
    'altair', 'jsonschema', 'rpds', 'functorch', 'tkinter', 'markupsafe'
]

# Analysis
a = Analysis(
    [str(SRC_DIR / 'main.py')],
    pathex=['.'],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    upx_dir=UPX_DIR,
    cipher=None
)

# Splash screen
splash = Splash(str(ASSETS_DIR / 'images/splash.png'),
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(20, 330),
                text_size=10,
                text_color='#1c1c1c',
                always_on_top=False)

# Build
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    splash,
    splash.binaries,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,
    upx=True,
    onefile=True,
    icon=str(ASSETS_DIR / 'images/icon.png'),
    console=False
)
