#!/usr/bin/env python3

import sys
import uuid

username = sys.argv[1]
tag = uuid.uuid4()

print(f"{username}-{tag}")
