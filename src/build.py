import argparse
import csv
from datetime import datetime
import functools
import re
import sqlite3
import string
import time
import unicodedata

CSV_COL_ID = "ID"
CSV_COL_ORIG = "GOÂNIÚ"
CSV_COL_NEW = "SIN PÁN"
CSV_COL_HAN = "HÀNJĪ"
CSV_COL_NOTE = "CHÙKÁI"
MARKED_DELETE = "刪除"
STRIP = string.punctuation + " "
LEGAL_INPUT = r"^[A-Za-z0-9 '-]+$"

TONE_SUBS = {
    '2': '\u0301',
    '3': '\u0300',
    '5': '\u0302',
    '7': '\u0304',
    '8': '\u030D',
    '9': '\u0306',
}

ROC_SUBS = [
    (r'ts', 'ch'),
    (r'ua', 'oa'),
    (r'ue', 'oe'),
    (r'oo', 'o\u0358'),
    (r'ing', 'eng'),
    (r'ik', 'ek'),
    (r'nn', '\u207F'),
    (r'Ts', 'Ch'),
    (r'Ua', 'Oa'),
    (r'Ue', 'Oe'),
    (r'Oo', 'O\u0358'),
    (r'Ing', 'Eng'),
    (r'Ik', 'Ek'),
    (r'nn', '\u207F'),
]

ROC_SUBS_ASCII = [
    (r'ts', 'ch'),
    (r'ua', 'oa'),
    (r'ue', 'oe'),
    (r'oo', 'ou'),
    (r'ing', 'eng'),
    (r'ik', 'ek'),
    (r'Ts', 'Ch'),
    (r'Ua', 'Oa'),
    (r'Ue', 'Oe'),
    (r'Oo', 'Ou'),
    (r'Ing', 'Eng'),
    (r'Ik', 'Ek'),
]

def get_cursor(file):
    con = sqlite3.connect(file)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    return cur

def tone_index(text):
    match = re.match(r'o[ae][a-z]', text, re.I)
    if match is not None:
        return match.start() + 2
    else:
        for v in ['o', 'O', 'a', 'A', 'e', 'E', 'u', 'U', 'i', 'I', 'n', 'N', 'm', 'M']:
            index = text.find(v)
            if index > -1:
                return index + 1

def rojascii_to_pojascii(text):
    for sub in ROC_SUBS_ASCII:
        text = re.sub(sub[0], sub[1], text)
    return text

def rocascii_to_poj(text):
    text = unicodedata.normalize('NFD', text)
    for sub in ROC_SUBS:
        text = re.sub(sub[0], sub[1], text)
    tone = None
    if '235789'.find(text[-1]) > -1:
        tone = text[-1]
        text = text[:-1]
        index = tone_index(text)
        text = text[0:index] + TONE_SUBS[tone] + text[index:]
    return unicodedata.normalize('NFC', text)

def get_row_toj(row):
    orig = row[CSV_COL_ORIG]
    new = row[CSV_COL_NEW]

    toj = ''
    i = 0

    # if orig == 'si7-m7-si7':
    #     print('ok')

    for orig_chat in re.split(r'[ -]+', orig):
        j = i + len(orig_chat)
        new_chat = new[i:j]
        if orig_chat.lower() == new_chat.lower():
            toj += rocascii_to_poj(new_chat)
            i += len(orig_chat)
            while i < len(new) and re.match(r'\W', new[i]):
                toj += new[i]
                i += 1
    return toj

def skip_row(row):
    return row[CSV_COL_ORIG].strip(STRIP) == '' \
        or row[CSV_COL_NEW].strip(STRIP) == '' \
        or row[CSV_COL_NOTE].find(MARKED_DELETE) > -1

def alpha_only(reading):
    return ''.join(ch for ch in reading if ch.isalpha())

def get_qstrings(reading):
    roc_reading = reading.lower()
    poj_reading = rojascii_to_pojascii(roc_reading)
    roc_alphas = alpha_only(roc_reading)
    poj_alphas = alpha_only(poj_reading)

    syls = re.split(r'-+', roc_reading)
    n_syls = len(syls)

    if n_syls == 1:
        return [poj_reading] if poj_reading == roc_reading else [poj_reading, roc_reading]
    if n_syls == 2:
        return [poj_alphas] if poj_alphas == roc_alphas else [poj_alphas, roc_alphas]
    else:
        roc_initials = ''
        poj_initials = ''
        for syl in syls:
            m = re.match(r'tsh?|[ptk]h', syl, re.IGNORECASE)
            init = syl[m.start():m.end()] if m is not None else syl[0]
            roc_initials += init
            poj_initials += init.replace('ts', 'ch')
        if poj_initials == roc_initials and poj_alphas == roc_alphas:
            return [poj_initials, poj_alphas]
        elif poj_initials == roc_initials and poj_alphas != roc_alphas:
            return [poj_initials, poj_alphas, roc_alphas]
        else:
            return [poj_initials, roc_initials, poj_alphas, roc_alphas]

