#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 S59MZ.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#


import numpy as np
from gnuradio import gr

class sample_mod_src(gr.sync_block):
    """
    docstring for block sample_mod_src
    """
    mods = [
    'OOK',      '4ASK',      '8ASK',      'BPSK',   'QPSK',    '8PSK',
    '16PSK',    '32PSK',     '16APSK',    '32APSK', '64APSK',  '128APSK',
    '16QAM',    '32QAM',     '64QAM',     '128QAM', '256QAM',
    'AM-DSB-WC', 'AM-DSB-SC', 'FM', 'GMSK','OQPSK']

    def __init__(self, samples_file, classes_file, index):
        gr.sync_block.__init__(self,
            name="sample_mod_src",
            in_sig=None,
            out_sig=[(np.complex64, 1024)])
        self.samples = np.load(samples_file)
        self.index = index
        self.index_ = -1

        self.mods = [
        'OOK',      '4ASK',      '8ASK',      'BPSK',   'QPSK',    '8PSK',
        '16PSK',    '32PSK',     '16APSK',    '32APSK', '64APSK',  '128APSK',
        '16QAM',    '32QAM',     '64QAM',     '128QAM', '256QAM',
        'AM-DSB-WC', 'AM-DSB-SC', 'FM', 'GMSK','OQPSK']

        self.modulations = np.load(classes_file)


    def work(self, input_items, output_items):
        if self.index != self.index_:
            self.sample = self.samples[self.index]
            modulation = self.mods[np.argmax(self.modulations[self.index])]
            self.index_ = self.index
            print(modulation)

        out = output_items[0]
        numOf = len(out)
        # <+signal processing here+>
        for vec in range(numOf):
            for s in range(1024):
                out[vec][s] = self.sample[s][0][0] + 1j* self.sample[s][0][1]
        return len(output_items[0])

