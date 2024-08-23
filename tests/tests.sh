conda activate bar_project_env

cd /data/bar_lab/Bartender

coverage -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1_and_run2_run3_run4

coverage run -m pytest -sv tests/test_*.py && coverage report -m

python -m slipcover -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1_and_run2_run3_run4

python -m slipcover -m pytest -sv tests/unit/test_*.py

pytest tests/end_to_end --cov

pytest tests/unit --cov

# python -m slipcover -m pytest -sv tests/unit/test_StandardBarcodeName.py

# python -m slipcover -m pytest -sv tests/unit/test_SetupManager.py

# python -m slipcover -m pytest -sv tests/unit/test_FilePaths.py

# python -m slipcover -m pytest -sv tests/unit/test_Record.py

# python -m slipcover -m pytest -sv tests/unit/test_Stock.py

# python -m slipcover -m pytest -sv tests/unit/test_Experimental.py

# python -m slipcover -m pytest -sv tests/unit/test_ReportTable.py

# python -m slipcover -m pytest -sv tests/unit/end_to_end/test_simple.py

# python -m slipcover -m pytest -sv tests/unit/end_to_end/test_ete2.py

# python -m slipcover -m pytest -sv tests/unit/test_ReportTable.py::test_proportion_and_count_summary