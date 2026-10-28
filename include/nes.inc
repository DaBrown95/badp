PPUCTRL   = $2000
PPUMASK   = $2001
PPUSTATUS = $2002
OAMADDR   = $2003
PPUSCROLL = $2005
PPUADDR   = $2006
PPUDATA   = $2007
OAMDMA    = $4014
JOY1      = $4016

; Provisional mapper selection names, based on their producers and consumers.
; The secondary selection does not always map physical bank 1.
DefaultBankValue = $03C0
DefaultBankIndex = $03C1
SecondaryBankValue = $03C2
SecondaryBankIndex = $03C3
NmiSavedValue = $03C4
NmiSavedIndex = $03C5

; Provisional map-query and scroll workspace names, derived from the routines
; that use these addresses. Some fields also serve as intermediate scratch.
ScrollAxisOrder = $0398
MapTileXLow = $039A
MapTileXHigh = $039B
MapTileY = $039C
MapWidthTilesLow = $039E
MapWidthTilesHigh = $039F
ScrollStepPixels = $03E9
ScrollPendingFlags = $03EB
ScrollTargetXLow = $03EE
ScrollTargetXHigh = $03EF
ScrollTargetYLow = $03F0
ScrollTargetYHigh = $03F1
ScrollCurrentXLow = $03F3
ScrollCurrentXHigh = $03F4
ScrollCurrentYLow = $03F5
ScrollCurrentYHigh = $03F6
