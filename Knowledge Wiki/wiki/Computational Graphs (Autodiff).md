# Computational Graphs (Autodiff)

A computational graph is a **directed acyclic graph (DAG)** where:
- **Nodes** represent values — inputs, intermediate results, and the final output
- **Edges** represent data flow — each edge carries a value forward and a gradient backward

The key pattern: **data flows forward, gradients flow backward.** The backward pass starts at the output with a seed gradient of 1.0 and walks backward through the graph, multiplying local derivatives along the way.

This is the universal data structure that powers every autodiff system — PyTorch, TensorFlow, JAX all build one under the hood.

## Source
- Lesson: [teach/lessons/0001-chain-rule-and-computational-graphs.html](/home/workspace/teach/lessons/0001-chain-rule-and-computational-graphs.html)
- Date learned: 2026-07-08

## Connections
- Prerequisites: Partial Derivatives & Gradient, Chain Rule & Backpropagation
- Leads to: Two-Pass Autodiff Algorithm, Reverse-Mode Autodiff & Backprop
