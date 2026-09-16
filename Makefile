.PHONY: workbook test tables report quiz

workbook:
	python3 examples/run_workbook.py

test:
	python3 -m unittest discover -s tests -t . -v

tables:
	python3 -m kystlinje write-tables

report:
	python3 -m kystlinje report

quiz:
	python3 -m kystlinje quiz --answers

validate:
	python3 -m kystlinje validate