def build_db(file, word_list, qstring_list):
    now = datetime.now()
    con = sqlite3.connect(file)
    con.executescript(f'''
        DROP TABLE IF EXISTS words;
        DROP TABLE IF EXISTS qstring_word_mappings;
        DROP TABLE IF EXISTS cooked_information;
        CREATE TABLE words (id INTEGER PRIMARY KEY, reading, value, probability);
        CREATE TABLE qstring_word_mappings (qstring, word_id);
        CREATE TABLE cooked_information (key, value);
        INSERT INTO cooked_information VALUES
            ('version_timestamp', '{now.strftime("%Y%m%d")}'),
            ('cooked_timestamp_utc', '{round(time.time(), 1)}'),
            ('cooked_datetime_utc', '{now.strftime("%Y-%m-%d %H:%M UTC")}');

        CREATE INDEX words_index_key ON words (reading);
        CREATE INDEX qstring_word_mappings_index_qstring ON qstring_word_mappings (qstring);
    ''')

    words_table = []
    qstrings_table = []

    has_error = False

    for row in word_list:
        if row['value'] == '':
            print(f'Error in row {row["reading"]}')
            has_error = True
        words_table.append((row['id'], row['reading'], row['value'], 1))
    
    if has_error:
        print("Please correct errors in database.")
        quit()

    for row in qstring_list:
        qstrings_table.append((row['qstring'], row['word_id']))

    c = con.cursor()
    c.executemany('INSERT INTO words VALUES (?, ?, ?, ?)', words_table)
    c.executemany('INSERT INTO qstring_word_mappings VALUES (?, ?)', qstrings_table)
    con.commit()
    con.execute('VACUUM')
    con.close()


##############################################################################
#
# __main__
#
##############################################################################

parser = argparse.ArgumentParser(
    description="""Build FHL Database""",
    formatter_class=argparse.RawDescriptionHelpFormatter)

def read_csv(filename):
    ret = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if skip_row(row):
                continue
            row[CSV_COL_ORIG] = row[CSV_COL_ORIG].strip(STRIP)
            row[CSV_COL_NEW] = row[CSV_COL_NEW].strip(STRIP)
            row[CSV_COL_HAN] = row[CSV_COL_HAN].strip(STRIP)

            # One-offs...
            if row[CSV_COL_ORIG] == '2-Jun':
                row[CSV_COL_ORIG] = 'jun2'
                row[CSV_COL_NEW] = 'jun2'
            if row[CSV_COL_ORIG] == '7-Jun':
                row[CSV_COL_ORIG] = 'jun7'
                row[CSV_COL_NEW] = 'jun7'

            ret.append(row)
    return ret

def check_parse_error(row):
    id = row[CSV_COL_ID]
    orig = row[CSV_COL_ORIG]
    toj = row[CSV_COL_NEW]

    parse_error = False

    if not re.match(LEGAL_INPUT, orig):
        print(f"Chhògō͘ ID: {id}, GOÂNIÚ: {orig}")
        parse_error = True
    if not re.match(LEGAL_INPUT, toj):
        print(f"Chhògō͘ ID: {id}, TOJ: {toj}")
        parse_error = True

    return parse_error

def main(args):
    input_file = args.input if args.input else 'data/db.csv'
    output_file = args.output if args.output else 'data/TalmageOverride.db'

    word_list = []
    qstring_list = []

    id = 1
    inputs = read_csv(input_file)
    parse_error = False
    for row in inputs:
        if not row:
            continue
        parse_error = check_parse_error(row)
        if parse_error:
            continue

        toj = get_row_toj(row)
        word_list.append({
            'id': id,
            'reading': row[CSV_COL_ORIG].lower(),
            'value': toj,
        })
        qstrings = get_qstrings(row[CSV_COL_ORIG])
        for qstr in qstrings:
            qstring_list.append({
                'qstring': qstr,
                'word_id': id
            })
        id += 1

        if row[CSV_COL_HAN]:
            word_list.append({
                'id': id,
                'reading': row[CSV_COL_ORIG].lower(),
                'value': row[CSV_COL_HAN],
            })
            for qstr in qstrings:
                qstring_list.append({
                    'qstring': qstr,
                    'word_id': id
                })
            id += 1

    if parse_error:
        print("Please fix errors and try again.")
        quit()

    qstring_list = sorted(qstring_list, key=lambda x: x['qstring'])
    build_db(output_file, word_list, qstring_list)

### entry point ###

parser.add_argument('-i', "--input", metavar='FILE', required=True, help='csv input file')
parser.add_argument('-o', "--output", metavar='FILE', required=False, help='the output database file (TalmageOverride.db)')

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
