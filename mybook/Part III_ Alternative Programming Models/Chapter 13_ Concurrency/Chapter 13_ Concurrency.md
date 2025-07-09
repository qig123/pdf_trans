# Chapter 13: Concurrency

13

Concurrency

The bulk of this text has focused, implicitly, on sequential programs: pro- grams with a single active execution context. As we saw in Chapter 6, sequen- tiality is fundamental to imperative programming. It also tends to be implicit in declarative programming, partly because practical functional and logic languages usually include some imperative features, and partly because people tend to de- velop imperative implementations and mental models of declarative programs (applicative order reduction, backward chaining with backtracking), even when language semantics do not require such a model. By contrast, a program is said to be concurrent if it may have more than one active execution context—more than one “thread of control.” Concurrency has at least three important motivations:

1. To capture the logical structure of a problem. Many programs, particularly servers and graphical applications, must keep track of more than one largely independent “task” at the same time. Often the simplest and most logical way to structure such a program is to represent each task with a separate thread of control. We touched on this “multithreaded” structure when discussing coroutines (Section 9.5) and events (Section 9.6); we will return to it in Sec- tion 13.1.1. 2. To exploit parallel hardware, for speed. Long a staple of high-end servers and supercomputers, multiple processors (or multiple cores within a processor) have become ubiquitous in desktop, laptop, and mobile devices. To use these cores effectively, programs must generally be written (or rewritten) with con- currency in mind. 3. To cope with physical distribution. Applications that run across the Internet or a more local group of machines are inherently concurrent. So are many embed- ded applications: the control systems of a modern automobile, for example, may span dozens of processors spread throughout the vehicle.

In general, we use the word concurrent to characterize any system in which two or more tasks may be underway (at an unpredictable point in their execution) at the same time. Under this deﬁnition, coroutines are not concurrent, because at

623

