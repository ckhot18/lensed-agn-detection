# Skill: fits-and-data
Use when: reading files, building the manifest, inspecting data.

## Filename pattern (training data)
D[x]_[y][id]_[z].fits   x: 1=SLSim, 2=SIMCT | y: N=non-lens, L=lens | id: 8 digits | z: g,r,i,z,y
```python
import re
PAT = re.compile(r"D(\d)_([NL])(\d{8})_([grizy])\.fits$")
def parse(path):
    pipe, cls, oid, band = PAT.search(path).groups()
    return f"D{pipe}", cls, oid, band          # obj_key = f"D{pipe}_{cls}_{oid}"
```
One FILE = one band of one object. Five files = one object. Group them by obj_key.

## Reading (do NOT assume the layout; see STATE.md "Verified facts")
```python
from astropy.io import fits
with fits.open(path) as hdul:
    hdul.info()          # shows HDUs. Image in primary? Or a table column? Check, then record it.
```
If the image is a normal array: `fits.getdata(path)`. If it sits in a table column, read that
column. Cast to float32. Never write to raw files.

## Manifest
Build ONCE: data/manifest/manifest.csv (obj_key, pipeline, cls, id, path_g..path_y, n_bands).
Everything else (splits, datasets) reads the manifest, never re-globs the disk.

## Checks every time
- NaN/inf/sentinel counts per band (log them).
- All 5 bands present per object; list the exceptions.
- Shapes identical across objects/bands. Log H, W and dtype.
- Test-set filenames carry only the band: figure out grouping by inspection (Phase 9).

## Speed
Reading thousands of tiny FITS files is slow. After Phase 2, optionally cache the subset in use as
data/cache/*.npy (float16 or float32), gitignored. Only cache what the current experiment needs.
