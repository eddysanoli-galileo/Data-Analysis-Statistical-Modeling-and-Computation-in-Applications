# Module 3 - Networks: Written Analysis, Peer Review and Discussion

Name: eddysanoli

## Problem 1

### **Part (c) (2 points) (100 word limit.)**

How does the time complexity of your solution involving matrix multiplication in part (a) compare to your friend's algorithm?

- The time complexity of "my friends" (naive) algorithm is O(n^3). The matrix method, on the other hand, consists of a transpose (O(n) according to [IEEE](https://ieeexplore.ieee.org/document/6131813)) and a matrix multiplication, which can be done in O(n^3) if done by hand. By compounding both notations, we get a time complexity of O(n^3), the same as the naive algorithm. However, time complexity only reflects the asymptotic behavior of the algorithm, so one can be faster by the other in practice. For example, thanks to many optimizations, matrix multiplication can now be computed more efficiently, taking the time complexity to a value closer to [O(n^2.3)](https://arxiv.org/abs/2210.10173).

### **Part (d) (3 points) (200 word limit.)**

Bibliographic coupling and cocitation can both be taken as an indicator that papers deal with related material. However, they can in practice give noticeably different results. Why? Which measure is more appropriate as an indicator for similarity between papers?

- The difference is subtle, but I think the main reason why they both end up with drastically different results comes down to the direction in which the relationship between citation and citee is summarized. In cocitation we are summarizing the amount of papers that share a citation in a common paper, or how many papers use the same common source (papers -> source). In bibliographic coupling, we are summarizing the number of papers that cite a common paper or how many sources do a pair of papers share (source -> papers). If we assume that two papers will be more similar if they share a common source, then bibliographic coupling is the better measure, as it will give a higher score to paper pairs that share the most amount of sources. Cocitation on the other hand would be better suited to measure the relevance of a paper, as it will give a higher score to paper pairs that are cited by the highest amount of papers, basically giving a summary on how widespread their contributions have been.

## Problem 2
