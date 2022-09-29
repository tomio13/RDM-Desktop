# makefile to use for FLTK applications

CXX      = $(shell fltk-config --cxx)
DEBUG    = -g
CXXFLAGS = $(shell fltk-config --use-gl --use-images --cxxflags ) -I.
# FLTK kind of leaves freeing up widget memory to the system, thus the leak
# detector gets quite crazy about it... so, turn off the watchdog for now.
# LDFLAGS  = $(shell fltk-config --use-gl --use-images --ldflags ) "-O2" "-fsanitize=leak" "-lyaml"
LDFLAGS  = $(shell fltk-config --use-gl --use-images --ldflags ) "-O2" "-lyaml"
LDSTATIC = $(shell fltk-config --use-gl --use-images --ldstaticflags )
LINK     = $(CXX)
OUTPUT   = ../../bin


form_from_yaml: ../lists.cxx ../path.cxx ../read_yaml.cxx fltk_form_from_yaml.cxx
	$(CXX) $(CXXFLAGS) $? $(LDFLAGS) -o $(OUTPUT)/$@
