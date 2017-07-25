#!/usr/bin/env fades

# Copyright 2013-2017 Facundo Batista

# This file is GPL v3, part of http://github.com/facundobatista/certg
# project; refer to it for more info.

# This script is run by fades, which runs it automagically inside a
# virtualenv, for more info check http://fades.readthedocs.io/

import os
import subprocess
import sys
import tempfile

import yaml  # fades
from progress import bar  # fades


if len(sys.argv) != 2:
    print("Usage: {} <config.yaml>".format(sys.argv[0]))
    exit()

with open(sys.argv[1], 'rt', encoding='utf8') as fh:
    config = yaml.load(fh)

with open(config['svg_source'], "rt", encoding='utf8') as fh:
    content_base = fh.read()

# get all the replacing attrs
replacing_attrs = set()
for data in config['replace_info']:
    replacing_attrs.update(data)

progress_bar = bar.Bar("Processing", max=len(config['replace_info']))

for data in config['replace_info']:
    # indicate advance
    progress_bar.next()

    # replace content
    content = content_base
    for attr in replacing_attrs:
        value = data.get(attr)
        if value is None:
            # both because the attr is not supplied, or supplied empty
            value = ""
        content = content.replace("{{" + attr + "}}", value)

    # write the new svg
    _, tmpfile = tempfile.mkstemp(suffix='.svg')
    with open(tmpfile, "wt", encoding='utf8') as fh:
        fh.write(content)

    # generate PDF
    distinct = data[config['result_distinct']].lower().replace(" ", "")
    result = "{}-{}.pdf".format(config['result_prefix'], distinct)

    cmd = ['inkscape', '--export-text-to-path', '--export-pdf={}'.format(result), tmpfile]
    subprocess.check_call(cmd)
    os.remove(tmpfile)

progress_bar.finish()
