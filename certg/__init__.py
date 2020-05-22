# Copyright 2013-2020 Facundo Batista

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
import enum

from PIL import Image

Placement = enum.Enum('Placement', 'stretch center')


def get_gs_cmd(srcpath, dstpath):
    """Build the command for Ghoscript to optimize a PDF."""
    cmd = [
        '/usr/bin/gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', '-dPDFSETTINGS=/default',
        '-dNOPAUSE', '-dBATCH', '-dQUIET', '-sOutputFile={}'.format(dstpath), srcpath]
    return cmd


def get_inkscape_cmd(srcpath, dstpath):
    """Build the command for Inkscape to convert the SVG into PDF."""
    cmd = ['inkscape', '--export-text-to-path', '--export-pdf={}'.format(dstpath), srcpath]
    return cmd


def replace_images(content, image_info_raw, replacement_data):
    """Replace all the rectangles in the SVG for the specified images."""
    # add the xlink namespace
    content = content.replace("<svg", '<svg\n   xmlns:xlink="http://www.w3.org/1999/xlink"\n', 1)

    # preprocess the image info
    image_info = {}
    for item in image_info_raw:
        p = item.get('placement')
        placement = Placement.stretch if p is None else Placement[p]
        rectangle_id = item.get('rectangle_id', item['placement_rectangle_id'])  # backw' compat
        image_info[rectangle_id] = (replacement_data[item['path_variable']], placement)

    def mutate(match):
        params_all = dict(re.findall(r'(\w+)="?([\w\.\-]+)"?', match.groups()[0]))
        useful = {'id', 'width', 'height', 'x', 'y'}
        params = {k: v for k, v in params_all.items() if k in useful}

        if params['id'] not in image_info:
            # not the object we were searching for mutation, return the original sequence
            return match.string[slice(*match.span())]

        image_path, image_placement = image_info[params['id']]
        new_params = [
            'xlink:href="file://{}"'.format(image_path),
            'preserveAspectRatio="none"',
        ]

        # Fix params (if needed) according to placement option; by default the previous
        # coordinates will prevail, which will make placed images to stretch to drawn rectangle
        if placement == Placement.center:
            rect_w = float(params['width'])
            rect_h = float(params['height'])
            image_w, image_h = Image.open(image_path).size

            # Try to fit it according to it's width; if didn't work fit
            # it according to it's height
            new_width = rect_w
            new_height = image_h * rect_w / image_w
            if new_height > rect_h:
                new_height = rect_h
                new_width = image_w * rect_h / image_h

            # Center the image in the rectangle (note that x/y and
            # new_x/new_y are upper left corners)
            new_x = float(params['x']) + (rect_w - new_width) / 2
            new_y = float(params['y']) + (rect_h - new_height) / 2

            # replace info in params
            params.update({
                'width': new_width,
                'height': new_height,
                'x': new_x,
                'y': new_y,
            })

        new_params.extend('{}="{}"'.format(k, v) for k, v in params.items())
        return "<image {} />".format(" ".join(new_params))

    content = re.sub("<rect(.*?)>", mutate, content, flags=re.DOTALL)
    return content


def process(
        svg_source, result_prefix, result_distinct, replace_info, images=None, progress_cb=None,
        pdf_optimized=False):
    """Generate N PDFs.

    Each PDF is from a key in replace_info, replacing data into the
    svg_source, and naming each PDF according to result_*.

    Before each PDF progress_cb (if any) will be called to indicate progress.

    If pdf_optimized in True, Ghostscript will be called to improve the final file.
    """
    with open(svg_source, "rt", encoding='utf8') as fh:
        content_base = fh.read()

    # get all the replacing attrs
    replacing_attrs = set()
    for data in replace_info:
        replacing_attrs.update(data.keys())

    fileresults = []
    for data in replace_info:
        # indicate advance, if should
        if progress_cb is not None:
            progress_cb(data)

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
            content = replace_images(content, images, data)

        # write the new svg
        _, tmpfile = tempfile.mkstemp(suffix='.svg')
        with open(tmpfile, "wt", encoding='utf8') as fh:
            fh.write(content)

        # generate PDF
        distinct = data[result_distinct].lower().replace(" ", "")
        final_pdf = "{}-{}.pdf".format(result_prefix, distinct)
        fileresults.append(final_pdf)
        if pdf_optimized:
            _, pdf_by_inkscape = tempfile.mkstemp(suffix='.pdf')
            pdf_by_gs = final_pdf
        else:
            # inkscape generates directly the final PDF
            pdf_by_inkscape = final_pdf

        cmd = get_inkscape_cmd(tmpfile, pdf_by_inkscape)
        subprocess.check_call(cmd)
        os.remove(tmpfile)

        if pdf_optimized:
            # optimize the PDF generated by inkscape
            cmd = get_gs_cmd(pdf_by_inkscape, pdf_by_gs)
            subprocess.check_call(cmd)
            os.remove(pdf_by_inkscape)

    return fileresults
