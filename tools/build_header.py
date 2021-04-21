#!/usr/bin/env python3

import sys
from pycparser import parse_file, c_generator


def usage():
    sys.stderr.write("Usage:\n")
    sys.stderr.write("    build_header.py <odc.h> <odc_cffi.h>\n")


if len(sys.argv) != 3:
    usage()
    sys.exit(-1)

input_filename = sys.argv[1]
output_filename = sys.argv[2]

ast = parse_file(input_filename, use_cpp=True)
with open(output_filename, "w") as f:
    f.write(c_generator.CGenerator().visit(ast))
