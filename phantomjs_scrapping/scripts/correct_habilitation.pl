#!/usr/bin.perl

$habilitations = shift;
$dossiers  = shift;

open(FH, "$habilitations");
open(FD, "$dossiers");

foreach $uneligne (<FD>) {
  @unelignecsv = split(/;/, $uneligne);
  if (@unelignecsv[0] != $lastone) {
    foreach (@memeid) {
      @d = split(/;/);
      if ($d[2] =~ s/(\d{2})\/(\d{2})\/(\d{4}) .*/$3-$2-$1/) {
        $demandes{$d[0]} = $d[2];
      }
      if ($d[1] =~ /Demande Habilitation/i) {
        last;
      }
    }
    @memeid = ();
  }
  $lastone = $unelignecsv[0];
  $memeid[$#memeid + 1] = join(';', @unelignecsv);
}
foreach (@memeid) {
  @d = split(/;/);
  if ($d[2] =~ s/(\d{2})\/(\d{2})\/(\d{4}) .*/$3-$2-$1/) {
    $demandes{$d[0]} = $d[2];
  }
  if ($d[1] =~ /Demande Habilitation/i) {
    last;
  }
}
close FD;

foreach (<FH>) {
  chomp;
  @h = split(/;/);
  if ($h[12] =~ s/^(\d{2})\/(\d{2})\/(\d{4}).*/$3-$2-$1/ && !$h[11]) {
    $h[11] = $h[12];
    $h[12] = '';
  }
  if (!$h[11]) {
    $h[11] = $demandes{$h[1]};
  }
  print join(';', @h)."\n";
}
close FH;
