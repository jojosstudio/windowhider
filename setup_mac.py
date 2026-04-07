"""
Setup script for Window Hider macOS
Builds a .app bundle using py2app
"""

from setuptools import setup

APP = ['windowshider_macos.py']
DATA_FILES = [
    'settings_mac.json',
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter'],
    'includes': ['subprocess', 'json', 'os', 'sys'],
    'excludes': [],
    'iconfile': 'icon_mac.icns',  # macOS icon format
    'plist': {
        'CFBundleName': 'Window Hider',
        'CFBundleDisplayName': 'Window Hider',
        'CFBundleGetInfoString': 'Window Hider for macOS',
        'CFBundleIdentifier': 'com.jojosstudio.windowhider',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2026 Jojosstudio',
        'LSMinimumSystemVersion': '10.12',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='Window Hider',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
