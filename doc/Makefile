# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -aE #Always build even if no source file changed
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  = sphinx-apidoc
SOURCEDIR     = source
APIDIR 		  = source/api
BUILDDIR      = build
MODULEPATH    = ../pyfurc

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Modify the automatically generated apidoc including an introduction and
# removing the Submodules heading.
# Check out the script doc/api/mod_api_doc.py
api:
	@$(SPHINXAPIDOC) -MTf -o $(APIDIR) $(MODULEPATH)
	python $(APIDIR)/mod_api_doc.py

all:
	@make api
	@make html
