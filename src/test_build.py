import unittest

from build import CSV_COL_NEW, CSV_COL_ORIG, get_row_toj
from clean import convert_hanji_lomaji, realign_orig, snap_separators, split_syllables


def toj(orig, new):
    return get_row_toj({CSV_COL_ORIG: orig, CSV_COL_NEW: new})


class GetRowTojTest(unittest.TestCase):
    def test_joined_spaced_apostrophe_and_hyphen(self):
        self.assertEqual(toj('ang5-kong2-a2-tau7', "ang5 kong2'a2 tau7"), "âng kóng'á tāu")
        self.assertEqual(toj('ang5-khi7', 'ang5khi7'), 'ângkhī')
        self.assertEqual(toj('au-a', 'Au-A'), 'Au-A')
        self.assertEqual(toj('ann3', 'ann3'), 'àⁿ')
        self.assertEqual(toj('hennh-khun3', 'hennhkhun3'), 'heⁿhkhùn')

    def test_misaligned_syllables_raise(self):
        with self.assertRaises(ValueError):
            toj('ho2-poo3', 'ho2 po3')
        with self.assertRaises(ValueError):
            toj('ing5-i7', 'ing5i7 phoksu7')


class CleanTest(unittest.TestCase):
    def test_split_syllables(self):
        self.assertEqual(split_syllables('ooian3'), ['oo', 'ian3'])
        self.assertEqual(split_syllables('kanggiap8'), ['kang', 'giap8'])
        self.assertEqual(split_syllables('uainnh'), ['uainnh'])
        self.assertEqual(split_syllables('kiki'), ['ki', 'ki'])
        self.assertEqual(split_syllables('saikhia'), ['sai', 'khia'])
        self.assertEqual(split_syllables('pinntiau5'), ['pinn', 'tiau5'])
        self.assertEqual(split_syllables('mng5'), ['mng5'])
        self.assertEqual(split_syllables('suatsuat', {'peh', 'suat'}), ['suat', 'suat'])
        self.assertIsNone(split_syllables('guitar'))

    def test_realign_orig_follows_sin_pan(self):
        self.assertEqual(realign_orig('ho2 po3'), 'ho2-po3')
        self.assertEqual(realign_orig("Kosoa"), 'Ko-soa')
        self.assertEqual(realign_orig('tshookhng hinn7'), 'tshoo-khng-hinn7')
        self.assertEqual(realign_orig('Pakisuthan'), 'Pa-ki-su-than')
        self.assertEqual(realign_orig('ting7 huainnhhuainnh'), 'ting7-huainnh-huainnh')
        self.assertEqual(realign_orig('tsi2 inui7', 'tsi2-in-ui3'), 'tsi2-in-ui7')
        self.assertEqual(realign_orig("ang5 kong2'a2 tau7"), 'ang5-kong2-a2-tau7')

    def test_snap_separators_to_syllable_boundaries(self):
        self.assertEqual(snap_separators('bo5-sioh8-bo5-lioh8', 'bo5s ioh8 bo5 lioh8'), 'bo5 sioh8 bo5 lioh8')
        self.assertEqual(snap_separators('me7-thinn-uan3-te7', 'me7 thin nuan3 te7'), 'me7 thinn uan3 te7')
        self.assertEqual(snap_separators('tua7-ku7-a2', "tua7k u7'a2"), "tua7 ku7'a2")
        self.assertIsNone(snap_separators('sim-kuann-ngi7', 'simkua nnngi7'))

    def test_convert_hanji_lomaji(self):
        self.assertEqual(convert_hanji_lomaji('手蹄a2'), '手蹄á')
        self.assertEqual(convert_hanji_lomaji('pangtsan7 gua2'), 'pangchān góa')
        self.assertEqual(convert_hanji_lomaji('金tshang花'), '金chhang花')
        self.assertEqual(convert_hanji_lomaji("tsiu2te5'a2"), "chiútê'á")
        self.assertEqual(convert_hanji_lomaji('tin3-sau3-tse'), 'tìn-sàu-che')
        self.assertEqual(convert_hanji_lomaji('kiki哮'), 'kiki哮')
        self.assertEqual(convert_hanji_lomaji('發hou7'), '發hō͘')
        self.assertEqual(convert_hanji_lomaji('inn-inn-ennh-ennh'), 'iⁿ-iⁿ-eⁿh-eⁿh')
        self.assertEqual(convert_hanji_lomaji('白suatsuat', 'peh8-suat-suat'), '白soatsoat')
        self.assertEqual(convert_hanji_lomaji('tsham錚5'), 'chhâm錚')
        self.assertEqual(convert_hanji_lomaji('tshe尾2'), 'chhé尾')
        self.assertEqual(convert_hanji_lomaji('猴tshe尾2'), '猴chhé尾')

    def test_convert_hanji_leaves_poj_and_glosses_alone(self):
        for text in ['紅kìkì', "gí'á(gear)", '克拉（carat）', 'phiànchih（ペンチ）', 'Koh活節', 'tsinná2', 'berh']:
            self.assertEqual(convert_hanji_lomaji(text), text)


if __name__ == '__main__':
    unittest.main()
