# Module 4 - Time Series: Written Analysis, Peer Review and Discussion

Name: eddysanoli

## Problem 1: The Mauna Loa CO2 Concentration

### The final model

1. (3 points) Plot the periodic signal $P_i$. (Your plot should have 1 data point for each month, so 12 in total.) Clearly state the definition the $P_i$, and make sure your plot is clearly labeled.

   Python tip: For interpolation, you may use interp1d from Scikit-learn. See Documentation on interp1d.

2. (2 points) Plot the final fit $F_n(t_i) + P_i. Your plot should clearly show the final model on top of the entire time series, while indicating the split between the training and testing data.

3. (4 points) Report the root mean squared prediction error RMSE and the mean absolute percentage error MAPE with respect to the test set for this final model. Is this an improvement over the previous model $F_n(t_i)$ without the periodic signal? (Maximum 200 words.)

4. (3 points) What is the ratio of the range of values of $F$ to the amplitude of $P_i$ and the ratio of the amplitude of $P_i$ to the range of the residual $R_i$ (from removing both the trend and the periodic signal)? Is this decomposition of the variation of the $CO_2$ concentration meaningful? (Maximum 200 words.)

----

## Problem 2: Autovariance Functions

1. (4 points) Consider the MA(1) model,

    $$
    X_ t = W_ t + \theta W_{t-1},
    $$

    where $\{ W_t\}  \sim W\sim \mathcal{N}(0,\sigma ^2)$. Find the autocovariance function of $\{ X_ t\}$. Include all important steps of your computations in your report.

2. (4 points) Consider the AR(1) model,

    $$
    X_ t = \phi X_{t-1} + W_ t,
    $$

    where $\{ W_t\}  \sim W\sim \mathcal{N}(0,\sigma ^2)$. Suppose $|\phi | < 1$. Find the autocovariance function of $\{ X_t\}$. You may use, without proving, the fact that $\{ X_ t\}$ is stationary if $|\phi | < 1$. Include all important steps of your computations in your report.

----

## Problem 3: CPI and BER Data Analysis

### Converting to Inflation Rates

1. Repeat the model fitting and evaluation procedure from the previous page for the monthly inflation rate computed from CPI.

    Your response should include:

   - (1 point) Description of how you compute the monthly inflation rate from CPI and a plot of the monthly inflation rate. (You may choose to work with log of the CPI.)
   - (2 points) Description of how the data has been detrended and a plot of the detrended data.
   - (3 points) Statement of and justification for the chosen $AR(p)$ model. Include plots and reasoning.
   - (3 points) Description of the final model; computation and plots of the 1 month-ahead forecasts for the validation data. In your plot, overlay predictions on top of the data.

2. (3 points) Which $AR(p)$ model gives the best predictions? Include a plot of the $RMSE$ against different lags $p$ for the model.

3. (3 points) Overlay your estimates of monthly inflation rates and plot them on the same graph to compare. (There should be 3 lines, one for each datasets, plus the prediction, over time from September 2013 onward.)
