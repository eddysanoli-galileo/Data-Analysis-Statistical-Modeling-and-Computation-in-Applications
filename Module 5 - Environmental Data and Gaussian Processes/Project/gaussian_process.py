from typing import Callable, Optional, Union, Tuple
from sklearn.model_selection import KFold
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

# ============================================== #
# SQUARED EXPONENTIAL KERNEL                     #
# ============================================== #


def squared_exp_kernel(X, l, sigma):
    """
    Squared exponential kernel function. 
    """

    # Get ||zi - z2|| for each pair of points in the dataset
    # (Euclidean distance between all pairs of points in X)
    m, n = np.meshgrid(X, X)
    zi_zj = (m - n)

    # Compute the kernel
    K = sigma**2 * np.exp(-zi_zj**2 / (l**2))

    return K

# ============================================== #
# OPTIMIZE KERNEL PARAMS                         #
# ============================================== #


def optimize_kernel_params(
    data: np.ndarray,
    l_range: np.ndarray,
    std_range: np.ndarray,
    tau: float = 0.001,
    num_folds: int = 10,
    kernel: Optional[Callable[..., np.ndarray]] = None,
) -> Tuple[float, float, pd.DataFrame]:
    """
    Optimize the kernel parameters for the Gaussian Process.

    Parameters
    ----------
    data : np.ndarray
        Array containing the data to be used for the Gaussian Process.

    l_range : np.ndarray
        Array with all of the values that want to be tested for the length
        scale parameter of the kernel. e.g. np.arange(0.1, 1.1, 0.1)

    std_range : np.ndarray
        Array with all of the values that want to be tested for the standard
        deviation parameter of the kernel. e.g. np.arange(0.1, 1.1, 0.1)

    tau : float, optional
        Parameter indicating the variance of the noise in observations. For the
        Philippines dataset, this is set to 0.001 by default.

    num_folds : int, optional
        Number of folds to use for the cross validation. For the Philippines dataset,
        this is set to 10 by default.

    kernel : Callable[..., np.ndarray], optional
        Kernel function to use for the Gaussian Process. If not specified, the
        squared exponential kernel will be used by default.
    """

    # ================ KERNEL PARAMS =============== #

    # Create a meshgrid with the parameter ranges
    l_grid, std_grid = np.meshgrid(l_range, std_range)

    # Flatten the grids to create a list of all the possible combinations
    l_list = l_grid.flatten()
    std_list = std_grid.flatten()

    # Stack the parameters to create a single array with shape (n, 2)
    # Each row will consist of a different combination of parameters
    param_pairs = np.stack([l_list, std_list], axis=1)

    # =================== KERNEL =================== #

    if kernel is None:
        kernel = squared_exp_kernel

    # =========== PARAMETER OPTIMIZATION =========== #

    # List of optimization results
    optimization_results: list[dict[str, Union[float, int]]] = []

    # Go through each parameter pair in the list
    for params in tqdm(param_pairs):

        # ================= PARAMETERS ================= #

        # Get the parameters for the kernel
        l = params[0]
        std = params[1]

        # Get the full range of values for X
        # (For the Philippines dataset, this is just the X axis of the data, or
        # a range from 0 to the number of timesteps)
        X = np.arange(len(data))

        # Calculate the Sigma matrix from the kernel. This will be used as the
        # covariance matrix for the Gaussian Process
        Sigma = squared_exp_kernel(X, l, std)

        # ============== CROSS VALIDATION ============== #

        # Create the k-fold object
        kf = KFold(n_splits=num_folds, shuffle=False)

        # Total log likelihood for all the folds
        total_log_likelihood = 0

        for x_train, x_test in kf.split(data):

            # Get the training and test data for the current fold
            y_train, y_test = data[x_train], data[x_test]

            # Get the moving average of the training data to use as the
            # mean for the Gaussian Process
            window_size = 5
            mu_1 = np.convolve(
                y_test,
                np.ones(window_size)/window_size,
                mode='same'
            )
            mu_2 = np.convolve(
                y_train,
                np.ones(window_size)/window_size,
                mode='same'
            )

            # Get each of the parts of the Sigma matrix:
            # - Sigma_11: Variance of the test data
            # - Sigma_12: Covariance between the test and train data
            # - Sigma_21: Covariance between the train data and the test data
            # - Sigma_22: Variance of the train data
            # (The weird indexing is to get the correct shape for the matrix, Sigma
            # is still a 2D array but the matrices inside are not in a fixed location
            # due to the k-fold splitting)
            Sigma_11 = Sigma[x_test][:, x_test]
            Sigma_12 = Sigma[x_test][:, x_train]
            Sigma_21 = Sigma[x_train][:, x_test]
            Sigma_22 = Sigma[x_train][:, x_train]

            # Compute the estimated noise in the variance of the training data
            # The resulting matrix should have the same shape as Sigma_22
            Sigma_22_noise = Sigma_22 + tau * np.eye(len(Sigma_22))

            # Compute the conditional mean and variance of the test data,
            # given the train data
            mu_1_given_2 = mu_1 + \
                Sigma_12 @ np.linalg.inv(Sigma_22_noise) @ (y_train - mu_2)
            Sigma_1_given_2 = Sigma_11 - \
                Sigma_12 @ np.linalg.inv(Sigma_22_noise) @ Sigma_21

            # Parameters for the log-likelihood function
            N_minus_d = len(y_train)
            k = len(y_test)

            # Compute the log-likelihood of the test data given the train data
            # for the current k-fold
            term_1 = -np.log((2 * np.pi)**((N_minus_d / k)/2) *
                             np.linalg.det(Sigma_22_noise)**(1/2))
            term_2 = 0.5 * (y_test - mu_1_given_2).T @ \
                np.linalg.inv(Sigma_1_given_2) @ (y_test - mu_1_given_2)

            k_fold_log_likelihood = term_1 - term_2

            # Add the log-likelihood of the current k-fold to the total
            total_log_likelihood += k_fold_log_likelihood

        # =================== RESULTS ================== #

        # Add the total log-likelihood of the current parameter pair to the
        # dictionary that documents the parameters and their likelihood
        optimization_results.append({
            'l': l,
            'standard_deviation': std,
            'log_likelihood': total_log_likelihood
        })

    # Convert the optimization results to a DataFrame
    results_df = pd.DataFrame(optimization_results)

    # Get the row with the lowest log-likelihood
    optimal_row = int(results_df["log_likelihood"].idxmin())
    optimal_result = results_df.iloc[optimal_row, :]

    # Get the optimal parameters
    optimal_l = optimal_result["l"]
    optimal_std = optimal_result["standard_deviation"]

    return optimal_l, optimal_std, results_df


