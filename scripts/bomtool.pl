#!/usr/bin/perl
use warnings;
use strict;

use feature 'say';
use feature 'signatures';

use open qw( :std :encoding(UTF-8) );

use Cwd qw( abs_path );
use File::Basename;
use Getopt::Long qw( :config no_ignore_case bundling );
use Math::Trig;
use Text::CSV qw( csv );

# Command line parameters
my $kicad_bom_filename;
my $kicad_pos_filename;
my $jlc_bom_filename;
my $jlc_cpl_filename;

# Look for adjustment data next to this script by default
my $adjustment_data_filename = dirname(__FILE__) . "/jlc_adjust.pl";

# At time of writing (2026 Feb) JLCPCB doesn't handle UTF-8
# input correctly. GBK is required for non-ASCII characters
# (eg. mu or omega).
my $output_encoding = "GBK";

# Option parsing
my %options = (
    'kicad-bom=s' => \$kicad_bom_filename,
    'kicad-pos=s' => \$kicad_pos_filename,
    'output-jlc-bom=s' => \$jlc_bom_filename,
    'output-jlc-cpl=s' => \$jlc_cpl_filename,
    'adjustment-data' => \$adjustment_data_filename,
    'output-encoding=s' => \$output_encoding,
);

GetOptions %options;

# Validate required options are present
for my $opt (keys %options) {
    my $ref = $options{$opt};
    if (!defined $$ref) {
        $opt =~ s/=.*//;
        say STDERR "missing required option: $opt";
        exit 1;
    }
}

# Mapping from part fields to BOM CSV fields
my %bom_csv_fields = (
    Ref       => "Reference",
    Comment   => "Value",
    Footprint => "Footprint",
    LCSC      => "LCSC#",
    Qty       => "QUANTITY",
    DNP       => "DNP",
);

# Adjustment match fields to part field mapping
my @match_fields = (
    ("MatchRef",        "Ref"),
    ("MatchComment",    "Comment"),
    ("MatchFootprint",  "Footprint"),
    ("MatchLCSC",       "LCSC"),
);

# Check if an adjustment pattern matches a part
sub match_adjustment ($adj, $part) {
    my $match = 0;
    for my ($mf, $f) (@match_fields) {
        if (exists $adj->{$mf}) {
            if ($part->{$f} =~ /^$adj->{$mf}$/) {
                $match = 1;
            } else {
                return 0;
            }
        }
    }

    return $match;
}

# Load adjustment data
my @adjustments = do (abs_path($adjustment_data_filename));

# Part list indexed by reference designators
my %parts;

# Read in BOM and position files
my $bom = csv (in => $kicad_bom_filename, headers => "auto");
my $pos = csv (in => $kicad_pos_filename, headers => "auto");

# Extract data from BOM
for my $row (@$bom) {
    my $refdes = $row->{$bom_csv_fields{Ref}};
    my $dnp = $row->{${bom_csv_fields{DNP}}} ? 1 : 0;
    my $footprint = $row->{${bom_csv_fields{Footprint}}};

    if ($row->{$bom_csv_fields{Qty}} > 1) {
        print "BOM entry for $refdes is not a single component\n";
        exit 1;
    }

    # Remove library prefix from footprint string because
    # the position file doesn't include it.
    $footprint =~ s/.*://;

    # Create part entry
    $parts{$refdes} = {
        Ref       => $refdes,
        Comment   => $row->{${bom_csv_fields{Comment}}},
        Footprint => $footprint,
        DNP       => $dnp,
        LCSC      => $row->{${bom_csv_fields{LCSC}}},
        Ignored   => 0,
        PosX      => "",
        PosY      => "",
        Rot       => "",
        Side      => "",
        OffX      => 0,
        OffY      => 0,
    };
}

