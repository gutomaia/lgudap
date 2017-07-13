GIT_HASH=${shell git rev-parse --verify HEAD | xargs -I [] git tag --points-at []}

ifeq "${GIT_HASH}" ""
GIT_HASH=${shell git rev-parse --verify HEAD | grep --regex '^.\{7\}' -o }
endif

VERSION=${GIT_HASH}

PROJECT_NAME=lgudap
PROJECT_TAG=lgudap

PYTHON_MODULES=lgudap

CELERY_LOG_LEVEL=INFO

WGET = wget -q

OK=\033[32m[OK]\033[39m
FAIL=\033[31m[FAIL]\033[39m
CHECK=@if [ $$? -eq 0 ]; then echo "${OK}"; else echo "${FAIL}" ; fi

default: python.mk
	@$(MAKE) -C . test

ifeq "true" "${shell test -f python.mk && echo true}"
include python.mk
endif

python.mk:
	@${WGET} https://raw.githubusercontent.com/gutomaia/makery/master/python.mk && \
		touch $@

clean: python_clean

purge: python_purge
	@rm python.mk

${CHECKPOINT_DIR}/setup.py: setup.py
	${VIRTUALENV} python setup.py develop && \
		touch $@


build: python_build ${CHECKPOINT_DIR}/setup.py

test: python_build ${REQUIREMENTS_TEST}
	${VIRTUALENV} nosetests

run: build
	${VIRTUALENV} lgudap nr

dist/.check:
	@mkdir -p dist && touch $@

dist: python_wheel

ci:
	${VIRTUALENV} CI=1 nosetests

pep8: ${REQUIREMENTS_TEST}
	${VIRTUALENV} pep8 --statistics -qq ${PYTHON_MODULES} | sort -rn || echo ''

tt:
	@${VIRTUALENV} pep8 --max-line-length=120 ${PYTHON_MODULES}

todo:
	@${VIRTUALENV} pep8 --first --max-line-length=120 ${PYTHON_MODULES}
	@find ${PYTHON_MODULES} -type f | xargs -I [] grep -H TODO []

search:
	find ${PYTHON_MODULES} -regex .*\.py$ | xargs -I [] egrep -H -n 'print|ipdb' [] || echo ''

report:
	coverage run --source=${PYTHON_MODULES} setup.py test

tdd:
	${VIRTUALENV} tdaemon --ignore-dirs="build,dist,${PYTHON_MODULES}.egg-info,venv" --custom-args="--with-notify --no-start-message"

.PHONY: clean run report
