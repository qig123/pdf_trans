# Chapter 12: Logic Languages

## **12**

## **Logic Languages**

**Having considered functional languages in some detail,** we now turn to
logic languages. The overlap between imperative and functional concepts in pro-
gramming language design has led us to discuss the latter at numerous points
throughout the text. We have had less occasion to remark on features of logic
programming languages. Logic of course is used heavily in the design of digi-
tal circuits, and most programming languages provide a logical (Boolean) type
and operators. Logic is also heavily used in the formal study of language seman-
tics, speciﬁcally in* axiomatic* semantics.1 In the 1970s, with the work of Alain
Colmeraurer and Philippe Roussel of the University of Aix–Marseille in France
and Robert Kowalski and associates at the University of Edinburgh in Scotland,
researchers also began to employ the process of logical deduction as a general-
purpose model of computing.
We introduce the basic concepts of logic programming in Section 12.1. We
then survey the most widely used logic language, Prolog, in Section 12.2. We
consider, in turn, the concepts of resolution and uniﬁcation, support for lists and
arithmetic, and the search-based execution model. After presenting an extended
example based on the game of tic-tac-toe, we turn to the more advanced topics of
imperative control ﬂow and database manipulation.
Much as functional programming is based on the formalism of lambda calcu-
lus, Prolog and other logic languages are based on* ﬁrst-order predicate calculus*.
A brief introduction to this formalism appears in Section C 12.3 on the compan-
ion site. Where functional languages capture the full capabilities of the lambda
calculus, however (within the limits, at least, of memory and other resources),
logic languages do not capture the full power of predicate calculus. We consider
the relevant limitations as part of a general evaluation of logic programming in
Section 12.4.

**1**
Axiomatic semantics models each statement or expression in the language as a* predicate trans-*
*former*—an inference rule that takes a set of conditions known to be true initially and derives a
new set of conditions guaranteed to be true after the construct has been evaluated. The study of
formal semantics is beyond the scope of this book.

**591**

*H** ←**B*1*,** B*2*, . . . ,** B**n*

The semantics of this statement are that when the* B**i* are all true, we can deduce
that* H* is true as well. When reading aloud, we say “*H*, if* B*1,* B*2, ..., and* B**n*.” Horn
clauses can be used to capture most, but not all, logical statements. (We return to
the issue of completeness in Section C 12.3.)
■
In order to derive new statements, a logic programming system combines ex-
isting statements, canceling like terms, through a process known as* resolution*. If
**EXAMPLE** 12.2

Resolution
we know that* A* and* B* imply* C*, for example, and that* C* implies* D*, we can deduce
that* A* and* B* imply* D*:

*C** ←**A**,** B*

*D** ←**C*

*D** ←**A**,** B*

In general, terms like* A*,* B*,* C*, and* D* may consist not only of constants
(“Rochester is rainy”) but also of* predicates* applied to* atoms* or to* variables*:
rainy(Rochester), rainy(Seattle), rainy(*X*).
■
During resolution, free variables may acquire values through* uniﬁcation* with
**EXAMPLE** 12.3

Uniﬁcation
expressions in matching terms, much as variables acquire types in ML (Sec-
tion 7.2.4):

ﬂowery(*X*)* ←*rainy(*X*)

rainy(Rochester)

ﬂowery(Rochester)

In the following section we consider Prolog in more detail. We return to formal
logic, and to its relationship to Prolog, in Section C 12.3.
■

**2**
Note that the word “head” is used for two different things in Prolog: the head of a Horn clause
and the head of a list. The distinction between these is usually clear from context.


![Figure 12.1 Backtracking search...](images/page_632_vector_331.png)
*Figure 12.1 Backtracking search in Prolog. The tree of potential resolutions consists of alter- nating AND and OR levels. An AND level consists of subgoals from the right-hand side of a rule, all of which must be satisﬁed. An OR level consists of alternative database clauses whose head will unify with the subgoal above; one of these must be satisﬁed. The notation _C = _X is meant to indicate that while both C and X are uninstantiated, they have been associated with one another in such a way that if either receives a value in the future it will be shared by both.*

```
The process of returning to previous goals is known as backtracking. It strongly
resembles the control ﬂow of generators in Icon (Section C 6.5.4). Whenever a
uniﬁcation operation is “undone” in order to pursue a different path through
the search tree, variables that were given values or associated with one another
as a result of that uniﬁcation are returned to their uninstantiated or unassociated
state. In Figure 12.1, for example, the binding of X to seattle is broken when
EXAMPLE 12.16
```

```
Backtracking and
instantiation
we backtrack to the rainy(X) subgoal. The effect is similar to the breaking of
bindings between actual and formal parameters in an imperative programming
language, except that Prolog couches the bindings in terms of uniﬁcation rather
than subroutine calls.
■
Space management for backtracking search in Prolog usually follows the
single-stack implementation of iterators described in Section C 9.5.3. The inter-
preter pushes a frame onto its stack every time it begins to pursue a new subgoal
G. If G fails, the frame is popped from the stack and the interpreter begins to
backtrack. If G succeeds, control returns to the “caller” (the parent in the search
tree), but G’s frame remains on the stack. Later subgoals will be given space above
```

