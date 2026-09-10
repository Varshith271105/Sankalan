"""
POWER humanizer — combines every technique that works, tuned iteratively vs ZeroGPT.

Pipeline (per paragraph):
  1. LAUNDER    : EN -> Chinese -> Japanese -> Finnish -> EN
                  (OpenRouter free LLM for the language rewrites + Google Translate hop).
                  Destroys the statistical fingerprint detectors read.
  2. REWRITE    : blader 35-pattern + heavy burstiness/perplexity rewrite (OpenRouter LLM).
                  Fixes translation artifacts, removes AI tells, varies rhythm hard.
  3. CLEAN      : strip punctuation tells (curly quotes, em/en dashes, non-breaking spaces).

All free (OpenRouter free model + Google Translate). Runs in the cloud; no local RAM.

Usage:
  python power_humanizer.py -f input.txt -o output.txt [--no-launder] [--model M]
  from power_humanizer import humanize ; humanize(text)
"""
import os, sys, re, json, time, argparse, urllib.request, urllib.error

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def _env(name, default=""):
    if os.environ.get(name):
        return os.environ[name]
    try:
        for line in open(os.path.join(os.path.dirname(__file__) or ".", ".env"), encoding="utf-8"):
            s = line.strip()
            if s.startswith(name + "="):
                return s.split("=", 1)[1].strip()
    except FileNotFoundError:
        pass
    return default

