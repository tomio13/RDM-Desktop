# RDM desktop
This project aims to develop a research data management (RDM) toolkit for
desktop computers following the KISS principles.

## what is KISS?
[Keep is simple and stupid](https://en.wikipedia.org/wiki/KISS\_principle), a very well working fundamental principle originating
in software tools of Unix operating systems.

Spelling it out in a more detailed way: write small programs which do a single
job, but do that right, being light weight as much as possible and also fast.
If any of the elements break, the majority may still function well, and will
not go down due to a single component.

# Problem description
## Motivation
Research data management is motivated by the fact that sofar a majority of
experiments are not documented well enuogh to be reliably reproduced. And
this lack of documention and data quality affects not only published papers,
but also local laboratory journals. As the major part of the wester research
society relies on PhD students stepping into the footprints of previous
students of the same lab, a significant amount of time can be saved if
experiment become reproducible between generations just based on their
description and results.

An actual, popular and enhanced version of this concept is to refer to the
[FAIR data principles](https://force11.org/info/the-fair-data-principles/) in science.

## Common solutions
Many companies develop and advertise electronic laboratory notebooks (ELNs) and
laboratory information management systems (LIMS) to address exactly this problem.
These solutions span from open source software to prescription models up to like
50 USD/user/month fees.

The most common part of these solutions to provide a database which collect all
information allowing for searches through the records. Data can be entered either
directly or as attachments. Metadata is also just data, usually provided in the
direct set.

Technically these solutions are completely generic. One can make a database of
anything. A free text, a bunch of numbers, it just does not matter. Many use
SQL, others document data bases, or just files on a file system with a powerful
indexer, like [Elasticsearch](https://github.com/elastic/elasticsearch).

## clients and interfaces
Most RDM solutions out there, such as:
  * [Find Molecule](https://findmolecule.com/)
  * [Logilab ELN](https://www.agaramtech.com/)
  * [labguru](https://www.labguru.com/eln)
  * [RSpace](https://www.researchspace.com/)
  * [Labii](https://www.labii.com/)
  * [SciNote](https://www.scinote.net/premium/)
  * [elabFTW](https://www.elabftw.net/)
  * [Chemotion](https://www.chemotion-repository.net/welcome)
  * etc.

provide a nice looking, very dynamic graphical / general user interface (GUI) and
an application programming interface (API), meaning a complex and often rather large
javascript code running inside the browser.

## where are the issues?
### Issue 1: javascript / browser
This is the future! And still, browsers are not really a high performance compiler
or interpreter systems meant for running code on your machine, but primarily a
rendering engine to present you complex and interactive documents across the web.
While there is a strong trend to make them a default language interpreter, for
a long time running javascript, recently pushing towards webassembly, they are
anything but optimal on any platforms.
Just looking at how much resoutces a common browser takes with a few (2-5) tabs
open may convince you that these tools require quite some power. And especially
to maintain security about what code is run and what data of the user can be
harvested by specific websites require quite some computation power.
Please do not misunderstand: they are excellent tools, but more specific clients
may prove to be better.

### Issue 2: server load
Many of the solutions are based on the cloud, that is server clusters running
everything needed.

An interesting trend is to add external software, contained applications (e.g.
in Docker containers) to process the data, and store the results directly in
the database. A very powerful approach especially for huge data sets, where
downloading and uploading the data takes much time and not every workstation
can even handle such large amounts.

This however also has some issues:
  * every data is on the cloud, which may belong to some company
  * not every institute can afford having a large cluster
  * all processing happens on the server side

### Issue 3: templates
Most of the available solutions are databases, which can take literally anything.
However, to achieve anything close to FAIR, we need templates, and we need them
such that they are common within institutes and then align to international
standards, such as [NeXuS](https://manual.nexusformat.org/), or requirements of
large data repositories, like [NOMAD](https://nomad-lab.eu/).

Thus, people have to write and share templates.

### Issue 4: publishing
In order to publish data, the content of the database has to be extracted and
packaged togeher is such manner that the database of the archive can handle it,
or it can be used as a self-consistent / self-contained archive file, extracted
into a folder tree.

This means specific plugins and filter programs doing this job. The output
formats are not well defined, can spread from MS EXCEL tables to simple text,
or what would be worse, any binary proprietary formats.

# Project idea
So, how about the following?

First, let us distribute the load. Have tools on the client side which
help managing storage and content.

Second, we can achieve a local copy of all data in a structured manner,
uploaded / synchronized to the ELN or data repository server.

## folder tree
Research data management starts at the file system level ([see for example
here](https://datamanagement.hms.harvard.edu/collect/directory-structure) or
[here](https://dmeg.cessda.eu/Data-Management-Expert-Guide/2.-Organise-Document/File-naming-and-folder-structure)).
If data is stored in a well defined folder tree and using some, also well
defined common file names and types, we already have a half document database.

Thus, a simple tool that ensures folder trees are generated according to
templates also enables maintaining a uniform structure across institutes.

## common content
Recording experiments, project ideas, summaries, etc. is a common task in
scientific work. Many turn for such cases to tools like MS WORD or MS EXCEL
which are not really target specific, and still produce proprieary data.

Much of the related data can be easily stored in text documents employing
some kind of markdown language.

Especially for experiments, the life of a user can be much improved if
we collect templates, and provide a simple interface to fill out a table
or other GUI widget, which then takes care of storing the data in a both
human and machine readable way.

## templates
Templates are made to simplify data collection, and also to ensure uniformity.
We can use them to:
  * define what fields can exist, unify field names
  * ensure values for mandatory fields
  * provide a way to translate the collected data to other standards

## server side
If our data is collected on the client in a well structured way, we should
write interfaces to upload this data to the server.

What server is utilized is flexible:
  * backup to USB drives
  * cloud based backup solution (e.g. rsync)
  * Own Cloud, Next Cloud, Drop Box synchronization
  * an ELN with API

Such synching take the folders necessary for the specific type of storage.
Multiple storage tools are available, e.g. ELN and backup simultaneously.

## archiving
is not more complicated than providing a backup of a part of the whole set.

## distributing the load
Because the data is stored locally, and only parts are uploaded, we can
provide relative links to archives or backups for large data sets.

# Software development
## Targeted platforms
in an ideal case, the tools should work on the three main operating systems:
  * Windows
  * Linux
  * Mac OS

It shall be a challenge, but doable.

## Language
Well, a challenge, because good code that is small and quite fast is best
written in C/C++.

However, the conceptual ideas can be first demonstrated e.g. in python to see
how all can work together.

Thus, the project has both languages at hand:
  * C/C++
  * python

An important limiting factor in institutes: many experimental system still
have old Windows installs, probably down to Windows XP (let us stop there). Thus,
the programs should be tested down to that line.

Python does not support anything below win 10 for a while, python [3.7 was the last
working on Win 7](https://www.python.org/downloads/windows/), but not able to run
on Windows XP.

## Dependencies
While it is extremely popular to use all libraries available to get functions
performed !(https://regmedia.co.uk/2008/07/02/fig3.gif) independent of the
library size, it is critical for a good code to use only as much as needed.
To write a simple import or export function, do not load a library except
if: 1.) provides an important functionality; 2.) it provides it in a minimal
manner. Thus, for reading a CSV do not pull in python pandas, except if you
are loading a 100 MB file, where it may provide a speed advantage.

### JSON
JSON is a standard way of sending and receiving data between javascript and server
APIs. Thus, we will need it to talk to ELNs or archiving solutions which do not
provide their own synchronization tools.

It is possible to handle JSON manually, but it is prone to throw errors with
users who do not have enough experience. And for those who have the experience
it still can be somewhat tedious.

### YAML
Again a structured text, but way more human readable. It may have a higher load
on the computer side of things, but saves much on the user experience.
Using standard library may be of help translating the structure to and from files.

#### configuration files
As a starting idea:
User readable configuration would be written in YAML. It can be still stored as
JSON, to be uploaded and distributed between installations using a server.

Furthermore, YAML / JSON can describe the GUI interfaces for various
experiments, forms, folder trees, etc.

### GUI?
One the one hand the KISS principle is often related to command line tools, which
are powerful and light weight. However, in this project user input is a very
critical part. Thus, we need graphical user interface elements to collect the
input, and present structured output.
Still, a program can be at least relatively small. It is to be expected that
programs change from a 20 kB command line tool to a 13 MB mini GUI, but it is
still way better than my browser will request to pop up a simple javascript
form.

### FLTK
For a start, it is a useful, fast and light weight C/C++ library to build
GUI interfaces. Especially, it is easy to get I/O widgets to communicate between
the user and the software.

### Tcl/Tk, Tkinter
Are a default install on Windows, so we can rely on them trying out concepts in
python.

### Gtk 3 or QT 6
If we run into very complex problems, it may be necessary to use these, but it
would be best to avoid them. The result has quite large depencencies, which
contradicts the KISS concept in our case.
So, just to put it plain: **NO!**

## Coding standard
In Python it is to be expected to keep the pylint happy. Though it is often
a hassle, it will be a coding standard one can follow.
**Except** allow using counters as single syllabi variables, when it is clear
and simple. Like i, j, k, l for indexing, N for length of an array on short term.

In C, clear tabulation of code blocks and a clear comment before every function
clarifying what the function does, its input and output are a must. Much like
[a nice code in PHP](https://www.tutorialspoint.com/php/php_coding_standard.htm).


## first steps
### folder generator
a small script that picks a string, e.g. project name, and create a bunch of
folders underneath according to a simple text configuration file.

### YAML to GUI
  * Define a YAML variable set to describe GUI elements
  * a GUI that can display them
  * export the input information to a YAML with keys from the GUI fields

