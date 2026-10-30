"""Clean a sheet export before building.

Applies hand-reviewed fixes (a CSV of ID, column, old, new, note) and a few
safe automatic rules, then writes the cleaned CSV plus a log of every change
so the same edits can be made in the Google Sheet.
"""
import argparse
import csv
from functools import lru_cache
import re
import unicodedata

from build import CSV_COL_HAN, CSV_COL_ID, CSV_COL_NEW, CSV_COL_NOTE, CSV_COL_ORIG, MARKED_DELETE, get_row_toj, rocascii_to_poj

INITIAL = r'(?:tsh|ts|chh|ch|ph|th|kh|ng|[pbmtnlkghsj])?'
RHYME = (r'(?:(?:iau|uai|oai|ai|au|ia|io|iu|ua|ue|ui|oa|oe|oo|ou|er|ir|ee|[aeiou])'
         r'(?:nnh?|ng|[mnptkh])?|(?:ng|m)h?)')
SYLLABLE = re.compile(f'{INITIAL}{RHYME}[235789]?', re.I)
ONSETLESS = re.compile(r'[aeiou]|(?:ng|m)h?[235789]?$', re.I)
CODA = re.compile(r'(?:ng|[mptkh]|[^n]n)[235789]?$', re.I)
PARENTHESIZED = re.compile(r'[(（][^)）]*[)）]')
LOMAJI_RUN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)*")
TONE_1_4 = re.compile(r'(?<=[A-Za-z])[14](?![0-9])')
HANJI = r'[㐀-鿿\U00020000-\U0003ffff]'
MISPLACED_TONE = re.compile(rf'(?<![A-Za-z])([A-Za-z]+)({HANJI}+)([235789])(?![A-Za-z0-9])')


def toneless(syllable):
    return re.sub(r'\d', '', syllable.lower())


def known_syllables(orig):
    return {toneless(s) for s in re.split(r"[ '-]+", orig) if s}


def split_syllables(word, known=frozenset()):
    """Split joined TL/POJ syllables. Among the possible splits, prefer the one
    using syllables from `known` (the row's GOÂNIÚ), then the fewest
    vowel-initial syllables, then the fewest final consonants ("kiki" is
    ki-ki, not kik-i; "saikhia" is sai-khia, not saik-hia; with known "suat",
    "suatsuat" is suat-suat, not sua-tsuat). Returns None if it doesn't parse."""
    @lru_cache(maxsize=None)
    def parse(i):
        if i == len(word):
            return (0, 0, 0), []
        best = None
        for j in range(i + 1, min(len(word), i + 10) + 1):
            syllable = word[i:j]
            if not SYLLABLE.fullmatch(syllable):
                continue
            rest = parse(j)
            if rest is None:
                continue
            (unknown, onsetless, codas), syllables = rest
            cost = (unknown + (toneless(syllable) not in known),
                    onsetless + bool(ONSETLESS.match(syllable)),
                    codas + bool(CODA.search(syllable)))
            if best is None or cost < best[0]:
                best = (cost, [syllable] + syllables)
        return best
    result = parse(0)
    return result[1] if result else None


def realign_orig(new, orig=''):
    """Rebuild a hyphenated GOÂNIÚ from SIN PÁN's syllables."""
    known = known_syllables(orig)
    syllables = []
    for chunk in re.split(r"[ '-]+", new.strip()):
        parts = split_syllables(chunk, known)
        if parts is None:
            return None
        syllables += parts
    return '-'.join(syllables)


def snap_separators(orig, new):
    """Move SIN PÁN's spaces/apostrophes/hyphens that sit one letter off a
    GOÂNIÚ syllable boundary ("bo5s ioh8" → "bo5 sioh8"). Returns None if a
    separator is further off than that."""
    boundaries, k = set(), 0
    for syllable in re.split(r'[ -]+', orig):
        k += len(alnum(syllable))
        boundaries.add(k)
    letters, separators, k = [], {}, 0
    for ch in new:
        if ch.isalnum():
            letters.append(ch)
            k += 1
        else:
            separators.setdefault(k, '')
            separators[k] += ch
    snapped = {}
    for k, sep in separators.items():
        target = next((t for t in (k, k - 1, k + 1) if t in boundaries), None)
        if target is None:
            return None
        snapped.setdefault(target, sep)
    return ''.join(snapped.get(i, '') + ch for i, ch in enumerate(letters))


def aligns(orig, new):
    try:
        get_row_toj({CSV_COL_ORIG: orig, CSV_COL_NEW: new})
        return True
    except ValueError:
        return False


def is_latin_mark(ch):
    return unicodedata.category(ch) == 'Mn' or ch == 'ⁿ' or \
        (ord(ch) > 0x7F and unicodedata.name(ch, '').startswith('LATIN'))


