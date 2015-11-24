#!/usr/bin/env python3

import logging, sys
from app import app

LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=LOG_FORMAT)

app.run(host='0.0.0.0', port=4000, debug=True)
