# Copyright 2013-2017 Facundo Batista

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  http://github.com/facundobatista/certg

import os
import re
import subprocess
import tempfile
import uuid


def pre_process_image(content, place_id):
    """Preprocess a SVG changing a rect for an image, to be filled by replacing a specific var."""
    replace_var = uuid.uuid4().hex

    def mutate(match):
        params = match.groups()[0].split()
        params = [p for p in params if p.startswith(("id=", "width=", "height=", "x=", "y="))]
        params.append('xlink:href="file://{}"'.format(replace_var))
        params.append('preserveAspectRatio="none"')
        return "<image {} />".format(" ".join(params))

    content = re.sub("<rect(.*?)>", mutate, content, flags=re.DOTALL)
    return content, replace_var


def process(svg_source, result_prefix, result_distinct, replace_info, images, progress_cb=None):
    """Generate N PDFs.

    Each PDF is from a key in replace_info, replacing data into the
    svg_source, and naming each PDF according to result_*.

    After each PDF progress_cb (if any) will be called to indicate progress.
    """
    with open(svg_source, "rt", encoding='utf8') as fh:
        content_base = fh.read()

    if images is not None:
        place_id = images['placement_rectangle_id']
        image_path_variable = images['path_variable']
        content_base, replacement_variable = pre_process_image(content_base, place_id)

    # get all the replacing attrs
    replacing_attrs = set()
    for data in replace_info:
        replacing_attrs.update(data)

    for data in replace_info:
        # indicate advance, if should
        if progress_cb is not None:
            progress_cb()

        # replace content
        content = content_base
        for attr in replacing_attrs:
            value = data.get(attr)
            if value is None:
                # both because the attr is not supplied, or supplied empty
                value = ""
            content = content.replace("{{" + attr + "}}", value)

        # replace image, if any
        if images is not None:
            image_path = os.path.abspath(data[image_path_variable])
            content = content.replace(replacement_variable, image_path)

        # write the new svg
        _, tmpfile = tempfile.mkstemp(suffix='.svg')
        with open(tmpfile, "wt", encoding='utf8') as fh:
            fh.write(content)

        # generate PDF
        distinct = data[result_distinct].lower().replace(" ", "")
        result = "{}-{}.pdf".format(result_prefix, distinct)

        cmd = ['inkscape', '--export-text-to-path', '--export-pdf={}'.format(result), tmpfile]
        subprocess.check_call(cmd)
        os.remove(tmpfile)
