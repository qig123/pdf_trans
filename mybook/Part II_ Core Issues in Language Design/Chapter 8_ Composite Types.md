# Chapter 8: Composite Types

## **8**

## **Composite Types**

**Chapter 7 introduced the notion of types** as a way to organize the many
values and objects manipulated by computer programs. It also introduced ter-
minology for both built-in and* composite* types. As we noted in Section 7.1.4,
composite types are formed by joining together one or more simpler types using
a* type constructor*. From a denotational perspective, the constructors can be mod-
eled as operations on sets, with each set representing one of the simpler types.
In the current chapter we will survey the most important type constructors:
records, arrays, strings, sets, pointers, lists, and ﬁles. In the section on records
we will also consider both variants (unions) and tuples. In the section on point-
ers, we will take a more detailed look at the value and reference models of vari-
ables introduced in Section 6.1.2, and the heap management issues introduced in
Section 3.2. The section on ﬁles (mostly on the companion site) will include a
discussion of input and output mechanisms.
## 8.1

**Records (Structures)**
```
Record types allow related data of heterogeneous types to be stored and manipu-
lated together. Originally introduced by Cobol, records also appeared in Algol 68,
which called them structures, and introduced the keyword struct. Many mod-
ern languages, including C and its descendants, employ the Algol terminology.
Fortran 90 simply calls its records “types”: they are the only form of programmer-
deﬁned type other than arrays, which have their own special syntax. Structures
in C++ are deﬁned as a special form of class (one in which members are globally
visible by default). Java has no distinguished notion of struct; its program-
mers use classes in all cases. C# and Swift use a reference model for variables of
class types, and a value model for variables of struct types. In these languages,
structs do not support inheritance. For the sake of simplicity, we will use the
term “record” in most of our discussion to refer to the relevant construct in all
these languages.
```

**351**

### Each of the record components is known as a* ﬁeld*. To refer to a given ﬁeld of a

### record, most languages use “dot” notation:

**EXAMPLE** 8.2
```
Accessing record ﬁelds
element copper;
const double AN = 6.022e23;
/* Avogadro's number */
...
copper.name[0] = 'C'; copper.name[1] = 'u';
double atoms = mass / copper.atomic_weight * AN;
```

```
In Fortran 90 one would say copper%name and copper%atomic_weight. Cobol
reverses the order of the ﬁeld and record names: name of copper and atomic_
weight of copper. In Common Lisp, one would say (element-name copper)
and (element-atomic_weight copper).
■
Most languages allow record deﬁnitions to be nested. Again in C:
EXAMPLE 8.3
```

```
Nested records
struct ore {
char name[30];
struct {
char name[2];
int atomic_number;
double atomic_weight;
_Bool metallic;
} element_yielded;
};
```

### Alternatively, one could say

```
struct ore {
char name[30];
struct element element_yielded;
};
```

```
In Fortran 90 and Common Lisp, only the second alternative is permitted:
record ﬁelds can have record types, but the declarations cannot be lexically
nested. Naming for nested records is straightforward: malachite.element_
```

```
Nested records as
references
shown at the bottom of the ﬁgure. In the following code, using the declarations
at the bottom of the ﬁgure, assignment of s1 into s2 copies only the reference, so
s2.n.j is an alias for s1.n.j:
```

```
S s1 = new S();
s1.n = new T();
// fields initialized to 0
S s2 = s1;
s2.n.j = 7;
System.out.println(s1.n.j);
// prints 7
■
```

A few languages and implementations allow the programmer to specify that a
**EXAMPLE** 8.8

```
Layout of packed types
record type (or an array, set, or ﬁle type) should be packed. In Ada, one uses a
pragma:
```

```
type element = record
...
end;
pragma Pack(element);
```

```
Variable mat1 is a two-dimensional array; mat2 is an array of one-dimensional
arrays. With the former declaration, we can access individual real numbers as
mat1(3, 4); with the latter we must say mat2(3)(4). The two-dimensional
array is arguably more elegant, but the array of arrays supports additional op-
erations: it allows us to name the rows of mat2 individually (mat2(3) is a 10-
element, single-dimensional array), and it allows us to take slices, as discussed
```

Elaborated arrays in
Fortran 90
### after elaboration, but it does not allow those bounds to change once they have

### been deﬁned:

```
real, dimension (:,:), allocatable :: mat
! mat is two-dimensional, but with unspecified bounds
...
allocate (mat (a:b, 0:m-1))
! first dimension has bounds a..b; second has bounds 0..m-1
...
deallocate (mat)
! implementation is now free to reclaim mat's space
```

```
Execution of an allocate statement can be treated like the elaboration of a dy-
namic shape array in a nested block. Execution of a deallocate statement can
```

d
a
y

W
e
d
n
e
s

d
a
y
S
a
t
u
r

s
h

F
i
r


![Figure 8.9 Contiguous array...](images/page_404_vector_279.png)
*Figure 8.9 Contiguous array allocation vs row pointers in C. The declaration on the left is a true two-dimensional array. The slashed boxes are NUL bytes; the shaded areas are holes. The declaration on the right is a ragged array of pointers to arrays of characters. The arrays of characters may be located anywhere in memory—next to each other or separated, and in any order. In both cases, we have omitted bounds in the declaration that can be deduced from the size of the initializer (aggregate). Both data structures permit individual characters to be accessed using double subscripts, but the memory layout (and corresponding address arithmetic) is quite different.*

**Address Calculations**

### For the usual contiguous layout of arrays, calculating the address of a particular

### element is somewhat complicated, but straightforward. Suppose a compiler is

**EXAMPLE** 8.25
Indexing a contiguous array
### given the following declaration for a three-dimensional array:

A : array [*L*1 . .* U*1] of array [*L*2 . .*U*2] of array [*L*3 . .* U*3] of elem type;

### Let us deﬁne constants for the sizes of the three dimensions:

*S*3
= size of elem type

*S*2
=
(*U*3* −**L*3 + 1)* ×** S*3
*S*1
=
(*U*2* −**L*2 + 1)* ×** S*2

Here the size of a row (*S*2) is the size of an individual element (*S*3) times the
### number of elements in a row (assuming row-major layout). The size of a plane

(*S*1) is the size of a row (*S*2) times the number of rows in a plane. The address of
A[i, j, k] is then
