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
        replace_info,
        progress_cb=None,
        pdf_optimized=False)

... where all mandatory parameters have the same meaning that if you have them
in the YAML config (see below), and `progress_cb` is a callback to be called
after processing each item (useful to report progress).


Some usage examples
-------------------

Get the code, and run::

    bin/certg examples/certificate.yaml

The `example_certificate.yaml` is included in the project, with the
other file it uses: `example_certificate.svg`.

After successful execution, you will get three `.pdf` files, the result
of the generation.

Here's other example that inserts different images in the outputs::

    bin/certg examples/carnet.yaml

Finally, if you want to check a code that uses `certg` programatically,
replacing several fields and *multiple* images in the SVG, see
`this real life code <https://github.com/PyAr/asoc/tree/master/carnets>`_.


What do you need to have installed
----------------------------------

The Python's module `yaml` and `Inkscape` in your system. If you want to
optimize the resulting PDF, also need Ghostscript installed (`gs`).


How to really use it, for your specific needs
---------------------------------------------

You need to create two files: the configuration, and the source SVG.
Here's a deep explanation of how it all works, but remember you can
get the examples provided and start tweaking them :)

The source SVG is the SVG you want to transform into PDFs, but with
some indications for text to be replaced in. These indications are
between curly brackets.  For example, you may have::

    Thanks {{name}} for all your {{type_of_doing}}!

Then, in the configuration file you have a `replace_info` variable: it's
a list of dictionaries. Each dictionary will produce a generated PDF with
the info replaced, and the keys/values in that dictionary will be the
info to replace.

Note that you need to provide in the config all the attributes to
replace; for example::

    name: Foo Bar
    type_of_doing: support

Furthermore, in the config you have some mandatory variables you need
to fill. Those are:

- `svg_source`: the filename of the SVG you created

- `result_prefix`: the prefix of the PDFs' filenames that will
  be generated

- `result_distinct`: the name of the variable in the replacing
  attributes used as a distinct string for the PDFs.

For example, if you put `certs` as the prefix and `name` as the
distinct value, you'll get as output a file named `certs-foobar.pdf`.

There are some optional variables for different configurations, currently:

- `pdf_optimized`: it will run Ghoscript (`gs`, which you need to have
  installed in the system) to optimize the resulting PDF.
