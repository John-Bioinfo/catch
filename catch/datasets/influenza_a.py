"""Dataset with 'Influenza A virus' sequences.

A dataset with 194737 'Influenza A virus' sequences. The virus is
segmented and has 8 segments. Based on their strain and/or isolate,
these sequences were able to be grouped into 63599 genomes. Many
genomes may have fewer than 8 segments.

THIS PYTHON FILE WAS GENERATED BY A COMPUTER PROGRAM! DO NOT EDIT!
"""

from os.path import dirname
from os.path import join
from os import listdir
import sys

from catch.datasets import GenomesDatasetMultiChrom

__author__ = 'Hayden Metsky <hayden@mit.edu>'

chrs = ["segment_" + seg for seg in ['1', '2', '3', '4', '5', '6', '7', '8']]

def seq_header_to_chr(header):
    import re
    c = re.compile(r'\[segment (1|2|3|4|5|6|7|8)\]')
    m = c.search(header)
    if not m:
        raise ValueError("Unknown segment in header %s" % header)
    seg = m.group(1)
    valid_segs = ['1', '2', '3', '4', '5', '6', '7', '8']
    if seg not in valid_segs:
        raise ValueError("Unknown segment %s" % seg)
    return "segment_" + seg

def seq_header_to_genome(header):
    import re
    c = re.compile(r'\[genome (.+)\]')
    m = c.search(header)
    return m.group(1)


ds = GenomesDatasetMultiChrom(__name__, __file__, __spec__,
                              chrs, seq_header_to_chr,
                              seq_header_to_genome=seq_header_to_genome)

for seg in ['1', '2', '3', '4', '5', '6', '7', '8']:
    ds.add_fasta_path("data/influenza_a_segment" + seg + ".fasta.gz",
        relative=True)

sys.modules[__name__] = ds
