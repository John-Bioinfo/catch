"""Provides analysis of a probe set for targeted genomes.
"""

import logging

from hybseldesign import probe
from hybseldesign.utils import interval
from hybseldesign.utils import pretty_print

__author__ = 'Hayden Metsky <hayden@mit.edu>'

logger = logging.getLogger(__name__)


class Analyzer:
    """Methods for testing quality control of a probe set.
    """

    def __init__(self,
                 probes,
                 target_genomes,
                 mismatches=0,
                 lcf_thres=100,
                 kmer_size=10,
                 num_kmers_per_probe=20):
        """
        Args:
            probes: collection of instances of probe.Probe that form a
                complete probe set
            target_genomes: list [g_1, g_2, g_m] of m groupings of genomes,
                where each g_i is a list of genome.Genomes belonging to
                group i. For example, a group may be a species and each g_i
                would be a list of the target genomes of species i.
            mismatches/lcf_thres: consider a probe to hybridize to a sequence
                if a stretch of 'lcf_thres' or more bp aligns with
                'mismatches' or fewer mismatched bp; used to compute whether
                a probe "covers" a portion of a sequence
            kmer_size/num_kmers_per_probe: parameters to use when determining
                what parts of a sequence each probe "covers"; used in calls
                to probe.construct_kmer_probe_map and
                probe.find_probe_covers_in_sequence
        """
        self.probes = probes
        self.target_genomes = target_genomes
        self.cover_range_fn = \
            probe.probe_covers_sequence_by_longest_common_substring(
                mismatches, lcf_thres)
        self.kmer_size = kmer_size
        self.num_kmers_per_probe = num_kmers_per_probe

    def _iter_target_genomes(self, rc_too=False):
        """Yield target genomes across groupings to iterate over.

        Args:
            rc_too: when True, also yields False and True for each
                target genome

        Yields:
            i, j, gnm [, rc]
                - i is the index of a target genome grouping
                - j is the index of a genome in grouping i
                - gnm is an instance of genome.Genome corresponding to
                  to genome j in grouping i
                - if rc_too is True, rc cycles through False and True
                  so that an iterator can take the reverse complement
                  of gnm's sequences
        """
        for i, genomes_from_group in enumerate(self.target_genomes):
            for j, gnm in enumerate(genomes_from_group):
                if rc_too:
                    yield i, j, gnm, False
                    yield i, j, gnm, True
                else:
                    yield i, j, gnm

    def _find_covers_in_target_genomes(self):
        """Find intervals across the target genomes covered by the probe set.

        This considers the given probe set (self.probes) and determines the
        intervals, in each genome of the target genomes (as well as their
        reverse complements), that are covered by the probes. This saves a
        dict, self.target_covers, as follows: self.target_covers[i][j][b]
        is a list of all the intervals covered by the probes in the target
        genome j of grouping i (in the reverse complement of the genome if
        b is True, and provided sequence if b is False).

        The endpoints of the intervals are offset so as to give unique integer
        positions in the genome (e.g., endpoints in the second chromosome
        are offset based on the length of the first chromosome). There may
        be duplicate intervals if two probes cover the same region of a
        sequence.
        """
        logger.info("Building map from k-mers to probes")
        kmer_probe_map = probe.construct_kmer_probe_map(
            self.probes,
            k=self.kmer_size,
            num_kmers_per_probe=self.num_kmers_per_probe,
            include_positions=True)

        self.target_covers = {}
        for i, j, gnm, rc in self._iter_target_genomes(True):
            if not rc:
                logger.info(("Computing coverage in grouping %d (of %d), "
                             "with target genome %d (of %d)"), i,
                            len(self.target_genomes), j,
                            len(self.target_genomes[i]))
            if i not in self.target_covers:
                self.target_covers[i] = {}
            if j not in self.target_covers[i]:
                self.target_covers[i][j] = {False: None, True: None}

            gnm_covers = []
            length_so_far = 0
            for sequence in gnm.seqs:
                if rc:
                    # Take the reverse complement of sequence
                    rc_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
                    sequence = ''.join([rc_map.get(b, b)
                                       for b in sequence[::-1]])

                # Find cover ranges of the probes, while allowing the ranges
                # to overlap (e.g., if one probe covers two regions that
                # overlap)
                probe_cover_ranges = probe.find_probe_covers_in_sequence(
                    sequence, kmer_probe_map,
                    k=self.kmer_size,
                    cover_range_for_probe_in_subsequence_fn=self.cover_range_fn,
                    merge_overlapping=False)
                for p, cover_ranges in probe_cover_ranges.iteritems():
                    for cover_range in cover_ranges:
                        # The endpoints of cover_range give positions in just
                        # this sequence (chromosome), so adjust them (according
                        # to length_so_far) to give a unique integer position
                        # in the genome gnm
                        adjusted_cover = (cover_range[0] + length_so_far,
                                          cover_range[1] + length_so_far)
                        gnm_covers += [adjusted_cover]
                length_so_far += len(sequence)
            self.target_covers[i][j][rc] = gnm_covers

    def _compute_bp_covered_in_target_genomes(self):
        """Count number of bp covered by probes in each target genome.

        self._find_covers_in_target_genomes() must be called prior to this,
        so that self.target_covers can be accessed.

        This saves a dict, self.bp_covered, as follows:
        self.bp_covered[i][j][b] gives the number of bp covered by the
        probes in genome j of target genome grouping i (in the reverse
        complement of j if b is True, and in the provided sequence if b
        if False).
        """
        self.bp_covered = {}
        for i, j, gnm, rc in self._iter_target_genomes(True):
            if i not in self.bp_covered:
                self.bp_covered[i] = {}
            if j not in self.bp_covered[i]:
                self.bp_covered[i][j] = {False: None, True: None}
            covers = self.target_covers[i][j][rc]

            # Make an IntervalSet out of all covers to merge overlapping
            # ones and make it easy to count the number of bp covered
            covers_set = interval.IntervalSet(covers)
            self.bp_covered[i][j][rc] = len(covers_set)

    def _compute_average_coverage_in_target_genomes(self):
        """Calculate the average coverage/depth in each target genome.

        self._find_covers_in_target_genomes() must be called prior to this,
        so that self.target_covers can be accessed.

        This saves a dict, self.average_coverage, as follows:
        self.average_coverage[i][j][b] gives the average coverage/depth
        provided by the probes in genome j of target genome grouping i
        (in the reverse complement of j if b is True, and in the provided
        sequence if b is False).

        Specifically, the value is the average, taken across all bases,
        of the number of probes that hybridize to a region that includes
        a given base.
        """
        self.average_coverage = {}
        for i, j, gnm, rc in self._iter_target_genomes(True):
            if i not in self.average_coverage:
                self.average_coverage[i] = {}
            if j not in self.average_coverage[i]:
                self.average_coverage[i][j] = {False: None, True: None}
            covers = self.target_covers[i][j][rc]

            # Count the total number of bases covered by all the probe
            # hybridizations
            # (covers may include duplicates if two probes hybridize to
            # the same region, so it is important not to convert probes
            # to an IntervalSet or merge its intervals)
            total_covered = sum(c[1] - c[0] for c in covers)

            # Divide by the genome length to average across bases
            self.average_coverage[i][j][rc] = float(total_covered) / gnm.size()

    def run(self):
        """Run all analysis methods.

        The methods called save their output to self.
        """
        self._find_covers_in_target_genomes()
        self._compute_bp_covered_in_target_genomes()
        self._compute_average_coverage_in_target_genomes()

    def _make_data_matrix(self):
        """Return 2D array representing results (as strings) to output.

        Returns:
            2D array, with row and column headers, containing data to
            output as a table
        """
        # Make row headers
        data = [["Genome",
                 "Num bases covered",
                 "Average coverage/depth"]]

        # Create a row for every genome, including reverse complements
        for i, j, gnm, rc in self._iter_target_genomes(True):
            col_header = "Grouping %d, genome %d" % (i, j)
            if rc:
                col_header += " (rc)"

            # Format bp covered
            bp_covered = self.bp_covered[i][j][rc]
            frac_covered = float(bp_covered) / gnm.size()
            if frac_covered < 0.0001:
                prct_covered_str = "<0.01%"
            else:
                prct_covered_str = "{0:.2%}".format(frac_covered)
            bp_covered_str = "%d (%s)" % (bp_covered, prct_covered_str)

            # Format average covered
            average_coverage = self.average_coverage[i][j][rc]
            if average_coverage < 0.01:
                average_coverage_str = "<0.01"
            else:
                average_coverage_str = "{0:.2f}".format(average_coverage)

            row = [col_header, bp_covered_str, average_coverage_str]
            data += [row]

        return data

    def print_analysis(self):
        """Print a table of results of the analysis.
        """
        print pretty_print.table(self._make_data_matrix(),
                                 ["left", "right", "right"],
                                 header_underline=True)