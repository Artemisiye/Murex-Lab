


# Procedural Levers

## A - Artidity
1) A1 - Hyper-dry
2) A2 - Arid
3) A3 - Semi-arid
4) A4 - Sub-humid
5) A5 - Humid

## E - Elevation
1) E1 - Lowland
2) E2 - Colline
3) E3 - Highland
4) E4 - Montane
5) E5 - Alpine

## T - Temperature
0) T0 - Frozen
1) T1 - Cold
2) T2 - Cool
3) T3 - Temperate
4) T4 - Warm
5) T5 - Hot

## Effective Temperature
T_eff = Clamp(T - E + 1, 0, 5)


# Biome Matrix

## Matrix

| A/T         | 0 Frozen | 1 Cold     | 2 Cool    | 3 Temperate | 4 Warm    | 5 Hot     |
| ----------- | -------- | ---------- | --------- | ----------- | --------- | --------  |
| 1 Dry       | Tundra   | Tundra     | Desert    | Hammada     | Erg       | Erg       |
| 2 Arid      | Tundra   | Steppe     | Steppe    | Shrubland   | Hammada   | Hammada   |
| 3 Semi-Arid | Tundra   | Steppe     | Grassland | Maquis      | Shrubland | Shrubland |
| 4 Sub-Humid | Tundra   | Forest     | Woodland  | Woodland    | Maquis    | Woodland  |
| 5 Humid     | Tundra   | Forest     | Forest    | Forest      | Forest    | Forest    |


## Biome + Tile List
- Tundra - Cold and barren landscape, potentially covered in snow and ice #9ab4bcff
- Desert - Dry, cool and barren landscape. #faf7d1ff
- Hammada - Dry, hot and stone landscape. Mineral-rich. #f0e171
- Erg - Dry, hot and sandy landscape. #fff899
- Steppe - Dry and cold grass open plains. #e7f79c
- Grassland - Green grassy open plains, richer soil. #95c663
- Shrubland - Woody shrubs and bushes, patchy grass. Often transitional. #cccc00
- Maquis - Dense, thick and rugged evergreen shrublands. #667621
- Woodland - Open canopy-trees present but spaced. #7aad43
- Forest - Closed canopy. #39912d
- Beach - #fff899
- River - #85d1e0ff
- Lake - #a3ccf5ff
- Sea - Saltwater tile. #99ccff
- Ocean - Non-traversable #006699