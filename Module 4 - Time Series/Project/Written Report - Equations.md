# Problem 1

## Exercise 1

Autocovariance function of an MA(1) process:

$X_t = Wt + \theta W_{t-1}$

Additional considerations:

$Cov(W_t, W_t) = Var(W_t) = \sigma^2$

$Cov(W_t, W_{t-s}) = 0$

$Cov(AW_t, AW_t) = A^2 Var(W_t)$

---

$|t -s | = 0$

$Cov(X_t, X_t) = Cov(W_t, W_t) + \theta Cov(W_t, W_{t-1}) + \theta Cov(W_{t-1}, W_t) + \theta^2 Cov(W_{t-1}, W_{t-1})$

$Cov(X_t, X_t) = \sigma^2 + \theta^2 \sigma^2 = \sigma^2 (1 + \theta^2)$

$\gamma(0) = \sigma^2 (1 + \theta^2)$

---

$|t - s|= 1$

$Cov(X_t, X_{t-1}) = Cov(W_t, W_{t-1}) + \theta Cov(W_t, W_{t-2}) + \theta Cov(W_{t-1}, W_{t-1}) + \theta^2 Cov(W_{t-1}, W_{t-2})$

$Cov(X_t, X_{t-1}) = \theta \sigma^2$

$\gamma(1) = \theta \sigma^2$

---

$|t -s| > 1$

$\gamma(t) = 0$

<br>
<br>

## Exercise 2

Consider the AR(1) model,

$$
X_t = \phi X_{t-1} + W_t
$$

where $\{ W_t\}  \sim W\sim \mathcal{N}(0,\sigma ^2)$. Suppose $|\phi | < 1$. Find the autocovariance function of $\{ X_t\}$. You may use, without proving, the fact that $\{ X_ t\}$ is stationary if $|\phi | < 1$. Include all important steps of your computations in your report.

$\gamma(0) = Cov(X_t, X_t)$

$\qquad = Var(X_t)$

$\gamma(1) = Cov(X_t, X_{t-1})$

$\qquad = Cov(\phi X_{t-1} + W_t, X_{t-1})$

$\qquad = Cov(\phi X_{t-1}, X_{t-1}) + Cov(W_t, X_{t-1})$

$\qquad = \phi Cov(X_{t-1}, X_{t-1})$

$\qquad = \phi \gamma(0)$

$\gamma(2) = Cov(X_t, X_{t-2})$

$\qquad = Cov(\phi X_{t-1} + W_t, X_{t-2})$

$\qquad = Cov(\phi (\phi X_{t-2} + W_t) + W_t, X_{t-2})$

$\qquad = Cov(\phi^2 X_{t-2} + \phi W_t + W_t, X_{t-2})$

$\qquad = \phi^2 Cov(X_{t-2}, X_{t-2})$

$\qquad = \phi^2 \gamma(0)$

Here we can see a pattern emerge. We have an initial value $\gamma(0)$ that consists of the variance of the auto-regressive process plus the variance of the white noise. Then, for each subsequent lag, we have a value that is the auto-regressive coefficient squared times the previous value. So we can write the general formula for the autocovariance function of an AR(1) process in the following way:

$\gamma(h) = \phi^h \gamma(0) \qquad \text{for h} = 1, 2, 3, ...$

Since we know that $|\phi| < 1$, we can say that the AR(1) model will exponentially decay to zero, as a fraction ($\phi$) elevated to an ever increasing exponential will eventually tend to zero.

To get $\gamma(0)$, we need to find the variance $Var(X_0)$. For this, we can use the formula for the variance based on the expectation:

$Var(X_0) = E[X_0^2] - E[X_0]^2$

Since we know that $X$ is a stationary process, its mean is assumed to be 0 (also assuming that $X_0$ = 0 and no drift exists). So we can simplify the formula to:

$Var(X_0) = E[X_0^2]$

Now we can just square the AR(1) formula and take the expectation. We can also use the fact that $X_0$ is independent of $W_t$ to remove the $E[X_0 W_t]$ term from the formula, as well as the fact that the expectation of the square of the white noise is equal to its variance:

$(X_t)^2 = (\phi X_{t-1} + W_t)^2$

$\qquad = \phi^2 X_{t-1}^2 + 2 \phi X_{t-1} W_t + W_t^2$

$E[(X_t)^2] = E[\phi^2 X_{t-1}^2 + 2 \phi X_{t-1} W_t + W_t^2]$

$\qquad = \phi^2 E[X_{t-1}^2] + 2 \phi E[X_{t-1} W_t] + E[W_t^2]$

$\qquad = \phi^2 E[X_{t-1}^2] + E[W_t^2]$

$\qquad = \phi^2 E[X_{t-1}^2] + \sigma^2$

$Var(X_t) = \phi^2 Var(X_t) + \sigma^2$

Now we just need to solve for $Var(X_t)$:

$$
Var(X_t) = \gamma(0) = \frac{\sigma^2}{1 - \phi^2}
$$

And we can finally get the full autocovariance function:

$$
\gamma(h) = \phi^h \frac{\sigma^2}{1 - \phi^2} \qquad \text{for h} = 1, 2, 3, ...
$$
