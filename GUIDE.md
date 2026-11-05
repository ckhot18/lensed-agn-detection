# GUIDE.md — everything you need to know before starting (for YOU, not the agent)

## 1. The 60-second picture
You get tiny sky images (cutouts), five filtered versions of each (g, r, i, z, y). Some contain a
lensed AGN: a bright, star-like quasar whose light was bent by a galaxy into 2 (double) or 4 (quad)
copies. Others are contaminants: galaxies, stars, ordinary AGN. Your model gives each object a score
from 0 to 1. The organizers judge how well your scores separate the two on a hidden test set.
The data are simulated, by two different recipes: SLSim (D1, fully synthetic) and SIMCT (D2, real
sky patches with injected objects, degraded to LSST-like quality). The hidden test set will not look
exactly like your training set. That gap is your research topic.
Deadline: 2026-11-30 23:59 UTC. The test set was "to be generated soon": check the site often.

## 2. Your workflow loop
1. Type "do phase N" to the agent.
2. It works, makes figures, updates STATE.md and DECISIONS.md, commits and pushes.
3. YOU open the figures listed in its reply and check the "what you verify" items below.
4. Only then say "do phase N+1".
Other prompts: "resume" (after a break or agent switch), "review phase N", "status", "explain X".
Do not skip your checks. The agent cannot tell when a picture looks wrong to a human eye.

## 3. What YOU check after each phase
| Phase | You check |
|-------|-----------|
| 0 | Push works. Data is not in git (GitHub repo shows no big files). |
| 1 | Open the lens grids. Can you spot the multiple point sources? Compare D1 and D2: do they look different (noise, blur)? Counts make sense? |
| 2 | Augmentation demo: all 5 bands rotate together. Tests green. |
| 3 | If a dumb statistics model separates lenses well, something is a shortcut. Ask the agent why. |
| 4 | Gallery: are the false positives understandable (star next to a galaxy)? |
| 5 | Only the initialization differs between the two ResNets. Error bars shown. |
| 6 | Same splits for every band set. Is one band clearly best or worst? |
| 7 | The off-diagonal cells of the heatmap. How big is the drop? |
| 8 | Look at the worst failures yourself and write 3 plain observations. |
| 9 | Submission matches the rules. Upload it yourself. |
| 10 | README commands work from a fresh clone. |

## 4. Red flags (stop and ask)
- AUC near 1.0 on the first try. Likely leakage or a shortcut.
- Validation much better than the same model on the holdout.
- All predictions are about the same value.
- Different seeds give wildly different scores (too little data, or a bug).
- Huge gap between D1 and D2 (domain shift: real, and interesting. Report it.)
- The agent says "I assumed the cutout size". It must inspect or ask.

## 5. Ideas you must understand (short)
- Leakage: validation looks good for the wrong reason. Our guard: split by object, never by file.
- Shortcut learning: the model learns how the data was made (noise level, border) instead of what a lens looks like.
- Domain shift: test data differ from training data. Two kinds: images look different (D1 vs D2), and class balance
  differs (training 50/50, real lenses are rare).
- Why accuracy is not enough: with rare lenses, precision = TPR*pi / (TPR*pi + FPR*(1-pi)). With TPR 0.9, FPR 1%
  and 1% lenses, precision is about 0.48. That is why we report TPR at fixed small FPR.
- Seeds: one run is luck. Three or more runs with mean and std is a result.
- Static search: one deep image, no light curves over time.

## 6. Compute plan
Local machine: code, tests, small dataset, smoke tests. Colab/Kaggle GPU: long runs.
You do not need all 200k objects to learn something. Start with the small dataset (4000 objects) and scale up only
after Phase 5. See SETUP.md.

## 7. Git basics
The agent commits and pushes for you. You never commit data, zips or model weights. If something looks wrong:
git log --oneline | head, and ask the agent to "review phase N".

## 8. Switching agents
Open the repo in the new agent. Say: "Read AGENTS.md and STATE.md, then resume."
That is all it needs. If it asks you what was done, STATE.md was not updated properly: tell the old agent to fix it.

## 9. Timeline (today is 2026-11-05, 25 days left)
- Nov 5-8: Phases 0-2 (setup, data, splits)
- Nov 9-13: Phases 3-5 (baselines, CNN, ResNet scratch vs pretrained)
- Nov 14-20: Phases 6-8 (bands, transfer, failures)
- Nov 20-27: Phase 9 when the test set is out, then Phase 10
- Nov 28-30: buffer. Do not plan to finish on the last day.
If you get squeezed, finish Phases 0-5 and 8 first. They already make a decent write-up.

## 10. Turning this into a blog or paper
Title idea: "What makes a lensed-AGN classifier robust across simulation pipelines?"
Core results to report: bands (6), transfer matrix (7), pretrained vs scratch (5), failures (8).
Always say "in these simulations". Co-authorship on the organizers' paper depends on a unique method plus
your help describing it: when you submit, include your methodology and links. A short blog post comes first; an
arXiv note can follow if the results are interesting (a first-time author may need an endorser).

## 11. Still UNKNOWN (agent must verify, you can help)
Cutout size, FITS layout, label tables (doubles/quads, contaminant type), official metric, submission format,
test release date, the realistic validation set. Paste the Evaluation and Submission text from the site to the agent when you see it.

## 12. Mini glossary
Band: one color filter. Coadd: stacked exposures. Cutout: small image around an object. PSF: blur.
AGN: black hole eating gas, bright point source. Lensed: light bent into multiple images. Contaminant: look-alike non-lens.
Doubles/quads: 2 or 4 lensed images. TPR/FPR: caught-lens rate / false-alarm rate. TTA: test-time augmentation.
