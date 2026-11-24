.PHONY: timeline stats test check
timeline:
	python3 -m decoder timeline samples/
stats:
	python3 -m decoder stats samples/
test:
	python3 -m unittest discover -s tests -t . -v
check:
	python3 tools/redact.py --check samples/