def convert_hanji_lomaji(text, orig=''):
    """Convert TL or tone-number lomaji embedded in HÀNJĪ to POJ.

    Only touches ASCII runs that parse completely as syllables, are not glued
    to POJ letters (e.g. "tsinná2", left for a human) and are not inside
    parentheses (English or Japanese glosses). A tone digit typed after the
    Hànjī that follows a syllable ("tshe尾2") is moved back to the syllable."""
    known = known_syllables(orig)
    text = MISPLACED_TONE.sub(r'\1\3\2', text)
    skip = [m.span() for m in PARENTHESIZED.finditer(text)]

    def convert(m):
        run = m.group(0)
        start, end = m.span()
        if any(a <= start < b for a, b in skip):
            return run
        if (start > 0 and is_latin_mark(text[start - 1])) or (end < len(text) and is_latin_mark(text[end])):
            return run
        pieces = []
        for piece in run.split("'"):
            syllables = split_syllables(piece, known)
            if syllables is None:
                return run
            # "ou" is an ASCII stand-in for o͘
            pieces.append(''.join(rocascii_to_poj(s.replace('ou', 'oo')) for s in syllables))
        return "'".join(pieces)

    return LOMAJI_RUN.sub(convert, text)


def normalize_text(text):
    text = unicodedata.normalize('NFC', text)
    text = text.replace('’', "'").replace('‘', "'")
    return re.sub(r' {2,}', ' ', text).strip()


def alnum(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())


def apply_fixes(rows_by_id, fixes_file, log):
    with open(fixes_file, encoding='utf-8', newline='') as f:
        for fix in csv.DictReader(f):
            row = rows_by_id[fix['ID']]
            col, old, new = fix['column'], fix['old'], fix['new']
            current = unicodedata.normalize('NFC', row[col])
            if current == unicodedata.normalize('NFC', new):
                continue
            if current != unicodedata.normalize('NFC', old):
                raise SystemExit(f'Fix for ID {fix["ID"]} {col}: expected "{old}", found "{row[col]}"')
            row[col] = new
            log.append((fix['ID'], col, old, new, fix['note']))


def set_value(row, col, value, rule, log):
    if row[col] != value:
        log.append((row[CSV_COL_ID], col, row[col], value, rule))
        row[col] = value


def clean_row(row, log):
    for col in (CSV_COL_ORIG, CSV_COL_NEW, CSV_COL_HAN):
        set_value(row, col, normalize_text(row[col]), 'normalize', log)
    if MARKED_DELETE in row[CSV_COL_NOTE]:
        return
    set_value(row, CSV_COL_HAN, convert_hanji_lomaji(row[CSV_COL_HAN], row[CSV_COL_ORIG]), 'HÀNJĪ lomaji → POJ', log)
    for col in (CSV_COL_ORIG, CSV_COL_NEW):
        set_value(row, col, TONE_1_4.sub('', row[col]), 'tone 1/4 digit dropped', log)
    orig, new = row[CSV_COL_ORIG], row[CSV_COL_NEW]
    if not new or aligns(orig, new):
        return
    if alnum(orig) == alnum(new):
        snapped = snap_separators(orig, new)
        if snapped and aligns(orig, snapped):
            set_value(row, CSV_COL_NEW, snapped, 'SIN PÁN space moved to syllable boundary', log)
            return
    realigned = realign_orig(new, orig)
    if realigned:
        set_value(row, CSV_COL_ORIG, realigned, 'GOÂNIÚ follows SIN PÁN', log)


def review_reason(row):
    """Why a cleaned row still needs a human, or None."""
    if MARKED_DELETE in row[CSV_COL_NOTE]:
        return None
    han = PARENTHESIZED.sub('', row[CSV_COL_HAN])
    if not row[CSV_COL_NEW]:
        return 'SIN PÁN empty (row is skipped)'
    if not aligns(row[CSV_COL_ORIG], row[CSV_COL_NEW]):
        return 'SIN PÁN does not match GOÂNIÚ'
    if not han:
        return 'HÀNJĪ empty'
    if re.search(r'\d', han):
        return 'HÀNJĪ has tone digits'
    if re.search(r'[-*●]', han):
        return 'HÀNJĪ has placeholder or private-use characters'
    return None


def main(args):
    with open(args.input, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    rows_by_id = {row[CSV_COL_ID]: row for row in rows}

    log = []
    for fixes_file in args.fixes or []:
        apply_fixes(rows_by_id, fixes_file, log)
    for row in rows:
        clean_row(row, log)

    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with open(args.changes, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'column', 'old', 'new', 'note'])
        writer.writerows(log)
    print(f'{len(log)} changes written to {args.changes}')

    if args.review:
        review = [(row, review_reason(row)) for row in rows]
        review = [(row, reason) for row, reason in review if reason]
        with open(args.review, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', CSV_COL_ORIG, CSV_COL_NEW, CSV_COL_HAN, CSV_COL_NOTE, 'problem'])
            for row, reason in review:
                writer.writerow([row[CSV_COL_ID], row[CSV_COL_ORIG], row[CSV_COL_NEW], row[CSV_COL_HAN], row[CSV_COL_NOTE], reason])
        print(f'{len(review)} rows to review written to {args.review}')


parser = argparse.ArgumentParser(description='Clean the FHL sheet export')
parser.add_argument('-i', '--input', required=True, help='sheet export CSV')
parser.add_argument('-o', '--output', required=True, help='cleaned CSV')
parser.add_argument('-c', '--changes', required=True, help='CSV log of every change')
parser.add_argument('-f', '--fixes', action='append', help='hand-reviewed fixes CSV (repeatable)')
parser.add_argument('-r', '--review', help='CSV of rows that still need a human')

if __name__ == '__main__':
    main(parser.parse_args())
