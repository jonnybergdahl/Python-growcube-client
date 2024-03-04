import os
import sys

sys.path.insert(0, os.path.abspath('../'))  # Adjust the path accordingly

extensions = [
    'sphinx.ext.autodoc',
]

# The main document name (master document).
master_doc = 'index'
html_theme = 'sphinx_rtd_theme'
project = 'growcube-client'

