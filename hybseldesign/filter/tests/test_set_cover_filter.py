"""Tests for set_cover_filter module.
"""

__author__ = 'Hayden Metsky <hayden@mit.edu>'

import unittest
import logging

from hybseldesign import probe
from hybseldesign.filter import set_cover_filter as scf
from hybseldesign.utils import interval


"""Tests the set cover filter output on contrived input.
"""
class TestSetCoverFilter(unittest.TestCase):

  def setUp(self):
    # Disable logging
    logging.disable(logging.INFO)

  def get_filter_and_output(self, lcf_thres, mismatches,
      target_genomes, input, coverage_frac, k,
      num_kmers_per_probe):
    input_probes = [probe.Probe.from_str(s) for s in input]
    f = scf.SetCoverFilter(mismatches=mismatches, lcf_thres=lcf_thres,
          coverage_frac=coverage_frac, kmer_size=k,
          num_kmers_per_probe=num_kmers_per_probe)
    f.target_genomes = target_genomes
    f.filter(input_probes)
    return (f, f.output_probes)

  def verify_target_genome_full_coverage(self, selected_probes,
      target_genomes, k, num_kmers_per_probe, filter):
    kmer_probe_map = probe.construct_kmer_probe_map(
                      selected_probes, k=k,
                      num_kmers_per_probe=10,
                      include_positions=True)
    for tg in target_genomes:
      probe_cover_ranges = probe.find_probe_covers_in_sequence(
          tg, kmer_probe_map, k=k,
          cover_range_for_probe_in_subsequence_fn=filter.cover_range_fn)
      all_cover_ranges = []
      for cover_ranges in probe_cover_ranges.values():
        for cv in cover_ranges:
          all_cover_ranges += [cv]
      all_cover_ranges = interval.merge_overlapping(all_cover_ranges)
      self.assertEquals(len(all_cover_ranges), 1)
      start, end = all_cover_ranges[0][0], all_cover_ranges[0][1]
      self.assertEquals(start, 0)
      self.assertEquals(end, len(tg))

  def test_full_coverage(self):
    target_genomes = [ 'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEF',
                       'ZYXWVFGHIJWUTSOPQRSTFEDCBAZYXWVF' ]
    input = []
    for tg in target_genomes:
      input += [ tg[i:(i+6)] for i in xrange(len(tg)-6+1) ]
    must_have_output = [ 'OPQRST',
                         'UVWXYZ',
                         'FEDCBA',
                         'ABCDEF',
                         'ZYXWVF' ]
    f, output = self.get_filter_and_output(6, 0, target_genomes,
        input, 1.0, 3, 10)
    # output must have probes in must_have_output
    for o in must_have_output:
      self.assertTrue(probe.Probe.from_str(o) in output)
    # verify that each of the target genomes is fully covered
    self.verify_target_genome_full_coverage(output,
      target_genomes, 3, 10, f)

  def tearDown(self):
    # Re-enable logging
    logging.disable(logging.NOTSET)
