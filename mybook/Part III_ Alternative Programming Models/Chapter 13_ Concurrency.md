# Chapter 13: Concurrency

## **13**

## **Concurrency**

**The bulk of this text has focused,** implicitly, on* sequential* programs: pro-
grams with a single active execution context. As we saw in Chapter 6, sequen-
tiality is fundamental to imperative programming. It also tends to be implicit in
declarative programming, partly because practical functional and logic languages
usually include some imperative features, and partly because people tend to de-
velop imperative implementations and mental models of declarative programs
(applicative order reduction, backward chaining with backtracking), even when
language semantics do not require such a model.
By contrast, a program is said to be* concurrent* if it may have more than one
active execution context—more than one “thread of control.” Concurrency has
at least three important motivations:

**1.*** To capture the logical structure of a problem.*
Many programs, particularly
servers and graphical applications, must keep track of more than one largely
independent “task” at the same time. Often the simplest and most logical way
to structure such a program is to represent each task with a separate thread
of control. We touched on this “multithreaded” structure when discussing
coroutines (Section 9.5) and events (Section 9.6); we will return to it in Sec-
tion 13.1.1.
**2.*** To exploit parallel hardware, for speed.* Long a staple of high-end servers and
supercomputers, multiple processors (or multiple cores within a processor)
have become ubiquitous in desktop, laptop, and mobile devices. To use these
cores effectively, programs must generally be written (or rewritten) with con-
currency in mind.
**3.*** To cope with physical distribution.* Applications that run across the Internet or a
more local group of machines are inherently concurrent. So are many embed-
ded applications: the control systems of a modern automobile, for example,
may span dozens of processors spread throughout the vehicle.

In general, we use the word* concurrent* to characterize any system in which two
or more tasks may be underway (at an unpredictable point in their execution) at
the same time. Under this deﬁnition, coroutines are not concurrent, because at

**623**

```
int zero_count;
public static int foo(int n) {
int rtn = n - 1;
if (rtn == 0) zero_count++;
return rtn;
}
```

Consider now what may happen when two or more instances of this code run
concurrently:

**Thread 1**
. . .
**Thread 2**
r1 := zero count
. . .
r1 := r1 + 1
r1 := zero count
zero count := r1
r1 := r1 + 1
. . .
zero count := r1
. . .

If the instructions interleave roughly as shown, both threads may load the same
value of zero count, both may increment it by one, and both may store the (only
one greater) value back into zero count. The result may be less than what we
expect.
In general, a* race condition* occurs whenever two or more threads are “racing”
toward points in the code at which they touch some common object, and the
behavior of the system depends on which thread gets there ﬁrst. In this particular
example, the store of zero count in Thread 1 is racing with the load in Thread 2.

**1**
Ideally, we might like the compiler to ﬁgure this out automatically, but the problem of indepen-
dence is undecidable in the general case.

```
A parallel loop in C#
Parallel.For(0, 3, i => {
Console.WriteLine("Thread " + i + "here");
});
```

```
The third argument to Parallel.For is a delegate, in this case a lambda ex-
pression. A similar Foreach method expects two arguments—an iterator and a
delegate.
■
In many systems it is the programmer’s responsibility to make sure that con-
current execution of the loop iterations is safe, in the sense that correctness will
never depend on the outcome of race conditions. Access to global variables, for
example, must generally be synchronized, to make sure that iterations do not
```

## ...

## ...

Thread Ma
Process Ma

Process Mj

Thread Mb

Thread Ml

### ...

### ...


![Figure 13.6 Two-level implementation...](images/page_681_vector_312.png)
*Figure 13.6 Two-level implementation of threads. A thread scheduler, implemented in a library or language run-time package, multiplexes threads on top of one or more kernel-level processes, just as the process scheduler, implemented in the operating system kernel, multiplexes processes on top of one or more physical cores.*

top of one or more physical cores. We will use the terminology of threads on top
of processes in the remainder of this section.
The typical implementation starts with coroutines (Section 9.5). Recall that
coroutines are a sequential control-ﬂow mechanism: the programmer can sus-
pend the current coroutine and resume a speciﬁc alternative by calling the
transfer operation. The argument to transfer is typically a pointer to the con-
text block of the coroutine.
To turn coroutines into threads, we proceed in a series of three steps. First, we
hide the argument to transfer by implementing a* scheduler* that chooses which
thread to run next when the current thread yields the core. Second, we imple-
ment a* preemption* mechanism that suspends the current thread automatically on
a regular basis, giving other threads a chance to run. Third, we allow the data
structures that describe our collection of threads to be shared by more than one
OS process, possibly on separate cores, so that threads can run on any of the pro-
cesses.

**Uniprocessor Scheduling**


![Figure 13.7 illustrates the...](images/page_681_vector_576.png)
*Figure 13.7 illustrates the data structures employed by a simple scheduler. At any EXAMPLE 13.21*

Cooperative
multithreading on a
uniprocessor

particular time, a thread is either* blocked* (i.e., for synchronization) or* runnable*.
A runnable thread may actually be running on some process or it may be awaiting

