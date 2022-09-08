'''
==========================================================================
utils.py
==========================================================================
Utility functions for PRBS. PRBS output is represented using a bitmap,
where each output bit is represented using a bitstream. For example,
0b0101 represents x[2] ^ x[3].

Author : Yanghui Ou
  Date : Sep 1, 2022
'''
import re

from pymtl3 import *

#-------------------------------------------------------------------------
# Local parameters
#-------------------------------------------------------------------------

re_poly = re.compile( r'^\s*[x\^\d*\s*\+\s*]+\s*\+\s*1' )

#-------------------------------------------------------------------------
# _poly_to_bits
#-------------------------------------------------------------------------
# Convert polynomial to Bits representation

def _poly_to_bits( poly_str ):
  assert re_poly.match( poly_str ), f'{poly_str} is not a valid polynomial for LFSR!'
  terms = poly_str.split( '+' )[:-1]
  orders = [ 1 if t.strip()=='x' else int(t.split('^')[-1]) for t in terms]
  T = mk_bits( max(orders) )
  ret = T()
  for n in orders:
    ret[n-1] = b1(1)
  return ret

#-------------------------------------------------------------------------
# gen_bitmap_std
#-------------------------------------------------------------------------
# Generate bitmap for LFSR using standard implementation.

def gen_bitmap_std( nbits, poly_str ):
  bitstream = _poly_to_bits( poly_str )
  assert nbits >= bitstream.nbits, f'{nbits}-bit is too short for {poly_str}!'
  T = mk_bits( nbits )

  # x[0] <= input expression
  bitmap = [ bitstream ]

  # x[i] <= x[i-1]
  for i in range( 1, nbits ):
    bitmap.append( T(1) << (i-1) )

  return bitmap

#-------------------------------------------------------------------------
# gen_bitmap_ahd
#-------------------------------------------------------------------------
# Generate bitmap for LFSR using standard implementation.

def gen_bitmap_ahd( nbits, poly_str ):
  bitstream = _poly_to_bits( poly_str )
  assert nbits >= bitstream.nbits, f'{nbits}-bit is too short for {poly_str}!'
  T = mk_bits( nbits )

  # Initialize output to be x[i] <= x[i]
  bitmap = [ T(1) << i for i in range(nbits) ]
  poly   = zext( bitstream, nbits )

  # Apply the polynomial n-times
  for _ in range( nbits ):
    tmp = list( bitmap )

    # Apply polynomial
    tmp[0] = T()
    for i, term in enumerate( bitstream ):
      if bitstream[i]:
        tmp[0] ^= bitmap[i]

    # Shift
    for i in range( 1, nbits ):
      tmp[i] = bitmap[i-1]

    bitmap = list( tmp )

  return bitmap

#-------------------------------------------------------------------------
# print_equation
#-------------------------------------------------------------------------

def print_equation( bitmap ):
  for i, expr in enumerate( bitmap ):
    lst = []
    for j in range( expr.nbits ):
      if expr[j]:
        lst.append( f'x[{j}]' )
    equation = ' ^ '.join( lst )
    print( f'x[{i}] <= {equation}' )

