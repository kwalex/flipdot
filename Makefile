init:
	pip install -r requirements.txt

sim:
	python3 flipdot/sim.py

demo:
	python3 demo.py udp

.PHONY: init sim demo
