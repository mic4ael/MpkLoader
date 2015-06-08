#!/usr/bin/env python

from .daemon import MpkLoader


def run():
    instance = MpkLoader()
    instance.run()