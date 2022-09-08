'''
==========================================================================
PatternVerifier.py
==========================================================================
RTL implemetation for PRBS verifier.
- In IDLE mode, do nothing. Switch to LOCK mode if s.en is high.
- In LOCK mode, the PRBS verifier tries to lock to the PRBS sequence.
- In ERROR_COUNT mode, the PRBS verifier compares the input against the
expected result. If a mismatch is encountered, switch back to LOCK or
IDLE mode based on s.en.

Author : Yanghui Ou
  Date : Aug 24, 2022
'''

from pymtl3 import *
from pymtl3.stdlib.basic_rtl import Reg

from ..lfsr import LfsrGeneric

#-------------------------------------------------------------------------
# PatternVerifier
#-------------------------------------------------------------------------
# TODO: seed is not necessary! remove it!

class PatternVerifier( Component ):
  def construct( s, nbits, lfsr_bitmap, lock_cycles=31 ):

    # Local parameters

    s.DataT       = mk_bits( nbits )
    s.MatchCountT = mk_bits( clog2(lock_cycles+1) )
    s.lock_cycles = lock_cycles

    s.STATE_IDLE        = b2(0)
    s.STATE_LOCK        = b2(1)
    s.STATE_ERROR_COUNT = b2(2)

    # Interface

    s.seed = InPort( s.DataT )
    s.in_  = InPort( s.DataT )

    s.en          = InPort ()
    s.locked      = OutPort()
    s.error_count = OutPort(32) #TODO: paramatrize this?

    # Registers and wires

    s.state_r       = Wire(2)
    s.match_count_r = Wire( s.MatchCountT )
    # s.first_r       = Wire( s.DataT )

    s.state_next          = Wire(2)
    s.match_count_reached = Wire()
    s.matched             = Wire()

    # Component

    s.in_r = Reg( s.DataT ) # buffer input for better timing
    s.lfsr = LfsrGeneric( nbits, lfsr_bitmap )

    # Connections and assignments

    s.in_r.in_            //= s.in_
    # s.lfsr.in_            //= lambda: s.lfsr.out if ( s.state_r != s.STATE_IDLE ) & s.matched else s.seed
    s.matched             //= lambda: s.in_r.out == s.lfsr.out
    s.match_count_reached //= lambda: s.match_count_r == s.lock_cycles

    # Logic

    @update_ff
    def up_state_transition():
      if s.reset:
        s.state_r  <<= s.STATE_IDLE
      else:
        s.state_r <<= s.state_next

    @update
    def up_state_next():
      s.state_next @= s.STATE_IDLE
      if s.state_r == s.STATE_IDLE:
          s.state_next @= s.STATE_LOCK if s.en else s.STATE_IDLE

      elif s.state_r == s.STATE_LOCK:
        s.state_next @= s.STATE_ERROR_COUNT if s.match_count_reached else s.STATE_LOCK

      elif s.state_r == s.STATE_ERROR_COUNT:
        s.state_next @= s.STATE_ERROR_COUNT if s.matched else \
                        s.STATE_LOCK        if s.en else \
                        s.STATE_IDLE

    # Handle the special case
    # @update_ff
    # def up_fisrt_r():
    #   if s.match_count_r == 0:
    #     s.first_r <<= s.lfsr.out
    #   else:
    #     s.first_r <<= s.first_r

    @update
    def up_lfsr_in():
      s.lfsr.in_ @= s.in_r.out
      # if s.state_r == s.STATE_LOCK:
      #   if s.matched:
      #     s.lfsr.in_ @= s.lfsr.out
      #   elif ( s.match_count_r == 1 ) & ( s.in_r.out == s.first_r ):
      #     s.lfsr.in_ @= s.first_r
      if s.state_r == s.STATE_ERROR_COUNT:
        s.lfsr.in_ @= s.lfsr.out

    @update_ff
    def up_locked():
      if s.reset:
        s.locked <<= 0
      else:
        s.locked <<= ( s.state_r == s.STATE_LOCK ) & ( s.state_next == s.STATE_ERROR_COUNT ) | \
                     ( s.state_r == s.STATE_ERROR_COUNT ) & ( s.state_next == s.STATE_ERROR_COUNT )

    @update_ff
    def up_match_count_r():
      if s.reset:
        s.match_count_r <<= 0
      elif s.state_r == s.STATE_LOCK:
        if s.matched:
          s.match_count_r <<= s.match_count_r + 1 if ~s.match_count_reached else 0
        # elif ( s.match_count_r == 1 ) & ( s.in_r.out == s.first_r ):
        #   s.match_count_r << s.match_count_r
        else:
          s.match_count_r <<= 0
      else:
        s.match_count_r <<= 0

    @update_ff
    def up_error_count():
      if s.reset:
        s.error_count <<= 0
      elif s.state_r == s.STATE_ERROR_COUNT:
        s.error_count <<= s.error_count if s.in_r.out == s.lfsr.out else s.error_count + 1
      else:
        s.error_count <<= s.error_count

  def line_trace( s ):
    state = 'I' if s.state_r == s.STATE_IDLE else \
            'L' if s.state_r == s.STATE_LOCK else \
            'E' if s.state_r == s.STATE_ERROR_COUNT else \
            '?'
    return f'{s.in_}({state}[{s.match_count_r}]{s.in_r.out}={s.lfsr.out})'

