# Chapter 10: Data Abstraction and Object Orientation

## **10**

## **Data Abstraction and Object**

## **Orientation**

```
In Chapter 3 we presented several stages in the development of data ab-
straction, with an emphasis on the scoping mechanisms that control the visibility
of names. We began with global variables, whose lifetime spans program execu-
tion. We then added local variables, whose lifetime is limited to the execution of a
single subroutine; nested scopes, which allow subroutines themselves to be local;
and static variables, whose lifetime spans execution, but whose names are visible
only within a single scope. These were followed by modules, which allow a collec-
tion of subroutines to share a set of static variables; module types, which allow the
programmer to instantiate multiple instances of a given abstraction, and classes,
which allow the programmer to deﬁne families of related abstractions.
Ordinary modules encourage a “manager” style of programming, in which a
module exports an abstract type. Module types and classes allow the module
itself to be the abstract type. The distinction becomes apparent in two ways. First,
the explicit create and destroy routines typically exported from a manager
module are replaced by creation and destruction of an instance of the module
type. Second, invocation of a routine in a particular module instance replaces
invocation of a general routine that expects a variable of the exported type as
argument. Classes build on the module-as-type approach by adding mechanisms
for inheritance, which allows new abstractions to be deﬁned as reﬁnements or
extensions to existing ones, and dynamic method binding, which allows a new
version of an abstraction to display newly reﬁned behavior, even when used in
a context that expects an earlier version. An instance of a class is known as an
object; languages and programming techniques based on classes are said to be
object-oriented.1
The stepwise evolution of data abstraction mechanisms presented in Chapter 3
is a useful way to organize ideas, but it does not completely reﬂect the historical
development of language features. In particular, it would be inaccurate to sug-
gest that object-oriented programming developed as an outgrowth of modules.
```

**1**
In previous chapters we used the term “object” informally to refer to almost anything that can
have a name. In this chapter we will use it only to refer to an instance of a class.

**471**

```
list class that uses
list_node
follows:
```

```
class list {
list_node header;
public:
// no explicit constructor required;
// implicit construction of 'header' suffices
int empty() {
return header.singleton();
}
list_node* head() {
return header.successor();
}
void append(list_node *new_node) {
header.insert_before(new_node);
}
~list() {
// destructor
if (!header.singleton())
throw new list_err("attempt to delete nonempty list");
}
};
```

To create an empty list, one could then write

```
list* my_list_ptr = new list;
```

```
Each in-line declaration or call to new would then need to provide a value:
```

```
list_node element1(0);
// in-line
list_node *e_ptr = new list_node(13);
// heap
```

As we shall see in Section 10.3.1, C++ actually allows us to declare* both* construc-
tors, and uses the usual rules of function overloading to differentiate between
them: declarations without a value will call the no-parameter constructor; decla-
rations with an integer argument will call the integer-parameter constructor.
■

```
class queue : private list {
...
int head() {
if (empty())
throw new list_err("attempt to peek at head of empty queue");
return list::head()->val;
}
```

```
Note that the head method of class list is still visible to methods of class
queue (but not to its users!) when identiﬁed with the scope resolution opera-
tor (list::).
■
```

```
Does the choice of the method to be called depend on the types of the variables x
and y, or on the classes of the objects s and p to which those variables refer?
■
The ﬁrst option (use the type of the reference) is known as static method bind-
ing. The second option (use the class of the object) is known as dynamic method
binding. Dynamic method binding is central to object-oriented programming.
Imagine, for example, that our administrative computing program has created
a list of persons who have overdue library books. The list may contain both
students and professors. If we traverse the list and print a mailing label for
each person, dynamic method binding will ensure that the correct printing rou-
tine is called for each individual. In this situation the deﬁnitions in the derived
classes are said to override the deﬁnition in the base class.
```

a

b

w
c

bar’s vtable

foo::l

foo::n
bar::s

bar::t

bar::m
code pointers

foo::k


![Figure 10.4 Implementation of...](images/page_543_vector_354.png)
*Figure 10.4 Implementation of single inheritance. As in Figure 10.3, the representation of object B begins with the address of its class’s vtable. The ﬁrst four entries in the table represent the same members as they do for foo, except that one—m—has been overridden and now contains the address of the code for a different subroutine. Additional ﬁelds of bar follow the ones inherited from foo in the representation of B; additional virtual methods follow the ones inherited from foo in the vtable of class bar.*

r1 := f
r2 :=* ∗*r1
–– vtable address
r2 :=* ∗*(r2 + (3−1) × 4)
–– assuming 4 = sizeof (address)
call* ∗*r2

```
On a typical modern machine this calling sequence is two instructions (both of
which access memory) longer than a call to a statically identiﬁed method. The
extra overhead can be avoided whenever the compiler can deduce the type of the
relevant object at compile time. The deduction is trivial for calls to methods of
object-valued variables (as opposed to references and pointers).
■
If bar is derived from foo, we place its additional ﬁelds at the end of the
EXAMPLE 10.46
```

```
Implementation of single
inheritance
“record” that represents it. We create a vtable for bar by copying the vtable for
foo, replacing the entries of any virtual methods overridden by bar, and append-
ing entries for any virtual methods introduced in bar (see Figure 10.4).
If we
have an object of class bar we can safely assign its address into a variable of type
foo*:
```

