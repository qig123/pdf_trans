# Chapter 11: Functional Languages

## **11**

## **Functional Languages**

**Previous chapters of this text have focused** largely on imperative program-
ming languages. In the current chapter and the next we emphasize functional
and logic languages instead. While imperative languages are far more widely
used, “industrial-strength” implementations exist for both functional and logic
languages, and both models have commercially important applications.
Lisp
has traditionally been popular for the manipulation of symbolic data, particu-
larly in the ﬁeld of artiﬁcial intelligence. OCaml is heavily used in the ﬁnancial
services industry. In recent years functional languages—statically typed ones in
particular—have become increasingly popular for scientiﬁc applications as well.
Logic languages are widely used for formal speciﬁcations and theorem proving
and, less widely, for many other applications.
Of course, functional and logic languages have a great deal in common with
their imperative cousins. Naming and scoping issues arise under every model. So
do types, expressions, and the control-ﬂow concepts of selection and recursion.
All languages must be scanned, parsed, and analyzed semantically. In addition,
functional languages make heavy use of subroutines—more so even than most
von Neumann languages—and the notions of concurrency and nondeterminacy
are as common in functional and logic languages as they are in the imperative
case.
As noted in Chapter 1, the boundaries between language categories tend to be
rather fuzzy. One can write in a largely functional style in many imperative lan-
guages, and many functional languages include imperative features (assignment
and iteration). The most common logic language—Prolog—provides certain im-
perative features as well. Finally, it is easy to build a logic programming system in
most functional programming languages.
Because of the overlap between imperative and functional concepts, we have
had occasion several times in previous chapters to consider issues of particu-
lar importance to functional programming languages. Most such languages de-
pend heavily on polymorphism (the implicit parametric kind—Sections 7.1.2,
7.3, and 7.2.4). Most make heavy use of lists (Section 8.6). Several, historically,
were dynamically scoped (Sections 3.3.6 and C 3.4.2). All employ recursion (Sec-
tion 6.6) for repetitive execution, with the result that program behavior and per-

**535**

**1**
Alan Turing (1912–1954), after whom the Turing Award is named, was a British mathematician,
philosopher, and computer visionary. As intellectual leader of Britain’s cryptanalytic group dur-
ing World War II, he was instrumental in cracking the German “Enigma” code and turning the
tide of the war. He also helped lay the theoretical foundations of modern computer science, con-
ceived the general-purpose electronic computer, and pioneered the ﬁeld of Artiﬁcial Intelligence.
Persecuted as a homosexual after the war, stripped of his security clearance, and sentenced to
“treatment” with drugs, he committed suicide.

**2**
Alonzo Church (1903–1995) was a member of the mathematics faculty at Princeton University
from 1929 to 1967, and at UCLA from 1967 to 1990. While at Princeton he supervised the doc-
toral theses of, among many others, Alan Turing, Stephen Kleene, Michael Rabin, and Dana
Scott. His codiscovery, with Turing, of undecidable problems was a major breakthrough in un-
derstanding the limits of mathematics.

```
The read-eval-print loop
(+ 3 4)
```

the interpreter will print

```
7
```

If the user types

```
eval: 7 is not a procedure
```

Unlike the situation in almost all other programming languages, extra parenthe-
ses change the semantics of Lisp/Scheme programs:

```
(+ 3 4)
=⇒7
((+ 3 4))
=⇒error
```

Here the =*⇒*means “evaluates to.” This symbol is not a part of the syntax of
Scheme itself.
■
One can prevent the Scheme interpreter from evaluating a parenthesized ex-
**EXAMPLE** 11.3

Quoting
pression by* quoting* it:

```
(quote (+ 3 4))
=⇒(+ 3 4)
```

Here the result is a three-element list. More commonly, quoting is speciﬁed with
a special shorthand notation consisting of a leading single quote mark:

```
'(+ 3 4)
=⇒(+ 3 4)
■
```

Though every expression has a type in Scheme, that type is generally not de-
termined until run time. Most predeﬁned functions check dynamically to make
**EXAMPLE** 11.4

Dynamic typing
sure that their arguments are of appropriate types. The expression