# ============================================== #
# PLOT GRID SEARCH RESULTS                       #
# ============================================== #

def plot_grid_search_results(
    x_results_df: pd.DataFrame,
    y_results_df: pd.DataFrame,
    position: np.ndarray,
    custom_title_text: Optional[str] = None
):
    """
    Plot two subplots side by side, one for the X component and one for the Y
    component. Each subplot will have a heatmap of the log likelihood for each
    combination of "l" and "sigma" for the given position.

    Parameters
    ----------
    x_results_df : pd.DataFrame
        DataFrame containing the results of the grid search for the X component.
        Three columns are required: "l", "standard_deviation", and "log_likelihood".

    y_results_df : pd.DataFrame
        DataFrame containing the results of the grid search for the Y component.
        Three columns are required: "l", "standard_deviation", and "log_likelihood".

    position : np.ndarray
        Position of the point to plot the results for. This is used as the title
        of the plot.
    """

    # Plot two subplots side by side, one for the X component and one for the Y
    # component. Each subplot will have a heatmap of the log likelihood for each
    # combination of "l" and "sigma"
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Plot the heatmap for the X component
    scatter_plot1 = ax1.scatter(
        x_results_df['l'],
        x_results_df['standard_deviation'],
        c=x_results_df['log_likelihood'],
        cmap='viridis',
        s=100,
    )
    ax1.set_xlabel('l')
    ax1.set_ylabel('Standard Deviation ($\sigma$)')
    ax1.set_title('Log Likelihood for $V_x$')
    fig.colorbar(scatter_plot1, ax=ax1)

    # Plot the heatmap for the Y component
    scatter_plot2 = ax2.scatter(
        y_results_df['l'],
        y_results_df['standard_deviation'],
        c=y_results_df['log_likelihood'],
        cmap='viridis',
        s=100,
    )
    ax2.set_xlabel('l')
    ax2.set_ylabel('Standard Deviation ($\sigma$)')
    ax2.set_title('Log Likelihood for $V_y$')
    fig.colorbar(scatter_plot2, ax=ax2)

    # Set the title of the figure
    if custom_title_text is None:
        fig.suptitle(f'Position: ({position[0]}, {position[1]})')
    else:
        fig.suptitle(custom_title_text)

    plt.show()
