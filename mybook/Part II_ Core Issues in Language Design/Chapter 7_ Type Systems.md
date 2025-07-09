# Chapter 7: Type Systems

## **7**

## **Type Systems**

**Most programming languages include a notion of**** type** for expressions
and/or objects.1 Types serve several important purposes:

**1.** Types provide implicit context for many operations, so that the programmer
does not have to specify that context explicitly. In C, for instance, the expres-
**EXAMPLE** 7.1

```
Operations that leverage
type information
sion a + b will use integer addition if a and b are of integer (int) type; it
will use ﬂoating-point addition if a and b are of ﬂoating-point (double or
float) type. Similarly, the operation new p in Pascal, where p is a pointer,
will allocate a block of storage from the heap that is the right size to hold an
object of the type pointed to by p; the programmer does not have to specify
(or even know) this size. In C++, Java, and C#, the operation new my_type()
not only allocates (and returns a pointer to) a block of storage sized for an ob-
ject of type my_type; it also automatically calls any user-deﬁned initialization
(constructor) function that has been associated with that type.
■
2. Types limit the set of operations that may be performed in a semantically valid
EXAMPLE 7.2
```

Errors captured by type
information
program. They prevent the programmer from adding a character and a record,
for example, or from taking the arctangent of a set, or passing a ﬁle as a param-
eter to a subroutine that expects an integer. While no type system can promise
to catch every nonsensical operation that a programmer might put into a pro-
gram by mistake, good type systems catch enough mistakes to be highly valu-
able in practice.
■
**3.** If types are speciﬁed explicitly in the source program (as they are in many
but not all languages), they can often make the program easier to read and
understand. In effect, they serve as stylized documentation, whose correctness
is checked by the compiler. (On the ﬂip side, the need for this documentation
can sometimes make the program harder to write.)
**4.** If types are known at compile time (either because the programmer speciﬁes
them explicitly or because the compiler is able to infer them), they can be used

**1**
Recall that unless otherwise noted we are using the term “object” informally to refer to anything
that might have a name. Object-oriented languages, which we will study in Chapter 10, assign a
narrower, more formal, meaning to the term.

**297**

```
As another example of orthogonality, consider the common need to “erase” the
value of a variable—to indicate that it does not hold a valid value of its type. For
pointer types, we can often use the value null. For enumerations, we can add an
extra “none of the above” alternative to the set of possible values. But these two
techniques are very different, and they don’t generalize to types that already make
use of all available bit patterns in the underlying implementation.
To address the need for “none of the above” in a more orthogonal way, many
EXAMPLE 7.6
```

```
Option types in OCaml
functional languages—and some imperative languages as well—provide a special
type constructor, often called Option or Maybe. In OCaml, we can write
```

```
let divide n d : float option =
(* n and d are parameters *)
match d with
(* "float option" is the return type *)
| 0. -> None
| _
-> Some (n /. d);;
(* underscore means "anything else" *)
```

```
let show v : string =
match v with
| None
-> "??"
| Some x -> string_of_float x;;
```

```
Here function divide returns None if asked to divide by zero; otherwise it returns
Some x, where x is the desired quotient. Function show returns either "??" or
the string representation of x, depending on whether parameter v is None or
Some x.
■
```

In Pascal and most of its descendants, however, the difference between an enu-
meration and a set of integer constants is much more signiﬁcant: the enumer-
ation is a full-ﬂedged type, incompatible with integers. Using an integer or an
enumeration value in a context expecting the other will result in a type clash er-
ror at compile time.
Values of an enumeration type are typically represented by small integers, usu-
**EXAMPLE** 7.11

```
Converting to and from
enumeration type
ally a consecutive range of small integers starting at zero. In many languages these
ordinal values are semantically signiﬁcant, because built-in functions can be used
to convert an enumeration value to its ordinal value, and sometimes vice versa. In
Ada, these conversions employ the attributes pos and val: weekday‚pos(mon)
= 1 and weekday‚val(1) = mon.
■
Several languages allow the programmer to specify the ordinal values of enu-
meration types, if the default assignment is undesirable. In C, C++, and C#, one
EXAMPLE 7.12
```

Distinguished values for
enums
could write

```
enum arm_special_regs {fp = 7, sp = 13, lr = 14, pc = 15};
```

(The intuition behind these values is explained in Sections C 5.4.5 and C 9.2.2.)
In Ada this declaration would be written

```
type arm_special_regs is (fp, sp, lr, pc);
-- must be sorted
for arm_special_regs use (fp => 7, sp => 13, lr => 14, pc => 15);
■
```

