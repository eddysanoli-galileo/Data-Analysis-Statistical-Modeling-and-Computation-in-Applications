from typing import Callable, Dict, Optional, Union, Tuple
from sklearn.model_selection import KFold
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm


# ============================================== #
# RADIAL BASIS KERNEL                            #
# ============================================== #

def radial_basis_kernel(X: np.ndarray, l: float, sigma: float) -> np.ndarray:
    """
    Radial basis kernel (RBF), also known as the squared exponential 
    kernel function. This is the most commonly used kernel function because
    of its properties.

    Parameters
    ----------
    X : np.ndarray
        Array containing the indices or "X" values of the data that we want to make
        predictions for.

    l : float
        Length scale parameter. This parameter controls the length of the "wiggles" in
        the function. In general, you wont be able to extrapolate more than "l" units
        away from the data.

    sigma : float
        Output variance. Average distance of the function away from its mean. This
        is basically just a scaling factor for the function.
    """

    # Get ||zi - z2|| for each pair of points in the dataset
    # (Euclidean distance between all pairs of points in X)
    i, j = np.meshgrid(X, X)
    zi_zj = j - i

    # Compute the kernel
    K = sigma * np.exp(-(zi_zj**2) / (2*l**2))

    return K

# ============================================== #
# RATIONAL QUADRATIC KERNEL                      #
# ============================================== #


def rational_quadratic_kernel(X: np.ndarray, l: float, sigma: float, alpha: float):
    """
    Rational quadratic kernel. This kernel is a generalization of the RBF kernel
    that allows for different length scales for different dimensions of the input.
    Good for regression or classification tasks, but it can falter for functions with
    discontinuities.

    Parameters
    ----------
    X : np.ndarray
        Array containing the indices or "X" values of the data that we want to make
        predictions for.

    l : float
        Length scale parameter. This parameter controls the length of the "wiggles" in
        the function.

    sigma : float
        Output variance. Average distance of the function away from its mean. This
        is basically just a scaling factor for the function.

    alpha : float
        Scale mixture parameter. This parameter controls the relative weighting of
        large-scale and small-scale variations of the function. If alpha is large,
        it will turn into an RBF kernel.
    """

    # Get ||zi - z2|| for each pair of points in the dataset
    # (Euclidean distance between all pairs of points in X)
    i, j = np.meshgrid(X, X)
    zi_zj = j - i

    # Compute the kernel
    K = sigma * (1 + ((zi_zj**2) / (2*alpha*l**2)))**(-alpha)

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
# GET OPTIMAL PARAMETERS                         #
# ============================================== #


def get_optimal_params_from_df(df: pd.DataFrame) -> Dict[str, np.float64]:
    """
    Given a dataframe with the results of a kernel optimization, return the optimal
    parameters for the kernel.
    """

    # Get the row with the highest log-likelihood
    optimal_row = int(df["log_likelihood"].idxmax())
    optimal_result = df.iloc[optimal_row, :]

    # Drop the "log_likelihood" column to just leave the parameters
    optimal_result = optimal_result.drop("log_likelihood")

    # Turn the result into a dictionary
    optimal_params = optimal_result.to_dict()

    return optimal_params


# ============================================== #
# OPTIMIZE KERNEL PARAMS                         #
# ============================================== #


