# Chapter 2: Programming Language Syntax

## **2**

## **Programming Language Syntax**

**Unlike natural languages such as English or Chinese,** computer languages
must be precise. Both their form (syntax) and meaning (semantics) must be spec-
iﬁed without ambiguity, so that both programmers and computers can tell what
a program is supposed to do. To provide the needed degree of precision, lan-
guage designers and implementors use formal syntactic and semantic notation.
To facilitate the discussion of language features in later chapters, we will cover
this notation ﬁrst: syntax in the current chapter and semantics in Chapter 4.
As a motivating example, consider the Arabic numerals with which we repre-
**EXAMPLE** 2.1

Syntax of Arabic numerals
sent numbers. These numerals are composed of digits, which we can enumerate
as follows (‘** |** ’ means “or”):

```
digit −→0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

Digits are the syntactic building blocks for numbers. In the usual notation, we say
that a natural number is represented by an arbitrary-length (nonempty) string of
digits, beginning with a nonzero digit:

```
non zero digit −→1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

*natural number** −→**non zero digit digit*** ***

Here the “Kleene1 star” metasymbol (*****) is used to indicate zero or more repeti-
tions of the symbol to its left.
■
Of course, digits are only symbols: ink blobs on paper or pixels on a screen.
They carry no meaning in and of themselves. We add semantics to digits when
we say that they represent the natural numbers from zero to nine, as deﬁned by
mathematicians. Alternatively, we could say that they represent colors, or the
days of the week in a decimal calendar. These would constitute alternative se-
mantics for the same syntax. In a similar fashion, we deﬁne the semantics of
natural numbers by associating a base-10, place-value interpretation with each

**1**
Stephen Kleene (1909–1994), a mathematician at the University of Wisconsin, was responsible
for much of the early development of the theory of computation, including much of the material
in Section C 2.4.

**43**

The symbols to the left of the* −→*signs provide names for the regular expres-
sions. One of these (*number*) will serve as a token name; the others are simply

**DESIGN & IMPLEMENTATION**

```
2.1 Contextual keywords
In addition to distinguishing between keywords and identiﬁers, some lan-
guages deﬁne so-called contextual keywords, which function as keywords in
certain speciﬁc places in a program, but as identiﬁers elsewhere. In C#, for ex-
ample, the word yield can appear immediately before return or break—a
place where an identiﬁer can never appear. In this context, it is interpreted as
a keyword; anywhere else it is an identiﬁer. It is therefore perfectly acceptable
to have a local variable named yield: the compiler can distinguish it from the
keyword by where it appears in the program.
C++11 has a small handful of contextual keywords. C# 4.0 has 26. Most
were introduced in the course of revising the language to create a new stan-
dard version. Given a large user community, any short, intuitively appealing
word is likely to have been used as an identiﬁer by someone, in some existing
program. Making that word a contextual keyword in the new version of the
language, rather than a full keyword, reduces the risk that existing programs
will suddenly fail to compile.
```

**3**
Some authors use* λ* to represent the empty string. Some use a period (**.**), rather than juxtaposi-
tion, to indicate concatenation. Some use a plus sign (**+**), rather than a vertical bar, to indicate
alternation.

### 2.1.3** Derivations and Parse Trees**

### A context-free grammar shows us how to generate a syntactically valid string of

### terminals: Begin with the start symbol. Choose a production with the start sym-

### bol on the left-hand side; replace the start symbol with the right-hand side of that

### production. Now choose a nonterminal* A* in the resulting string, choose a pro-

### duction* P* with* A* on its left-hand side, and replace* A* with the right-hand side of

### *P*. Repeat this process until no nonterminals remain.

### As an example, we can use our grammar for expressions to generate the string

**EXAMPLE** 2.6
```
Derivation of slope * x +
intercept
“slope * x + intercept”:
```

*expr* =*⇒**expr op expr*

```
=⇒expr op id
```

```
=⇒expr + id
```

```
=⇒expr op expr + id
```

```
=⇒expr op id + id
```

```
=⇒expr * id + id
```