OPENROUTER_KEY = _env("OPENROUTER_API_KEY")
MODEL = _env("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
OR_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_KEY = _env("GEMINI_API_KEY")
GEMINI_MODEL = _env("GEMINI_MODEL", "gemini-flash-lite-latest")

REWRITE_SYSTEM = """You are a human editor rewriting text so it reads like a real person wrote it, not a chatbot. Keep the meaning; do not invent facts.

Apply ALL of these:
1. VARY SENTENCE LENGTH HARD. Mix very short sentences (3-6 words) with long winding ones (25+ words). Never let two neighbouring sentences have similar length. This matters most.
2. Use less predictable, concrete wording. Avoid the most generic phrasing. A surprising-but-apt word here and there.
3. Delete AI-tell transitions completely: Moreover, Furthermore, Additionally, In conclusion, It is important to note, First and foremost, Overall, In summary.
4. Cut inflated/sales phrasing: "plays a vital role", "stands as a testament", "in today's fast-paced world", "transformative", "game-changer", "landscape", "delve", "leverage", "robust", "vibrant".
5. Use simple verbs (is, has, uses) instead of "serves as / represents / boasts".
6. Add mild human texture where it fits: a short aside, a rhetorical question, a contraction, an uneven rhythm. Do not overdo it.
7. No em dashes, no semicolons, no curly quotes, no emojis, no bold, no lists unless the input had them.
8. Keep it roughly the same length. Output ONLY the rewritten text, no notes."""

FORMAL_SYSTEM = """You are a human researcher rewriting text for a peer-reviewed paper. Keep the EXACT meaning and all facts. Add no examples, opinions, jokes, metaphors, or anything not in the source. Stay serious and professional, at the level a journal reviewer would accept. Professional does NOT mean uniform. Skilled human academic prose is irregular, and that irregularity is the goal.

Apply ALL of these, hardest first:
1. STRONG sentence-length variation. In every paragraph include at least one short sentence (4 to 9 words) AND at least one long sentence (28+ words), and place a short one directly after a long one at least once. Spread the lengths widely; do not let many sentences cluster in the 12-20 word band.
2. VARY SENTENCE OPENINGS. Never begin consecutive sentences with the same word or the same grammatical shape. Avoid starting many sentences with "The", "This", "These", or the main subject noun. Open some sentences with a subordinate clause, a prepositional phrase, a condition, an adverb, or occasionally And/But/Yet/So.
3. DESTROY groups of three and parallel lists. Never write "X, Y, and Z" series of three or more parallel items, and never use a colon to introduce such a list. Break them up: keep one or two items in a sentence, move the rest into separate sentences with DIFFERENT grammar, or drop redundant ones. No two adjacent clauses should share a parallel rhythm.
4. RAISE PERPLEXITY within a formal register. Replace generic, expected phrasing with precise, specific, less-predictable academic wording a domain expert would actually use. Prefer concrete nouns and exact verbs over abstract filler. Keep every number, name, and technical term from the source exactly.
5. VARY CLAUSE STRUCTURE. Mix simple, compound, and complex sentences. Do not let every sentence run subject-verb-object. Use an occasional measured hedge ("arguably", "on the available evidence", "in most reported cases") and the academic first-person plural ("we", "our analysis") where natural.
6. Break uniform paragraph shape. Do not make every paragraph a topic sentence, then even support, then a neat closing line. Let the emphasis fall unevenly.
7. Delete AI-tell transitions entirely: Moreover, Furthermore, Additionally, In conclusion, It is important to note, First and foremost, Overall, In summary, Notably, and Consequently as an opener.
8. Cut inflated phrasing: "plays a vital role", "stands as a testament", "transformative", "at its core", "in today's world", "landscape", "delve", "leverage", "robust", "vibrant", "game-changer", "underscores", "pivotal".
9. Simple verbs (is, has, uses) over "serves as / represents / boasts". Mostly active voice. No slang, no contractions, no em dashes, no semicolons, no curly quotes, no emojis, no bold, no lists unless the input had them.
10. Keep the same length and the same information. Output ONLY the rewritten text, no notes."""

PUNCT = {"‑": "-", "–": "-", "—": ", ", "‘": "'", "’": "'",
         "“": '"', "”": '"', "…": "...", " ": " "}

def clean(t):
    for k, v in PUNCT.items():
        t = t.replace(k, v)
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    t = re.sub(r",\s*,", ",", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()


def rudra_prepass(text, retries=3):
    """Run text through StealthHumanizer's rudra-free hosted model first (free, no key)."""
    url = "https://stealthhumanizer.vercel.app/api/humanize"
    body = json.dumps({"text": text, "model": "rudra-free", "intensity": "ninja"}).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, method="POST",
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            if d.get("fullText"):
                return d["fullText"]
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5); continue
            print(f"  [rudra pre-pass failed: {e}]", file=sys.stderr)
    return text


def _openrouter(messages, temperature=1.15, retries=5):
    # reasoning off: the free models are reasoning models and otherwise dump their
    # chain-of-thought into the output.
    # Cap output length to roughly the INPUT length so the model can't balloon the
    # text (nemotron will otherwise 7x the word count). ~1.5 tokens/word, x2 headroom.
    user_words = sum(len(m["content"].split()) for m in messages if m.get("role") == "user")
    max_toks = max(256, min(1400, int(user_words * 3)))
    body = {"model": MODEL, "messages": messages, "temperature": temperature,
            "top_p": 0.97, "max_tokens": max_toks, "reasoning": {"enabled": False}}
    data = json.dumps(body).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(OR_URL, data=data, method="POST", headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            # Free tier sometimes returns HTTP 200 with an error body (no 'choices').
            if "choices" not in d or not d["choices"]:
                msg = (d.get("error") or {}).get("message", str(d)[:120])
                if attempt < retries - 1:
                    w = 15 * (attempt + 1)
                    print(f"  [no completion ({msg}), waiting {w}s]", file=sys.stderr)
                    time.sleep(w); continue
                raise RuntimeError(f"OpenRouter returned no completion: {msg}")
            return d["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                w = 15 * (attempt + 1)
                print(f"  [429, waiting {w}s]", file=sys.stderr); time.sleep(w); continue
            raise


def _rewrite_lang(text, lang, temperature=1.15):
    msg = [
        {"role": "system", "content": "你是专业的多语言文案改写专家。"},
        {"role": "user", "content": f"翻译为{lang}，去掉 AI 味道，用不常见的、口语化的表达，句子长短交错，拟人化改写，只输出结果：\n{text}"},
    ]
    return _openrouter(msg, temperature)


def launder(text):
    from deep_translator import GoogleTranslator
    s1 = _rewrite_lang(text, "中文")
    s2 = _rewrite_lang(s1, "日语")
    # one non-LLM hop for extra structural distortion
    try:
        s3 = GoogleTranslator(source="ja", target="fi").translate(s2)
    except Exception:
        s3 = s2
    s4 = _openrouter([
        {"role": "system", "content": "You are a translator and editor."},
        {"role": "user", "content": "Translate the following into natural, human-sounding English "
         "with varied sentence lengths. Output only the English text:\n" + s3},
    ])
    return s4


def _gemini(system, user, temperature=0.7, retries=4):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {"temperature": temperature, "topP": 0.97, "maxOutputTokens": 4096},
    }
    data = json.dumps(body).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, method="POST",
                headers={"x-goog-api-key": GEMINI_KEY, "Content-Type": "application/json",
                         "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            parts = (d.get("candidates") or [{}])[0].get("content", {}).get("parts")
            if not parts:
                raise RuntimeError("gemini returned no content")
            return "".join(p.get("text", "") for p in parts).strip()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries - 1:
                w = 8 * (attempt + 1)
                print(f"  [gemini {e.code}, waiting {w}s]", file=sys.stderr); time.sleep(w); continue
            raise


# Reliable free OpenRouter fallback for the formal rewrite when Gemini is unavailable.
# minimax:free leaks meta-commentary, so use a sturdier model here.
FORMAL_FALLBACK_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

# Strip model meta-commentary / self-talk that free models sometimes leak into output.
_META_PATTERNS = [
    r"(?im)^\s*(let'?s|let us|now let'?s)\b.*$",
    r"(?im)^\s*(wait,|hold on|actually,|hmm,|okay,|ok,|sure,|here'?s|here is the).*$",
    r"(?im)^.*\b(rewrite|revise|rephrase)\s+(s\d|sentence|paragraph|this).*$",
    r'(?im)^\s*".*(as an opener|per the rule|per instruction).*"?!*\s*$',
    r"(?im)^\s*(sentence \d+|s\d+)\s*[:.\-].*$",
]

# Self-review commentary the model sometimes appends ("No three-item parallel lists
# remain. Sentence openings vary..."). Real academic prose never contains these.
_META_SENTENCE = re.compile(
    r"(parallel list|sentence opening|opening(s)? vary|clause structure|ai[- ]?tell|"
    r"inflated phrase|three[- ]item|(facts?|technical terms?|meaning|length)"
    r"[^.]{0,40}(preserved|unchanged|intact)|no (inflated|semicolon)|semicolons?,? or|"
    r"per (the )?(rule|instruction)|as (an|the) opener)", re.I)

def sanitize_meta(text):
    for pat in _META_PATTERNS:
        text = re.sub(pat, "", text)
    # drop any sentence that is self-review commentary about the rewrite itself
    sents = re.split(r"(?<=[.!?])\s+", text)
    kept = [s for s in sents if s.strip() and not _META_SENTENCE.search(s)]
    text = " ".join(kept)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


# Detects "A, B, and C" (or "A, B, C, and D") series of 3+ parallel items — the
# #1 thing ZeroGPT flags. Rough but catches the common academic tricolon.
_TRICOLON = re.compile(r"\w+[\w\s]*,\s+[\w\s]+,\s+(?:and|or)\s+[\w\s]+")

def count_tricolons(text):
    return len(_TRICOLON.findall(text))


def opening_problems(text):
    """Count sentence-opening monotony: consecutive same first word, or heavy The/This/These use."""
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    firsts = [re.sub(r"[^A-Za-z]", "", s.split()[0]).lower() for s in sents if s.split()]
    problems = 0
    for i in range(1, len(firsts)):
        if firsts[i] and firsts[i] == firsts[i - 1]:
            problems += 1
    stock = sum(1 for f in firsts if f in ("the", "this", "these", "it", "ai"))
    if firsts and stock / len(firsts) > 0.4:
        problems += 1
    return problems


DELIST_INSTR = ("\n\nCRITICAL: The previous version still contains lists of three or more parallel "
                "items (the 'A, B, and C' pattern). Find every such series and break it up: keep at "
                "most two items in any sentence, move the rest into separate sentences with different "
                "grammar, or drop redundant ones. No sentence may contain three comma-separated "
                "parallel items. Output ONLY the rewritten text.")


def _formal_rewrite(sysmsg, text):
    """Formal rewrite via Gemini flash-lite: fast, faithful (no padding), clean output.
    Falls back to OpenRouter only if Gemini is unavailable."""
    if GEMINI_KEY:
        try:
            return _gemini(sysmsg, "Rewrite this:\n\n" + text, temperature=0.7)
        except Exception as e:
            print(f"  [gemini failed, falling back to openrouter: {e}]", file=sys.stderr)
    return _openrouter([{"role": "system", "content": sysmsg},
                        {"role": "user", "content": "Rewrite this:\n\n" + text}],
                       temperature=0.6)


def rewrite(text, formal=False):
    sysmsg = FORMAL_SYSTEM if formal else REWRITE_SYSTEM
    if formal:
        return sanitize_meta(_formal_rewrite(sysmsg, text))
    return _openrouter([{"role": "system", "content": sysmsg},
                        {"role": "user", "content": "Rewrite this:\n\n" + text}])


def humanize(text, do_launder=True, formal=False, use_rudra=False):
    if not OPENROUTER_KEY:
        raise SystemExit("Set OPENROUTER_API_KEY in .env")
    if use_rudra:
        print("[rudra pre-pass...]", file=sys.stderr)
        text = rudra_prepass(text)
    paras = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    out = []
    for i, p in enumerate(paras, 1):
        r = p
        if do_launder:
            print(f"[para {i}/{len(paras)}] launder...", file=sys.stderr)
            try:
                r = launder(r)
            except Exception as e:
                print(f"  [launder failed: {e}]", file=sys.stderr)
        print(f"[para {i}/{len(paras)}] rewrite...", file=sys.stderr)
        r = rewrite(r, formal=formal)
        # Deterministic fix loop: tricolons and repeated openings are top ZeroGPT triggers.
        for attempt in range(2):
            tri = count_tricolons(r)
            opn = opening_problems(r)
            if tri == 0 and opn == 0:
                break
            print(f"  [fix pass {attempt+1}: {tri} tricolon(s), {opn} opening issue(s)]", file=sys.stderr)
            fix = ""
            if tri:
                fix += DELIST_INSTR
            if opn:
                fix += ("\n\nCRITICAL: Vary the sentence openings. Do not begin consecutive sentences "
                        "with the same word, and do not start more than a couple of sentences with "
                        "'The', 'This', 'These', 'It', or the subject noun. Recast openings using "
                        "subordinate clauses, prepositional phrases, conditions, or adverbs.")
            sysmsg = (FORMAL_SYSTEM if formal else REWRITE_SYSTEM) + fix
            try:
                if formal:
                    r = sanitize_meta(_formal_rewrite(sysmsg, r))
                else:
                    r = _openrouter([{"role": "system", "content": sysmsg},
                                     {"role": "user", "content": "Rewrite this:\n\n" + r}])
            except Exception as e:
                print(f"  [fix pass failed: {e}]", file=sys.stderr); break
        out.append(r)
    result = clean("\n\n".join(out))
    left = count_tricolons(result)
    if left:
        print(f"[warning: {left} tricolon(s) still present - consider re-running]", file=sys.stderr)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("-f", "--file")
    ap.add_argument("-o", "--output")
    ap.add_argument("--no-launder", action="store_true")
    ap.add_argument("--casual", action="store_true", help="casual register (default is formal, for research papers)")
    ap.add_argument("--rudra", action="store_true", help="add StealthHumanizer rudra-free pre-pass (off by default)")
    ap.add_argument("--model")
    a = ap.parse_args()
    global MODEL
    if a.model:
        MODEL = a.model
    text = open(a.file, encoding="utf-8").read() if a.file else a.text
    if not text:
        ap.error("provide text or --file")
    # Default: formal register, no rudra (rudra added little and was slow).
    result = humanize(text.strip(), do_launder=not a.no_launder,
                      formal=not a.casual, use_rudra=a.rudra)
    print("\n" + result)
    if a.output:
        open(a.output, "w", encoding="utf-8").write(result + "\n")
        print(f"\n[saved to {a.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
