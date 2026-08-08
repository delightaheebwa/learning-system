# Jacobian determinant

The Jacobian determinant is the determinant of a Jacobian matrix.

## Meaning

For a 2D transformation, it measures how area scales near a point.

- If \(|\det J| > 1\), areas expand.
- If \(|\det J| < 1\), areas shrink.
- If \(\det J < 0\), the map also flips orientation.

## Connection to the Jacobian matrix

The Jacobian matrix tells you the best local linear approximation to a multivariable function. Taking its determinant gives the area scaling of that local linear map.

## Why it matters

This is the correction factor that appears when changing variables in multiple integrals.

## Related pages

- [[Jacobian matrix]]
- [[Local linearity]]
