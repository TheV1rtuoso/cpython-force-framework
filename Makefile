BASE_PYTHON=python
FORCE_PYTHON_BUILDDIR=cpython/build/
FORCE_PYTHON_MAKEFILE=cpython/build/Makefile
FORCE_PYTHON=${FORCE_PYTHON_BUILDDIR}/python.exe

OUTPUTDIR=output
TARGETS=struct_to_json
SND_ARG=$(word 2, $(MAKECMDGOALS))


build_forced_python: ${FORCE_PYTHON_MAKEFILE}
	make -C ${FORCE_PYTHON_BUILDDIR}

${FORCE_PYTHON_MAKEFILE}:
	mkdir -p ${FORCE_PYTHON_BUILDDIR}
	cd ${FORCE_PYTHON_BUILDDIR} && ../configure


struct_to_json: struct_to_json.c
	${CC} ${CFLAGS} -o struct_to_json struct_to_json.c

all: ${OUT_FILES} ${DIS_FILES} ${TARGETS}
	echo ${OUT_FILES}

run: struct_to_json build_forced_python
	${FORCE_PYTHON} ${SND_ARG} && ./struct_to_json forced_output.bin > collection_struct.json && ${BASE_PYTHON} forced-parser.py collection_struct.json

${OUTPUTDIR}:
	mkdir -p ${OUTPUTDIR}

# Define the input files
SRC_FILES := $(wildcard programs/*.py)

DIS_FILES := $(patsubst %.py,${OUTPUTDIR}/%.py.dis,$(SRC_FILES)) 
OUT_FILES := $(patsubst %.py,${OUTPUTDIR}/%.py.output,$(SRC_FILES))

${OUTPUTDIR}/programs/%.py.dis: programs/%.py| $(OUTPUTDIR)
	mkdir -p `dirname $@`
	${BASE_PYTHON} -m dis $< > $@

${OUTPUTDIR}/programs/%.py.output: programs/%.py| $(OUTPUTDIR)
	echo $@
	${FORCE_PYTHON} $< > $@


clean:
	rm ${OUT_FILES}
