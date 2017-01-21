default: run

###########################################
# Install
###########################################
install: requirements.txt
	pip3 install -r requirements.txt

###########################################
# Runners
###########################################
run: install
	python3 src/main.py


###########################################
# Cleanup
###########################################
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm
