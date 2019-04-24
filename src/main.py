#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import core

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)


if __name__ == "__main__":
    core.run()
