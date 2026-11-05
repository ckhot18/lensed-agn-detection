# Skill: visualization
The owner wants to SEE lenses, failures and results. Save PNG (dpi 150) to figures/ as phaseN_what.png.
After saving, add one line to figures/INDEX.md: filename | what it shows | how to read it.
Use matplotlib. Titles in plain words. Label axes. Show class and score on every image tile.

## Showing one object (5 bands + color composite)
- For display, take the normalized (asinh) band, then stretch to the 1st-99.5th percentile.
- imshow(cmap="gray", origin="lower"). One column per band g r i z y, label each.
- Composite: astropy.visualization.make_lupton_rgb(i_img, r_img, g_img, stretch=..., Q=8)
  with noise-normalized inputs (x - median) / MAD. Tune stretch by eye.

## Required figure types (see PHASES.md per phase)
- Grids: lenses vs non-lenses, per pipeline, all bands.
- Normalization before/after; augmentation demo (8 variants, bands aligned).
- Curves: loss and AUC per epoch.  ROC and Precision-Recall.  Score histograms (lens vs non-lens).
- Galleries: true/false positives and negatives with scores (16-20 tiles).
- Bars with error bars (mean +/- std over seeds) for experiment comparisons.
- Heatmap for the pipeline transfer matrix (annotate numbers).

## Rules
- Never display raw un-normalized pixels without a stretch (they look black).
- Galleries pick top-scored errors (hardest false positives, most confident misses), not random ones.
- Keep each figure readable on a laptop screen. No more than 20 tiles per image.
