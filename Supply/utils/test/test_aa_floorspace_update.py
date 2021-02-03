import unittest
import pandas
import logging

from utils.aa_floorspace_update import combine_frames, luz_squarefootages, \
    luz_subtype_ratios, calculate_residential_floorspace, add_floorspace_entry


class TestAAFloorspaceUpdate(unittest.TestCase):
    def test_combine_frames(self):
        frame_1 = pandas.DataFrame({
            'TAZ': [1, 2],
            'Commodity': ['single_family', 's'],
            'Quantity': [2, 1]
        })
        frame_2 = pandas.DataFrame({
            'TAZ': [1, 2, 3],
            'Commodity': ['single_family', 's', 's'],
            'Quantity': [2, 2, 1]
        })
        expected_answer = pandas.DataFrame({
            'TAZ': [1, 2, 3],
            'Commodity': ['single_family', 's', 's'],
            'Quantity': [2, 2, 1]
        })

        answer = combine_frames(frame_1, frame_2)
        logging.debug('testing {} rows'.format(len(answer)))
        for i in range(len(expected_answer)):
            logging.debug(answer.iloc[i])
            self.assertTrue(expected_answer.iloc[i].equals(answer.iloc[i]))

    def test_luz_squarefootages(self):
        mgra_frame = pandas.DataFrame({
            'LUZ': [1, 1, 1, 2, 2],
            'SqFt_SF': [200, 500, 500, 100, 0],
            'SqFt_MF': [100, 200, 300, 300, 0]
        })
        label = 'SqFt_SF'
        expected_answer = {1: 1200, 2: 100}
        self.assertEqual(
            expected_answer, luz_squarefootages(mgra_frame, label))
        multi_family_label = 'SqFt_MF'
        expected_answer = {1: 600, 2: 300}
        self.assertEqual(expected_answer, luz_squarefootages(
            mgra_frame, multi_family_label))

        mgra_frame = pandas.DataFrame({
            'LUZ': [1, 1, 1],
            'SqFt_SF': [200, 500, 500],
            'SqFt_MF': [100, 200, 300]
        })

    def test_luz_subtype_ratios(self):
        floorspace = pandas.DataFrame({
            'TAZ': [1, 2],
            'Commodity': ['s', 'm'],
            'Quantity': [100, 200]
        })
        subtypes = ['s']
        self.assertEqual(1, len(luz_subtype_ratios(floorspace, subtypes)))

    def test_add_floorspace_entry(self):
        # basic test with 100% of one product subtype
        single_family_commodity = "Single Family Detached Residential Economy"
        entry = (1, 100)
        # equal to the luz_subtype_ratios output
        ratios = {1: {single_family_commodity: 100}}
        output = []
        # an array of aa_luz_export.create_row return values
        expected_output = [{"TAZ": 1,
                            "Commodity": single_family_commodity,
                            "Quantity": 100}]
        # modifies output in place
        add_floorspace_entry(entry, ratios, output)
        self.assertEqual(expected_output, output)
        # tests with ratios
        entry = (1, 100)
        single_family_subtype_2 = "Single Family Detached Residential Luxury"
        ratios = {1: {
            single_family_commodity: 100,
            single_family_subtype_2: 100
        }}
        output = []
        expected_output = [
            {"TAZ": 1,
             "Commodity": single_family_commodity,
             "Quantity": 50},
            {"TAZ": 1,
             "Commodity": single_family_subtype_2,
             "Quantity": 50}
        ]
        add_floorspace_entry(entry, ratios, output)
        self.assertEqual(expected_output, output)

    def test_calculate_residential_floorspace(self):
        mgra_frame = pandas.DataFrame({
            'LUZ': [1, 1, 1],
            'SqFt_SF': [200, 500, 500],
            'SqFt_MF': [100, 200, 300]
        })
        floorspace_frame = pandas.DataFrame({
            'TAZ': [1, 2],
            'Commodity': [
                "Single Family Detached Residential Economy",
                "Single Family Detached Residential Luxury"
            ],
            'Quantity': [3000, 4000]
        })

        expected_answer = pandas.DataFrame({
            'TAZ': [1],
            'Commodity': ['Single Family Detached Residential Economy'],
            'Quantity': [1200.0]
        })
        answer = calculate_residential_floorspace(mgra_frame, floorspace_frame)
        print(answer)
        print(expected_answer)
        self.assertTrue(expected_answer.equals(answer))
#         luz_10013 = pandas.DataFrame({
#             10013,Single Family Attached Residential Luxury,1.2
# 10013,Single Family Detached Residential Economy,80553.42004
# 10013,Single Family Detached Residential Luxury,16315.71205
# 10013,Spaced Rural Residential Economy,11041.03894
# 10013,Spaced Rural Residential Luxury,2121.01975
#         })

# TODO:
# add the cases where:
# there are no floorspace entries for a subtype on an luz, but there needs to be a ratio for allocating to the subtypes