# Extract data from position file
for my $row (@$pos) {
    my $refdes = $row->{Ref};
    my $footprint = $row->{Package};

    # Create entry for parts that don't exist in BOM
    if (!exists $parts{$refdes}) {
        $parts{$refdes} = {
            Ref       => $refdes,
            Comment   => "",
            Footprint => $footprint,
            DNP       => 0,
            LCSC      => "",
            Ignored   => 0,
        };
    }

    my $part = $parts{$refdes};

    $part->{PosX} = $row->{PosX} + 0;
    $part->{PosY} = $row->{PosY} + 0;
    $part->{Rot}  = $row->{Rot} + 0;
    $part->{Side} = $row->{Side};

    # OffX/OffY are offsets applied to the part in its local
    # coordinate system before any rotations.
    $part->{OffX} = 0;
    $part->{OffY} = 0;
}

# Split reference designator into string and numeric parts
sub split_refdes ($str) {
    return ($1, $2) if $str =~ /^(\D+)(\d*)$/;
    return ($str, 0);
}

# Sort by reference designators
sub by_refdes {
    my ($ar, $an) = split_refdes $a->{Ref};
    my ($br, $bn) = split_refdes $b->{Ref};

    my $res = $ar cmp $br;
    if ($res == 0) {
        $res = $an <=> $bn
    }

    return $res;
}

# Create list of parts sorted by reference designator.
my @sorted_parts = sort by_refdes (values %parts);

# Apply adjustments
for my $part (@sorted_parts) {
    for my $adj (@adjustments) {
        if (match_adjustment ($adj, $part)) {
            if (exists $adj->{Warning}) {
                say STDERR "WARNING: $part->{Ref}: $adj->{Warning}";
            }

            $part->{Rot} += $adj->{Rot}             if exists $adj->{Rot};
            $part->{LCSC} = $adj->{LCSC}            if exists $adj->{LCSC};
            $part->{Comment} = $adj->{Comment}      if exists $adj->{Comment};
            $part->{Footprint} = $adj->{Footprint}  if exists $adj->{Footprint};
            $part->{OffX} += $adj->{OffX}           if exists $adj->{OffX};
            $part->{OffY} += $adj->{OffY}           if exists $adj->{OffY};
            $part->{Ignored} += $adj->{Ignored}     if exists $adj->{Ignored};
        }
    }

    # Fix bottom side rotations; this must be done after adjustments
    # to ensure part rotation is adjusted consistently when the same
    # part occurs on both sides of the board.
    if ($part->{Side} eq "bottom") {
        $part->{Rot} = 180 - $part->{Rot};
    }

    # Put negative rotations into the positive range
    while ($part->{Rot} < 0) {
        $part->{Rot} += 360
    }

    # Put all rotations into the range -180,180
    while ($part->{Rot} >= 180) {
        $part->{Rot} -= 360
    }

    # Apply offsets after fixing rotation
    my $rot = deg2rad($part->{Rot});
    $part->{PosX} += cos($rot) * $part->{OffX} + sin($rot) * $part->{OffY};
    $part->{PosY} += sin($rot) * $part->{OffX} + cos($rot) * $part->{OffY};
}

# Create BOM and CPL files for JLC
my @jlc_bom = (["Designator", "Comment", "Footprint", "JLCPCB Part #"]);
my @jlc_cpl = (["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]);

for my $part (@sorted_parts) {
    if ($part->{Ignored}) {
        next;
    }

    if ($part->{LCSC} eq "") {
        say STDERR "WARNING: $part->{Ref}: missing LCSC part number";
    }

    if ($part->{PosX} eq "" || $part->{PosY} eq "" ||
        $part->{Side} eq "" || $part->{Rot} eq "") {
        say STDERR "WARNING: $part->{Ref}: missing position data";
    }

    push @jlc_bom, [
        $part->{Ref},
        $part->{Comment},
        $part->{Footprint},
        $part->{LCSC},
    ];

    push @jlc_cpl, [
        $part->{Ref},
        $part->{PosX},
        $part->{PosY},
        $part->{Side},
        $part->{Rot},
    ];
}

# Write out the CSV files
csv (in => \@jlc_bom, out => $jlc_bom_filename, encoding => $output_encoding);
csv (in => \@jlc_cpl, out => $jlc_cpl_filename, encoding => $output_encoding);
