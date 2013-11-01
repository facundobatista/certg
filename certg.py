#!/usr/bin/env python3

# Copyright 2013 Facundo Batista
# This file is GPL v3, part of http://github.com/facundobatista/certg
# project; refer to it for more info.

import subprocess
import sys
import tempfile

import yaml


if len(sys.argv) != 2:
    print("Usage: {} <config.yaml>".format(sys.argv[0]))
    exit()

with open(sys.argv[1], 'rt') as fh:
    config = yaml.load(fh)

with open(config['svg_source'], "rt") as fh:
    content_base = fh.read()

# get all the replacing attrs
replacing_attrs = set()
for data in config['replace_info']:
    replacing_attrs.update(data)

for data in config['replace_info']:

    # replace content
    content = content_base
    for attr in replacing_attrs:
        value = data.get(attr)
        if value is None:
            # both because the attr is not supplied, or supplied empty
            value = ""
        content = content.replace("{{" + attr + "}}", value)

    # write the new svg
    _, tmpfile = tempfile.mkstemp()
    with open(tmpfile, "wt") as fh:
        fh.write(content)

    # generate PDF
    distinct = data[config['result_distinct']].lower().replace(" ", "")
    result = "{}-{}.pdf".format(config['result_prefix'], distinct)

    cmd = ['inkscape', '--export-pdf={}'.format(result), tmpfile]
    subprocess.check_call(cmd)
