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


