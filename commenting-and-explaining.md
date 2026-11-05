# Skill: commenting-and-explaining
The owner is a beginner in astronomy data and wants to LEARN from the code.

## Every function
A docstring with: What it does (one line) / Why we need it (one line) / Inputs and shapes / Output.
## Every non-obvious line
A short plain-English comment. Prefer "why" over "what". Mention array shapes: # (5, H, W).
## Astronomy words
First time a term appears in a file, add a "Beginner note:" comment, e.g.
# Beginner note: a "band" is one color filter (g, r, i, z, y). Same sky, five filtered images.
# Beginner note: MAD (median absolute deviation) is a noise estimate that ignores outliers.
## Style
Short sentences, simple words, no jargon without a note. No walls of text.
## Example
```python
def normalize_band(img):
    """What: clean one band and compress its brightness range.
    Why: a few very bright pixels (point-source cores) would otherwise drown the faint structure.
    In: img, array (H, W). Out: array (H, W), float32."""
    img = np.nan_to_num(img.astype("float32"))             # replace NaN/inf with 0 so math doesn't break
    med = np.median(img)                                    # typical sky background level
    mad = 1.4826 * np.median(np.abs(img - med)) + 1e-8      # noise size (sigma); 1e-8 avoids divide-by-zero
    return np.arcsinh((img - med) / mad)                    # arcsinh squashes bright values, keeps faint ones
```
