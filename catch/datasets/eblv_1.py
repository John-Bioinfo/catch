"""Dataset with 'European bat 1 lyssavirus' sequences.

A dataset with 12 'European bat 1 lyssavirus' genomes.

THIS PYTHON FILE WAS GENERATED BY A COMPUTER PROGRAM! DO NOT EDIT!
"""

import sys

from catch.datasets import GenomesDatasetSingleChrom

__author__ = 'Hayden Metsky <hayden@mit.edu>'


ds = GenomesDatasetSingleChrom(__name__, __file__, __spec__)
ds.add_fasta_path("data/eblv_1.fasta", relative=True)
sys.modules[__name__] = ds