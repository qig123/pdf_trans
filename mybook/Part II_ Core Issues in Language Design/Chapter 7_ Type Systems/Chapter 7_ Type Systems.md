# Chapter 7: Type Systems

7 Type Systems

Most programming languages include a notion of type for expressions and/or objects.1 Types serve several important purposes:

1. Types provide implicit context for many operations, so that the programmer does not have to specify that context explicitly. In C, for instance, the expres- EXAMPLE 7.1

Operations that leverage type information sion a + b will use integer addition if a and b are of integer (int) type; it will use ﬂoating-point addition if a and b are of ﬂoating-point (double or float) type. Similarly, the operation new p in Pascal, where p is a pointer, will allocate a block of storage from the heap that is the right size to hold an object of the type pointed to by p; the programmer does not have to specify (or even know) this size. In C++, Java, and C#, the operation new my_type() not only allocates (and returns a pointer to) a block of storage sized for an ob- ject of type my_type; it also automatically calls any user-deﬁned initialization (constructor) function that has been associated with that type. ■ 2. Types limit the set of operations that may be performed in a semantically valid EXAMPLE 7.2

Errors captured by type information program. They prevent the programmer from adding a character and a record, for example, or from taking the arctangent of a set, or passing a ﬁle as a param- eter to a subroutine that expects an integer. While no type system can promise to catch every nonsensical operation that a programmer might put into a pro- gram by mistake, good type systems catch enough mistakes to be highly valu- able in practice. ■ 3. If types are speciﬁed explicitly in the source program (as they are in many but not all languages), they can often make the program easier to read and understand. In effect, they serve as stylized documentation, whose correctness is checked by the compiler. (On the ﬂip side, the need for this documentation can sometimes make the program harder to write.) 4. If types are known at compile time (either because the programmer speciﬁes them explicitly or because the compiler is able to infer them), they can be used

1 Recall that unless otherwise noted we are using the term “object” informally to refer to anything that might have a name. Object-oriented languages, which we will study in Chapter 10, assign a narrower, more formal, meaning to the term.

297

