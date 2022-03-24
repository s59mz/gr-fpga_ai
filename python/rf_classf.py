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

from ctypes import *
from typing import List
import cv2
import xir
import vart
import os
import math
import threading
import time
import sys


class rf_classf(gr.sync_block):
    """
     obtain dpu subgrah
    """
    def get_child_subgraph_dpu(self, graph: "Graph") -> List["Subgraph"]:
        assert graph is not None, "'graph' should not be None."
        root_subgraph = graph.get_root_subgraph()
        assert (
            root_subgraph is not None
        ), "Failed to get root subgraph of input Graph object."
        if root_subgraph.is_leaf:
            return []
        child_subgraphs = root_subgraph.toposort_child_subgraph()
        assert child_subgraphs is not None and len(child_subgraphs) > 0
        return [
            cs
            for cs in child_subgraphs
            if cs.has_attr("device") and cs.get_attr("device").upper() == "DPU"
        ]
	
    '''
    Calculate softmax
    data: data to be calculated
    size: data size
    return: softamx result
    '''
    def CPUCalcSoftmax(self, data, size, scale):
        sum = 0.0
        result = [0 for i in range(size)]
        for i in range(size):
            result[i] = math.exp(data[i] * scale)
            sum += result[i]
        for i in range(size):
            result[i] /= sum
        #print("Softmax = ", result)
        return result


    """
    docstring for block rf_classf
    """
    def __init__(self, model_filename):
        gr.sync_block.__init__(self,
            name="RF Classification",
            in_sig=[(np.complex64, 1024) ],
            out_sig=[np.short])

        g = xir.Graph.deserialize(model_filename)
        self.subgraphs = self.get_child_subgraph_dpu(g)
        assert len(self.subgraphs) == 1 # only one DPU kernel

        #self.runner = vart.Runner.create_runner(subgraphs[0], "run")

        self.mods = [
        'OOK',      '4ASK',      '8ASK',      'BPSK',   'QPSK',    '8PSK',
        '16PSK',    '32PSK',     '16APSK',    '32APSK', '64APSK',  '128APSK',
        '16QAM',    '32QAM',     '64QAM',     '128QAM', '256QAM',  
        'AM-DSB-WC', 'AM-DSB-SC', 'FM', 'GMSK','OQPSK']
        
    def start(self):
        print("START")
        self.runner = vart.Runner.create_runner(self.subgraphs[0], "run")

        """get tensor"""
        self.inputTensors = self.runner.get_input_tensors()
        outputTensors = self.runner.get_output_tensors()
        self.input_ndim = tuple(self.inputTensors[0].dims)
        self.pre_output_size = int(outputTensors[0].get_data_size() / self.input_ndim[0])
        self.output_ndim = tuple(outputTensors[0].dims)
        pre_output_size = int(outputTensors[0].get_data_size() / self.input_ndim[0])
        self.batchSize = self.inputTensors[0].dims[0]
        output_fixpos = outputTensors[0].get_attr("fix_point")
        self.output_scale = 1 / (2**output_fixpos)
        
        """prepare batch input/output """
        self.outputData = []
        self.inputData = []
        self.inputData = [np.empty(self.input_ndim, dtype=np.float32, order="C")]
        self.outputData = [np.empty(self.output_ndim, dtype=np.int8, order="C")]
        
        return True


    def stop(self):
        print("STOP")
        return True

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        
        runSize = len(in0)        

        """init input image to input buffer """
        for i in range(runSize):
            imageRun = self.inputData[0]
            for j in range(1024):
                imageRun[0, j, 0, 0] = in0[i][j].real 
                imageRun[0, j, 0, 1] = in0[i][j].imag 

            """run inference with batch on the FPGA DPU"""
            job_id = self.runner.execute_async(self.inputData, self.outputData)
            self.runner.wait(job_id)

            for j in range(len(self.outputData)):
                self.outputData[j] = self.outputData[j].reshape(1, self.pre_output_size)

            softmax = np.empty(self.pre_output_size)

            """softmax calculate with batch """
            softmax = self.CPUCalcSoftmax(self.outputData[0][0], self.pre_output_size, self.output_scale)
            modulation = np.argmax(softmax)
            modulation_name = self.mods[modulation]
            maxValue = np.amax(softmax)

            out[i] = np.short(modulation)
            print(f"Modulation = {modulation_name}\t Inx = {modulation}\t Prob: {maxValue:.2f}")
        
        return len(output_items[0])


