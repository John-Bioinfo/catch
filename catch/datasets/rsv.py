"""Dataset with 'Respiratory syncytial virus' sequences.

A dataset with 142 'Respiratory syncytial virus' genomes.

THIS PYTHON FILE WAS GENERATED BY A COMPUTER PROGRAM! DO NOT EDIT!
"""

import sys

from catch.datasets import GenomesDatasetSingleChrom

__author__ = 'Hayden Metsky <hayden@mit.edu>'


ds = GenomesDatasetSingleChrom(__name__, __file__, __spec__)
ds.add_fasta_path("data/rsv.fasta", relative=True)
sys.modules[__name__] = ds
