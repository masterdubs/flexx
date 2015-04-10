""" Script to generate glyph atlas texture.

This bit of code requires numpy and vispy, and should probably be run
at a Linux system (to take advantage of freetype).

"""

import os

import numpy as np
from vispy.util import fonts
import imageio


# Define font
font = {'face': 'DejaVu Sans Mono',
        'bold': False,
        'italic': False,
        'size': 14,
        }

# Define atlas
glyph_size = 16
tex_width = 512
glyphs_on_a_row = tex_width // glyph_size

# Define characters to pack
ranges = [(0, 1),
          (32, 127),
         ]


# Generate glyphs
glyphs = {}
for ra in ranges:
    for i in range(ra[0], ra[1]):
        c = chr(i)
        fonts._load_glyph(font, c, glyphs)
        g = glyphs[c]
        print(c, g['bitmap'].shape, g['offset'], g['advance'])

# Prepare
atlas = np.zeros((512, tex_width), 'uint8')
atlas += 100
coords = {}

# Collect all glyphs in the atlas
for i, c in enumerate(sorted(glyphs)):
    g = glyphs[c]
    # Put in 16x16 bitmap
    try:
        ox, oy = g['offset']
        h, w = g['bitmap'].shape
        oy = max(oy-10, 0)
        ox = max(ox-2, 0)
        bm = np.zeros((glyph_size, glyph_size), 'uint8')
        bm[oy:oy+h, ox:ox+w] = g['bitmap']
    except Exception:
        print(c, g['bitmap'].shape, g['offset'], g['advance'])
        raise
    # Get coordinates in atlas
    iy = i // glyphs_on_a_row
    ix = i - (iy * glyphs_on_a_row)
    y1, x1 = iy * glyph_size, ix * glyph_size
    y2, x2 = y1 + glyph_size, x1 + glyph_size
    # Put in
    atlas[y1:y2, x1:x2] = bm
    # Store texture coords
    xx1, xx2 = x1 / atlas.shape[1], x2 / atlas.shape[1]
    yy1, yy2 = y1 / atlas.shape[0], y2 / atlas.shape[0]
    #coords[c] = xx1, yy2, xx2, yy2, xx1, yy1, xx1, yy1, xx2, yy2, xx2, yy1
    coords[c] = xx1, yy1, xx2, yy1, xx1, yy2, xx1, yy2, xx2, yy1, xx2, yy2

# Write atlas to file
THISDIR = os.path.dirname(__file__)
imageio.imsave(os.path.join(THISDIR, 'glyphs.png'), atlas)
open(os.path.join(THISDIR, 'glyphs.blob'), 'wb').write(atlas.tostring())

# Store texture coords in a Python module
with open(os.path.join(THISDIR, '_coords.py'), 'wt') as f:
    f.write('# AUTOGENERATED, DO NOT EDIT\n')
    f.write('glyph_coords = {\n')
    for c in sorted(glyphs):
        f.write('    %r: %r,\n' % (c, coords[c]))
    f.write('    }\n')