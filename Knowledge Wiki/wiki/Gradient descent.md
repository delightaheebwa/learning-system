# Gradient descent

Gradient descent is a first-order optimization method that updates parameters by moving in the direction of steepest decrease predicted by the local linear model.

For a smooth scalar function \(f: \mathbb{R}^n \to \mathbb{R}\), the first-order Taylor approximation around \(x\) is

- \(f(x + \delta) \approx f(x) + \nabla f(x)^\top \delta\)

If you ask for the direction \(\delta\) that gives the largest decrease among small steps of fixed size, the answer points opposite the gradient:

- \(\delta \propto -\nabla f(x)\)

So the key idea is:

- the gradient points uphill
- the negative gradient points downhill fastest in the local linear approximation

## Why it matters

- It uses only first-order information.
- It ignores curvature, so it is cheaper than Newton-style methods.
- It is the simplest default method for many smooth optimization problems.

## Related pages

- [[Multivariate Taylor series]]
- [[Hessian matrix]]
- [[Local linearity]]
- [[Directional derivative]]
