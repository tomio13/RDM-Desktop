# Help is at: https://www.tutorialspoint.com/makefile/makefile_quick_guide.htm
# easy makefile for the commands here in:
# $? --> names of the changed dependents
# $@ --> name of the file to be created
# $@.cxx -> pick up all changed cxx files
# $< --> the name of the related file that caused the action
# $* --> the prefix shared by target and dependent files

CFLAGS="-Wall"
LDFLAGS="-fsanitize=leak" "-O2"
OUTPUT   = ../../bin

project_dir: ../lists.cxx ../path.cxx project_dir_cmd.cxx
	$(CXX) $(CFLAGS) $? $(LDFLAGS) -o $(OUTPUT)/$@
