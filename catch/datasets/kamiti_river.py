"""Dataset with 'Kamiti River virus' sequences.

A dataset with 1 'Kamiti River virus' genomes.

THIS PYTHON FILE WAS GENERATED BY A COMPUTER PROGRAM! DO NOT EDIT!
"""

import sys

from catch.datasets import GenomesDatasetSingleChrom

__author__ = 'Hayden Metsky <hayden@mit.edu>'


ds = GenomesDatasetSingleChrom(__name__, __file__, __spec__)
ds.add_fasta_path("data/kamiti_river.fasta", relative=True)
sys.modules[__name__] = ds
