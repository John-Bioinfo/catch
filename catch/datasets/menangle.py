"""Dataset with 'Menangle rubulavirus' sequences.

A dataset with 1 'Menangle rubulavirus' genomes.

THIS PYTHON FILE WAS GENERATED BY A COMPUTER PROGRAM! DO NOT EDIT!
"""

import sys

from catch.datasets import GenomesDatasetSingleChrom

__author__ = 'Hayden Metsky <hayden@mit.edu>'


ds = GenomesDatasetSingleChrom(__name__, __file__, __spec__)
ds.add_fasta_path("data/menangle.fasta", relative=True)
sys.modules[__name__] = ds
