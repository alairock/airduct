import os
import logging as lo


LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
lo.basicConfig(level=LOGLEVEL)

logger = lo.getLogger()