```
=⇒
id
(slope)
* id
(x)
+
id
(intercept)
```

```
3CHECK YOUR UNDERSTANDING
1.
What is the difference between syntax and semantics?
2.
What are the three basic operations that can be used to build complex regular
expressions from simpler regular expressions?
3.
What additional operation (beyond the three of regular expressions) is pro-
vided in context-free grammars?
4.
What is Backus-Naur form? When and why was it devised?
```

5.
Name a language in which indentation affects program syntax.
6.
When discussing context-free languages, what is a* derivation*? What is a* sen-*
*tential form*?
7.
What is the difference between a* right-most* derivation and a* left-most* deriva-
tion?

8.
What does it mean for a context-free grammar to be* ambiguous*?
9.
What are* associativity* and* precedence*? Why are they signiﬁcant in parse trees?

4
5

6
7
8
9
10

11
12

13

14
15

16


![Figure 2.6 Pictorial representation...](images/page_90_vector_415.png)
*Figure 2.6 Pictorial representation of a scanner for calculator tokens, in the form of a ﬁnite automaton. This ﬁgure roughly parallels the code in Figure 2.5. States are numbered for reference in Figure 2.12. Scanning for each token begins in the state marked “Start.” The ﬁnal states, in which a token is recognized, are indicated by double circles. Comments, when recognized, send the scanner back to its start state, rather than a ﬁnal state.*

### state to a ﬁnal state whose non-epsilon transitions are labeled, in order, by the

### characters of the token.

### To avoid the need to search all possible paths for one that “works,” the second

### step of a scanner generatortranslates the NFA into an equivalentDFA: an automa-

### ton that accepts the same language, but in which there are no epsilon transitions,

### and no states with more than one outgoing transition labeled by the same char-

### acter. The third step is a space optimization that generates a ﬁnal DFA with the

### minimum possible number of states.

11
12
13
14


![Figure 2.8 Construction of...](images/page_92_vector_404.png)
*Figure 2.8 Construction of an NFA equivalent to the regular expression d*( .d | d. ) d*. In the top row are the primitive automata for . and d, and the Kleene closure construction for d*. In the second and third rows we have used the concatenation and alternation constructions to build .d, d., and ( .d | d. ) . The fourth row uses concatenation again to complete the NFA. We have labeled the states in the ﬁnal automaton for reference in subsequent ﬁgures.*

ones without any ambiguity about where to create the connections, and without
creating any unexpected paths.
■
To make these constructions concrete, we consider a small but nontrivial
**EXAMPLE** 2.13

```
NFA for d*( .d | d. ) d*
example—the decimal strings of Example 2.3. These consist of a string of decimal
digits containing a single decimal point. With only one digit, the point can come
at the beginning or the end: ( .d | d. ), where for brevity we use d to represent
any decimal digit. Arbitrary numbers of digits can then be added at the beginning
or the end: d*( .d | d. ) d*. Starting with this regular expression and using the
constructions of Figure 2.7, we illustrate the construction of an equivalent NFA
in Figure 2.8.
■
```

id(A)

;

;

id(C)
,

id(A) , id(B) , id(C)

id(A) , id(B) , id(C) ;

id(A) , id(B) , id(C)

id(A) , id(B) , 

id(A) , id(B)

id(A) ,

id(A)

*id_list_tail*

*id_list_tail*

*id_list_tail*

;

id(C)

id(B)

,

,

*id_list_tail*

*id_list_tail*

*id_list_tail*

id

, id

;

*id_list*
*id_list_tail*

*id_list_tail*

*id_list_tail*

*id_list_tail*


![Figure 2.14 Top-down (left)...](images/page_104_vector_502.png)
*Figure 2.14 Top-down (left) and bottom-up parsing (right) of the input string A, B, C;. Grammar appears at lower left.*

```
to peek at the upcoming token (a comma), which allows it to choose between the
two possible expansions for id list tail. It then matches the comma and the id
and moves down into the next id list tail. In a similar, recursive fashion, the top-
down parser works down the tree, left-to-right, predicting and expanding nodes
and tracing out a left-most derivation of the fringe of the tree.
```

