# Personal methods lab. Does not invoke the 2023 GPU scripts.

PYTHON ?= python3

.PHONY: lab-list lab-baselines lab-metrics lab-catalog lab-rubric lab-validate lab-report lab-export test

lab-list:
	$(PYTHON) -m silverlab list

lab-baselines:
	$(PYTHON) -m silverlab baselines --id lab-01

lab-metrics:
	$(PYTHON) -m silverlab metrics --against abstractive

lab-catalog:
	$(PYTHON) -m silverlab catalog

lab-rubric:
	$(PYTHON) -m silverlab rubric

lab-validate:
	$(PYTHON) -m silverlab validate

lab-report:
	$(PYTHON) -m silverlab report --out examples/lab_report/index.html

lab-export:
	$(PYTHON) -m silverlab export-data

test:
	$(PYTHON) -m unittest discover -s tests -v
