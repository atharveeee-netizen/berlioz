.PHONY: test verify clean

test:
	python -m unittest discover -s tests -p "test_*.py" -v

verify:
	python verify_harness.py --bench $(if $(BENCH),$(BENCH),all) --salts $(if $(SALTS),$(SALTS),3)

clean:
	rm -rf build/*.kmb results/*.json
