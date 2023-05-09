from typing import Callable, Optional, Union, Tuple
from sklearn.model_selection import KFold
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm


# ============================================== #
# RADIAL BASIS KERNEL                            #
# ============================================== #

def radial_basis_kernel(X, l, sigma):
    """
    Radial basis kernel (RBF), also known as the squared exponential 
    kernel function. 
    """

    # Get ||zi - z2|| for each pair of points in the dataset
    # (Euclidean distance between all pairs of points in X)
    i, j = np.meshgrid(X, X)
    zi_zj = j - i

    # Compute the kernel
    K = sigma * np.exp(-(zi_zj**2) / (2*l**2))

    return K

# ============================================== #
# PREDICT CONDITIONAL MEAN AND VARIANCE          #
# ============================================== #


def predict_conditional_mean_and_var(
    x1: np.ndarray,
    x2: np.ndarray,
    y2: np.ndarray,
    kernel_args: tuple,
    kernel: Callable[..., np.ndarray] = radial_basis_kernel,
    tau: float = 0.001,
    moving_average_window_size: int = 5,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Predict the conditional mean and variance of the test data, given the train data.

    Parameters
    ----------
    x1 : np.ndarray
        Array containing the indices or "X" values of the data that we want to make 
        predictions for. During training this will consist of the X values of the
        test data.

    x2 : np.ndarray
        Array containing the indices or "X" values of the data that we want to use
        as reference for the predictions. During training this will consist of the
        X values of the train data.

    y2 : np.ndarray
        Array containing the actual measurements or "Y" values of the data that we
        want to use as reference for the predictions. During training this will 
        consist of the Y values of the train data (e.g. temperature, flow, speed, etc.).

    tau : float, optional
        Parameter indicating the variance of the noise in observations. For the
        Philippines dataset, this is set to 0.001 by default.

    moving_average_window_size : int, optional
        Size of the window to use for the moving average. Number of subsequent values
        to use for the moving average.
    """

    # Get the moving average of the training data to use as the
    # mean for the Gaussian Process
    mu_1 = np.convolve(
        x1,
        np.ones(moving_average_window_size)/moving_average_window_size,
        mode='same'
    )
    mu_2 = np.convolve(
        x2,
        np.ones(moving_average_window_size)/moving_average_window_size,
        mode='same'
    )

    # ============== X1 AND X2 INDICES ============= #

    # Get the ordered indexes for x1 and x2
    #
    # Lets say we have the following arrays:
    # - x1 = [1, 2, 3, 4, 5]
    # - x2 = [0.5, 1, 1.5, 2, 2.5]
    #
    # We merge them by concatenating them:
    #   idx  0  1  2  3  4   5   6   7   8   9
    # - x = [1, 2, 3, 4, 5, 0.5, 1, 1.5, 2, 2.5]
    #
    # We create a mask to separate the x1 and x2 values:
    # - mask = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    #
    # We sort the X array in ascending order and get the resulting indexes:
    # - sorting_indexes = [  5, 0, 6,   7, 1, 8,   9, 2, 3, 4]
    #          x values    0.5  1  1  1.5  2  2  2.5  3  4  5
    #
    # We sort the mask to check where the x1 and x2 ended up:
    # - sorted_mask = [1, 0, 1, 1, 0, 1, 1, 0, 0, 0]
    #
    # We assign new indexes to the sorted x array
    # - ind_x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    #
    # Finally, we get the new indexes of x that correspond to x1 and x2
    # (x1 has mask values of 0, x2 has mask values of 1)
    # - ind_x1 = [0, 2, 3, 5, 6]
    # - ind_x2 = [1, 4, 7, 8, 9]

    # Build an X array that groups all possible values of x1 and x2
    x = np.concatenate((x1, x2))

    # Create a mask to separate the x1 and x2 values
    mask_x1 = np.zeros(len(x1))
    mask_x2 = np.ones(len(x2))
    mask = np.concatenate((mask_x1, mask_x2))

    # We get the indexes that would sort the X array in ascending order
    sorting_indexes = np.argsort(x)

    # We sort both the X array and its mask
    x = x[sorting_indexes]
    sorted_mask = mask[sorting_indexes]

    # Assign new indexes to the sorted X array
    ind_x = np.arange(len(x))

    # Fetch the new indexes that correspond to x1 and x2
    ind_x1 = ind_x[sorted_mask == 0]
    ind_x2 = ind_x[sorted_mask == 1]

    # =========== CONDITIONAL ESTIMATION =========== #

    # Calculate the Sigma matrix from the kernel. This will be used as the
    # covariance matrix for the Gaussian Process
    sigma = kernel(x, *kernel_args)

    # Get each of the parts of the Sigma matrix:
    # - Sigma_11: Variance of the test data
    # - Sigma_12: Covariance between the test and train data
    # - Sigma_21: Covariance between the train data and the test data
    # - Sigma_22: Variance of the train data
    # (The weird indexing is to get the correct shape for the matrix, Sigma
    # is still a 2D array but the matrices inside are not in a fixed location
    # due to the k-fold splitting)
    sigma_11 = sigma[ind_x1][:, ind_x1]
    sigma_12 = sigma[ind_x1][:, ind_x2]
    sigma_21 = sigma[ind_x2][:, ind_x1]
    sigma_22 = sigma[ind_x2][:, ind_x2]

    # Compute the estimated noise in the variance of the training data
    # The resulting matrix should have the same shape as Sigma_22
    sigma_22_noise = sigma_22 + tau * np.eye(len(sigma_22))

    # Compute the conditional mean and variance of the test data,
    # given the train data
    mu_1_given_2 = mu_1 + \
        sigma_12 @ np.linalg.inv(sigma_22_noise) @ (y2 - mu_2)
    sigma_1_given_2 = sigma_11 - \
        sigma_12 @ np.linalg.inv(sigma_22_noise) @ sigma_21

    return mu_1_given_2, sigma_1_given_2, sigma_22_noise


# ============================================== #
# OPTIMIZE KERNEL PARAMS                         #
# ============================================== #


def optimize_kernel_params(
    data: np.ndarray,
    l_range: np.ndarray,
    std_range: np.ndarray,
    tau: float = 0.001,
    num_folds: int = 10,
    kernel: Callable[..., np.ndarray] = radial_basis_kernel,
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

    # =========== PARAMETER OPTIMIZATION =========== #

    # List of optimization results
    optimization_results: list[dict[str, Union[float, int]]] = []

    # Go through each parameter pair in the list
    for params in tqdm(param_pairs):

        # ================= PARAMETERS ================= #

        # Get the parameters for the kernel
        l = params[0]
        std = params[1]

        # ============== CROSS VALIDATION ============== #

        # Create the k-fold object
        kf = KFold(n_splits=num_folds, shuffle=False)

        # Total log likelihood for all the folds
        total_log_likelihood = 0

        for x_train, x_test in kf.split(data):

            # Get the training and test data for the current fold
            y_train, y_test = data[x_train], data[x_test]

            # Predict the conditional mean and variance of the test data
            mu_1_given_2, sigma_1_given_2, sigma_22_noise = predict_conditional_mean_and_var(
                x1=x_test,
                x2=x_train,
                y2=y_train,
                tau=tau,
                kernel_args=(l, std),
                kernel=kernel,
            )

            # Parameters for the log-likelihood function
            N_minus_d = len(y_train)
            k = len(y_test)

            # Compute the log-likelihood of the test data given the train data
            # for the current k-fold
            term_1 = -np.log((2 * np.pi)**((N_minus_d / k)/2) *
                             np.linalg.det(sigma_22_noise)**(1/2))
            term_2 = 0.5 * (y_test - mu_1_given_2).T @ \
                np.linalg.inv(sigma_1_given_2) @ (y_test - mu_1_given_2)

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

    # Get the row with the highest log-likelihood
    optimal_row = int(results_df["log_likelihood"].idxmax())
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
