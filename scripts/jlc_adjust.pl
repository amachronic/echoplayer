(
 ## Ignored parts

 {
     MatchFootprint => "NetTie_0.15mm_SMD",
     Ignored        => 1,
 },
 {
     MatchFootprint => "Switch_ContactPad_10x3mm_Cross",
     Ignored        => 1,
 },

 ## Fix comments on buttons which cause warnings in the JLCPCB BOM tool

 {
     MatchFootprint => "Switch_XKB_TS-1010-C-A",
     Comment        => "XKB_TS-1010-C-A",
 },
 {
     MatchFootprint => "Switch_XUNPU_TS-1088-AR",
     Comment        => "XUNPU_TS-1088-AR",
 },
 {
     MatchFootprint => "Jack_3.5mm_HCTL_HC-PJ-320A-4P-D",
     Comment        => "HCTL-PJ-320A-4P-D",
 },

 ## Hacks

 {
     # Note the replacement's characteristics apparently aren't
     # as good and it costs the same as the the -ES version.
     Warning        => "replacing CESD3V3AP-ES (LCSC# C5199223) with more available part",
     MatchLCSC      => "C5199223",
     Comment        => "CESD3V3AP",
     LCSC           => "C70435",
 },
 {
     # This is to suppress a warning from JLCPCB's BOM tool
     # TODO: fix this on the KiCAD side, the footprints are identical
     MatchLCSC      => "C725791",
     MatchFootprint => "TSOT-23-6",
     Footprint      => "SOT-23-6",
 },

 ## Part orientation and offset adjustments, should be matched
 ## by LCSC part number only.

 # 4 digits
 {
     MatchLCSC => "C5446",
     Rot       => 180,
 },
 # 5 digits
 {
     MatchLCSC => "C62246",
     Rot       => 90,
 },
 {
     MatchLCSC => "C70435",
     Rot       => 180,
 },
 {
     MatchLCSC => "C89597",
     Rot       => 90,
 },
 # 6 digits
 {
     MatchLCSC => "C107309",
     Rot       => 180,
 },
 {
     MatchLCSC => "C132156",
     Rot       => 90,
 },
 {
     MatchLCSC => "C165948",
     OffY      => -1.2,
 },
 {
     MatchLCSC => "C318941",
     OffY      => -0.3,
 },
 {
     MatchLCSC => "C347476",
     Rot       => 180,
 },
 {
     MatchLCSC => "C431541",
     Rot       => 180,
     OffY      => 0.55,
 },
 {
     MatchLCSC => "C460349",
     Rot       => 180,
 },
 {
     MatchLCSC => "C720505",
     OffY      => 1.6,
 },
 {
     MatchLCSC => "C725791",
     Rot       => 180,
 },
 # 7 digits
 {
     MatchLCSC => "C2869734",
     Rot       => -90,
 },
 {
     MatchLCSC => "C2897388",
     Rot       => -90,
     OffX      => 6.35,
 },
 {
     MatchLCSC => "C2923380",
     Rot       => 180,
 },
 # 8 digits
 {
     MatchLCSC => "C18198555",
     OffY      => 1.4,
 },
 {
     MatchLCSC => "C41378737",
     OffY      => -0.3,
 },
)
