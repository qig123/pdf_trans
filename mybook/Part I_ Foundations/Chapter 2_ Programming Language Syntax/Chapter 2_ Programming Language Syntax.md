# Chapter 2: Programming Language Syntax

2 Programming Language Syntax

Unlike natural languages such as English or Chinese, computer languages must be precise. Both their form (syntax) and meaning (semantics) must be spec- iﬁed without ambiguity, so that both programmers and computers can tell what a program is supposed to do. To provide the needed degree of precision, lan- guage designers and implementors use formal syntactic and semantic notation. To facilitate the discussion of language features in later chapters, we will cover this notation ﬁrst: syntax in the current chapter and semantics in Chapter 4. As a motivating example, consider the Arabic numerals with which we repre- EXAMPLE 2.1

Syntax of Arabic numerals sent numbers. These numerals are composed of digits, which we can enumerate as follows (‘ | ’ means “or”):

digit −→0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

Digits are the syntactic building blocks for numbers. In the usual notation, we say that a natural number is represented by an arbitrary-length (nonempty) string of digits, beginning with a nonzero digit:

non zero digit −→1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

natural number −→non zero digit digit *

Here the “Kleene1 star” metasymbol (*) is used to indicate zero or more repeti- tions of the symbol to its left. ■ Of course, digits are only symbols: ink blobs on paper or pixels on a screen. They carry no meaning in and of themselves. We add semantics to digits when we say that they represent the natural numbers from zero to nine, as deﬁned by mathematicians. Alternatively, we could say that they represent colors, or the days of the week in a decimal calendar. These would constitute alternative se- mantics for the same syntax. In a similar fashion, we deﬁne the semantics of natural numbers by associating a base-10, place-value interpretation with each

1 Stephen Kleene (1909–1994), a mathematician at the University of Wisconsin, was responsible for much of the early development of the theory of computation, including much of the material in Section C 2.4.

43

