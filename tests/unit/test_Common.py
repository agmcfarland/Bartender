import re
from Utils.Common import find_subtring_match

def test_find_subtring_match():
	"""
	python -m slipcover -m pytest -sv tests/unit/test_Common.py::test_find_subtring_match
	"""
	test_subject = [re.compile(subj) for subj in ['alex', 'kevin', 'chris', 'andrew']]

	store_results = []
	for test_query in ['alex.2', 'kevin_1', '__chrisxx_', 'andrewandrew']:

		store_results.append(find_subtring_match(test_query, test_subject))

	assert len(store_results) == 4

	assert store_results == ['alex', 'kevin', 'chris', 'andrew']


