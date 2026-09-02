"""
Humanize a research paper's body prose while preserving structure.
- Skips headers, short labels, table captions, and the References section.
- Faithful mode (no translation laundering) to protect technical accuracy.
- Saves incrementally so a rate-limit crash doesn't lose progress.
"""
import sys, re
import power_humanizer as ph

blocks = [b for b in open("paper-input.txt", encoding="utf-8").read().split("\n\n") if b.strip()]

# find References section start
ref_idx = next((i for i, b in enumerate(blocks) if b.strip().upper() == "REFERENCES"), len(blocks))

def should_humanize(i, b):
    if i >= ref_idx:
        return False                      # references + declarations: keep exact
    w = b.split()
    if len(w) < 12:
        return False                      # headers / short labels
    if b.strip().startswith("Table "):
        return False                      # table captions
    if re.match(r"(?i)^keywords\s*[:：]", b.strip()):
        return False                      # keep keyword list verbatim
    if b.strip().isupper():
        return False                      # ALL-CAPS headers
    return True

out = []
total = sum(1 for i, b in enumerate(blocks) if should_humanize(i, b))
done = 0
for i, b in enumerate(blocks):
    if should_humanize(i, b):
        done += 1
        print(f"[block {i} | humanizing {done}/{total} | {len(b.split())}w]", file=sys.stderr)
        try:
            # faithful formal rewrite + de-tricolon/opening fixes, no laundering
            r = ph.humanize(b, do_launder=False, formal=True)
        except Exception as e:
            print(f"  [failed, keeping original: {e}]", file=sys.stderr)
            r = b
        out.append(r)
    else:
        out.append(b)                     # keep structure/references verbatim
    # save progress after every block
    open("paper-humanized.txt", "w", encoding="utf-8").write("\n\n".join(out) + "\n")

print(f"\n[done: humanized {done} prose blocks, kept {len(blocks)-done} structural/reference blocks]", file=sys.stderr)
print("[saved to paper-humanized.txt]", file=sys.stderr)
