PYTHON=python3
PIP=pip3
MAINFILE=src/main.py

default: run

###########################################
# Install
###########################################
install: requirements.txt
	$(PIP) install -r requirements.txt

###########################################
# Runners
###########################################
run: install
	$(PYTHON) $(MAINFILE)


###########################################
# Cleanup
###########################################
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm
