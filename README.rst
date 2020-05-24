certg
=====

A certificate generator, from a SVG to a lot of PDFs

How to use it as a lib
----------------------

Install certg from PyPI and then...

::

    >>> import certg
    >>> certg.process(
        svg_source,
        result_prefix,
        result_distinct,
        replace_info)

... where all those mandatory parameters have the same meaning that if you 
have them in the YAML config (see below).

Optionally, you can also pass the following parameters:

- ``progress_cb``: a function to be called before processing each item (passing 
  the item about to be processed); very useful to report progress.

- ``pdf_optimized``: if True, Ghostscript will be called to improve the 
  final PDF file.

- ``images``: replacing information for images (see below)


Some usage examples
-------------------

Get the code, and run::

    bin/certg examples/certificate.yaml

The ``example_certificate.yaml`` is included in the project, with the
other file it uses: ``example_certificate.svg``.

After successful execution, you will get three ``.pdf`` files, the result
of the generation.

Here's other example that inserts different images in the outputs::

    bin/certg examples/carnet.yaml

Finally, if you want to check a code that uses ``certg`` programatically,
replacing several fields and *multiple* images in the SVG, see
`this real life code <https://github.com/PyAr/asoc/tree/master/carnets>`_.


What do you need to have installed
----------------------------------

Check ``requirements.txt`` file for needed Python modules.

At system level, you need ``Inkscape`` to be installed. Also, if you want to
optimize the resulting PDF, you need Ghostscript installed (``gs``).


How to really use it, for your specific needs
---------------------------------------------

You need to create two files: the configuration, and the source SVG.
Here's a deep explanation of how it all works, but remember you can
get the examples provided and start tweaking them :)

The source SVG is the SVG you want to transform into PDFs, but with
some indications for text to be replaced in. These indications are
between curly brackets.  For example, you may have::

    Thanks {{name}} for all your {{type_of_doing}}!

Then, in the configuration file you have a ``replace_info`` variable: it's
a list of dictionaries. Each dictionary will produce a generated PDF with
the info replaced, and the keys/values in that dictionary will be the
info to replace.

Note that you need to provide in the config all the attributes to
replace; for example::

    name: Foo Bar
    type_of_doing: support

Furthermore, in the config you have some mandatory variables you need
to fill. Those are:

- ``svg_source``: the filename of the SVG you created

- ``result_prefix``: the prefix of the PDFs' filenames that will
  be generated

- ``result_distinct``: the name of the variable in the replacing
  attributes used as a distinct string for the PDFs.

For example, if you put ``certs`` as the prefix and ``name`` as the
distinct value, you'll get as output a file named ``certs-foobar.pdf``.

There are some optional variables for different configurations, currently:

- ``pdf_optimized``: it will run Ghoscript (``gs``, which you need to have
  installed in the system) to optimize the resulting PDF.


Replacing images
----------------

If you want to replace images, you need to indicate a separate ``images`` 
structure that will provide the relevant info.

This structure will be a list containing as many items as images you want
to replace in the SVG file (NOT the quantity of PDFs you want to 
generate). Each item will be a dict holding:

- ``rectangle_id``: the id in the SVG of the rectangle you want 
  to replace (e.g. 'rect19351'); you can get it seeing the "object 
  properties" in Inkscape, or as a last resource inspecting the SVG source.

- ``path_variable``: how are you naming the attribute (in the general
  replacing information described above) that will hold the path to the 
  image to be replaced for each of the PDFs you want to generate.

Optionally:

- ``placement``: how the real image will be placed in relation to the 
  rectangle defined in the SVG. In any case, the image will not exceed the
  boundaries defined by the rectangle. It can be any of the following:

  - ``stretch`` (the default): the image will be accommodated to fill the 
    whole rectangle, changing its relation aspect if needed.

  - ``center``: the image's center will match the rectangle's center