def optimize_kernel_params(
    data: np.ndarray,
    param_ranges: Dict[str, np.ndarray],
    tau: float = 0.001,
    num_folds: int = 10,
    kernel: Callable[..., np.ndarray] = radial_basis_kernel,
) -> Tuple[Dict[str, np.float64], pd.DataFrame]:
    """
    Optimize the kernel parameters for the Gaussian Process.

    Parameters
    ----------
    data : np.ndarray
        Array containing the data to be used for the Gaussian Process.

    param_ranges : Tuple[np.ndarray, ...]
        Tuple containing the ranges for the kernel parameters used for the
        grid search.

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

    # ============ PRE PROCESSING RANGES =========== #

    # Get all the actual ranges into a tuple
    param_range_tuple = (
        value for key, value in param_ranges.items()
    )

    # Extract only the parameter names
    param_names = param_ranges.keys()

    # ================ KERNEL PARAMS =============== #

    # Create a meshgrid with the parameter ranges
    # (The *, stores all the returned values in a tuple)
    *grids, = np.meshgrid(*param_range_tuple)

    # Flatten the grids to create a list of all the possible combinations
    param_lists = []
    for grid in grids:
        param_lists.append(grid.flatten())

    # Turn the list of arrays into a single array with shape
    # (n, num_params). Each row will consist of a different combination of
    # parameters
    param_combinations = np.array(param_lists).T

    # =========== PARAMETER OPTIMIZATION =========== #

    # List of optimization results
    optimization_results: list[dict[str, Union[float, int]]] = []

    # Go through each parameter pair in the list
    for params in tqdm(param_combinations):

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
                kernel_args=tuple(params),
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

        # Add the value for each of the parameters to the dictionary
        results_dict = dict(zip(param_names, params))

        # Add the log-likelihood of the current parameter pair to the dictionary
        results_dict['log_likelihood'] = total_log_likelihood

        # Add the total log-likelihood of the current parameter set to the
        # list of results
        optimization_results.append(results_dict)

    # Convert the optimization results to a DataFrame
    results_df = pd.DataFrame(optimization_results)

    # Get the optimal parameters
    optimal_params = get_optimal_params_from_df(results_df)

    return optimal_params, results_df


# ============================================== #
# PLOT GRID SEARCH RESULTS                       #
# ============================================== #

def plot_grid_search_results(
    x_results_df: pd.DataFrame,
    y_results_df: pd.DataFrame,
    position: np.ndarray,
    params_to_plot: Optional[list[str]] = None,
    custom_title_text: Optional[str] = None,
    save_to_file: bool = False,
    filename: Optional[str] = None,
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

    custom_title_text : str, optional
        Custom text to add to the title of the plot. If not specified, the
        default title will be used: Position (X, Y).

    save_to_file : bool, optional
        Whether to save the plot to a file.

    filename : str, optional
        Name of the file to save the plot to. If not specified, a default will be
        used.
    """

    # Plot two subplots side by side, one for the X component and one for the Y
    # component. Each subplot will have a heatmap of the log likelihood for each
    # combination of "l" and "sigma"
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # =================== X AXIS =================== #

    # Get the values and names for the columns to plot
    if params_to_plot is None:
        vx_param1 = x_results_df[x_results_df.columns[0]]
        vx_param2 = x_results_df[x_results_df.columns[1]]
        vx_param1_name = x_results_df.columns[0]
        vx_param2_name = x_results_df.columns[1]
    else:
        vx_param1 = x_results_df[params_to_plot[0]]
        vx_param2 = x_results_df[params_to_plot[1]]
        vx_param1_name = params_to_plot[0]
        vx_param2_name = params_to_plot[1]

    # Plot the heatmap for the X component
    scatter_plot1 = ax1.scatter(
        vx_param1,
        vx_param2,
        c=x_results_df['log_likelihood'],
        cmap='viridis',
        s=100,
    )
    ax1.set_xlabel(vx_param1_name)
    ax1.set_ylabel(vx_param2_name)
    ax1.set_title('Log Likelihood for $V_x$')
    fig.colorbar(scatter_plot1, ax=ax1)

    # Get the optimal parameters for the X component
    optimal_params_vx = get_optimal_params_from_df(x_results_df)

    # Convert the optimal parameters (dict) into a list
    optimal_param_values_vx = list(optimal_params_vx.values())

    # Plot the optimal parameters on the heatmap as a red dot
    ax1.scatter(
        optimal_param_values_vx[0],
        optimal_param_values_vx[1],
        c='red',
        s=100,
        marker='x',
    )

    # =================== Y AXIS =================== #

    # Get the values and names for the columns to plot
    if params_to_plot is None:
        vy_param1 = y_results_df[y_results_df.columns[0]]
        vy_param2 = y_results_df[y_results_df.columns[1]]
        vy_param1_name = y_results_df.columns[0]
        vy_param2_name = y_results_df.columns[1]
    else:
        vy_param1 = y_results_df[params_to_plot[0]]
        vy_param2 = y_results_df[params_to_plot[1]]
        vy_param1_name = params_to_plot[0]
        vy_param2_name = params_to_plot[1]

    # Plot the heatmap for the Y component
    scatter_plot2 = ax2.scatter(
        vy_param1,
        vy_param2,
        c=y_results_df['log_likelihood'],
        cmap='viridis',
        s=100,
    )
    ax2.set_xlabel(vy_param1_name)
    ax2.set_ylabel(vy_param2_name)
    ax2.set_title('Log Likelihood for $V_y$')
    fig.colorbar(scatter_plot2, ax=ax2)

    # Get the optimal parameters for the Y component
    optimal_params_vy = get_optimal_params_from_df(y_results_df)

    # Convert the optimal parameters (dict) into a list
    optimal_param_values_vy = list(optimal_params_vy.values())

    # Plot the optimal parameters on the heatmap as a red dot
    ax2.scatter(
        optimal_param_values_vy[0],
        optimal_param_values_vy[1],
        c='red',
        s=100,
        marker='x',
    )

    # Set the title of the figure
    if custom_title_text is None:
        fig.suptitle(f'Position: ({position[0]}, {position[1]})')
    else:
        fig.suptitle(custom_title_text)

    # Save the figure to a file
    if save_to_file:
        if filename is None:
            filename = f'grid_search_results_pos_{position[0]}_{position[1]}.png'

        plt.savefig(filename)

    plt.show()
