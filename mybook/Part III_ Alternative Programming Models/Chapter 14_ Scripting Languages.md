# Chapter 14: Scripting Languages

## **14**

## **Scripting Languages**

**Traditional programming languages are intended** primarily for the con-
struction of self-contained applications: programs that accept some sort of input,
manipulate it in some well-understood way, and generate appropriate output. But
most actual* uses* of computers require the coordination of multiple programs. A
large institutional payroll system, for example, must process time-reporting data
from card readers, scanned paper forms, and manual (keyboard) entry; execute
thousands of database queries; enforce hundreds of legal and institutional rules;
create an extensive “paper trail” for record-keeping, auditing, and tax preparation
purposes; print paychecks; and communicate with servers around the world for
on-line direct deposit, tax withholding, retirement accumulation, medical insur-
ance, and so on. These tasks are likely to involve dozens or hundreds of separately
executable programs. Coordination among these programs is certain to require
tests and conditionals, loops, variables and types, subroutines and abstractions—
the same sorts of logical tools that a conventional language provides* inside* an
application.
On a much smaller scale, a graphic artist or photojournalist may routinely
download pictures from a digital camera; convert them to a favorite format; rotate
the pictures that were shot in vertical orientation; down-sample them to create
browsable thumbnail versions; index them by date, subject, and color histogram;
back them up to a remote archive; and then reinitialize the camera’s memory.
Performing these steps by hand is likely to be both tedious and error-prone. In
a similar vein, the creation of a dynamic web page may require authentication
and authorization, database lookup, image manipulation, remote communica-
tion, and the reading and writing of HTML text. All these scenarios suggest a
need for programs that coordinate other programs.
It is of course possible to write coordination code in Java, C, or some other
conventional language, but it isn’t always easy. Conventional languages tend to
stress efﬁciency, maintainability, portability, and the static detection of errors.
Their type systems tend to be built around such hardware-level concepts as ﬁxed-
size integers, ﬂoating-point numbers, characters, and arrays. By contrast* scripting*
*languages* tend to stress ﬂexibility, rapid development, local customization, and

**699**

While it is difﬁcult to deﬁne scripting languages precisely, there are several char-
acteristics that they tend to have in common:

*Both batch and interactive use.* A few scripting languages (notably Perl) have a
compiler that insists on reading the entire source program before it produces
any output. Most other languages, however, are willing to compile or inter-
pret their input line by line. Rexx, Python, Tcl, Guile, and (with short helper
scripts) Ruby and Lua will all accept commands from the keyboard.

in Perl, Python, or Ruby it is simply

```
print "Hello, world!\n"
■
```

*Lack of declarations; simple scoping rules.* Most scripting languages dispense with
declarations, and provide simple rules to govern the scope of names. In some
languages (e.g., Perl) everything is global by default; optional declarations can
be used to limit a variable to a nested scope. In other languages (e.g., PHP
and Tcl), everything is local by default; globals must be explicitly imported.
Python adopts the interesting rule that any variable that is assigned a value is
local to the block in which the assignment appears. Special syntax is required
to assign to a variable in a surrounding scope.

**DESIGN & IMPLEMENTATION**

14.1 Compiling interpreted languages
Several times in this chapter we will make reference to “the compiler” for a
scripting language. As we saw in Examples 1.9 and 1.10, interpreters almost
never work with source code; a front-end translator ﬁrst replaces that source
with some sort of intermediate form. For most implementations of most of
the languages described in this chapter, the front end is sufﬁciently complex
to deserve the name “compiler.” Intermediate forms are typically internal data
structures (e.g., a syntax tree) or “byte-code” representations reminiscent of
those of Java.

A whole loop on one line
semicolons. The following, for example, is equivalent to the loop in the previous
example:

```
for fig in *.eps; do ps2pdf $fig; done
■
```

**1**
Postscript is a programming language developed at Adobe Systems, Inc. for the description of
images and documents (we consider it again in Sidebar 15.1). Encapsulated Postscript (EPS) is
a restricted form of Postscript intended for ﬁgures that are to be embedded in other documents.
Portable Document Format (PDF, also by Adobe) is a self-contained ﬁle format that combines a
subset of Postscript with font embedding and compression mechanisms. It is strictly less powerful
than Postscript from a computational perspective, but much more portable, and faster and easier
to render.

Subshells
evaluation. If the opening parenthesis is preceded by a dollar sign, the output of
the nested command list is expanded into the surrounding context:

```
6
Strictly speaking, ] and } don’t require a protective backslash unless there is a preceding un-
matched (and unprotected) [ or {, respectively.
```

### using composite objects as keys in a hash. Tuples in Python work particularly

### well:

