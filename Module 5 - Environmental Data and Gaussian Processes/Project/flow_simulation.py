from typing import Union, Tuple, Optional

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

# ============================================== #
# SIMULATE FLOW                                  #
# ============================================== #


def simulate_flow(
    x_t: np.ndarray,
    v_t: np.ndarray,
    timesteps: int,
    epsilon: Union[float, int] = 3
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate the movement of a particle using the velocity information of the
    Philippine Archipelago.  

    Parameters
    ----------
    x_t : np.ndarray
        The initial position of all the particles. Shape is (N, 2) where N is
        the number of particles. The positions are assumed to be indexes, internally
        they will be converted to coordinates (km) by multiplying by 3.

    v_t : np.ndarray
        The velocity information of the Philippine Archipelago. Shape is (T, X, Y, 2),
        where T is the number of time steps, X are the X-coordinates, Y are the
        Y-coordinates, and the last dimension are the velocities in the X and Y
        directions.

    timesteps : int
        The number of time steps to simulate.

    epsilon : float or int
        The time step size in hours. Default is 3 hours.

    Returns
    -------
    x_history : np.ndarray
        The history of the positions of the particles. Shape is (T, N, 2) where T
        is the number of time steps, N is the number of particles, and the last
        dimension are the X and Y coordinates.

    v_history : np.ndarray
        The history of the velocities of the particles. Shape is (T, N, 2) where T
        is the number of time steps, N is the number of particles, and the last
        dimension are the velocities in the X and Y directions. Its worth mentioning that
        the velocities are expected to be flipped in the Y axis (if seen in a plot, Y = 0 
        is in the top of the plot). Take this into account when plotting the velocities. 
    """

    num_particles = x_t.shape[0]

    # Converting the initial positions from indexes to kilometers
    x_t = x_t * 3

    # History of the positions of the particles
    x_history = []
    x_history.append(x_t)

    # History of the particle velocities
    v_history = []
    v_history.append(np.zeros((num_particles, 2)))

    for t in range(timesteps):

        # Get the surrogate X and Y positions for the particles
        # (Closest integer coordinates after converting back to indexes by dividing by 3)
        x_surrogate = np.round(x_t / 3).astype(int)

        # Get the X and Y velocities for the surrogate positions
        # (Vt is already in kilometers per hour)
        v_surrogate = v_t[t, x_surrogate[:, 1], x_surrogate[:, 0], :]

        # Update the positions of the particles
        x_t = x_t + v_surrogate * epsilon

        # Add the new positions and velocities to the history
        x_history.append(x_t)
        v_history.append(v_surrogate)

    # Convert the histories to a numpy array
    x_history = np.asarray(x_history)
    v_history = np.asarray(v_history)

    # Convert the X_history array back to indexes
    # (divide by 3 and round to nearest integer)
    x_history = np.round(x_history / 3).astype(int)

    return x_history, v_history


# ============================================== #
# PLOT PARTICLE SIMULATION                       #
# ============================================== #

def plot_particle_simulation(
    x_history: np.ndarray,
    v_history: np.ndarray,
    v_t: np.ndarray,
    land_mask: np.ndarray,
    end_timestep: int,
    custom_ax: Optional[plt.Axes] = None,
    quivers: bool = True,
):
    """
    Given the velocity and position history of a particle flow simulation, plot the
    result of a simulation after a given number of time steps. Can be used for animations
    by calling this function from within the "update" function of the FuncAnimation class.

    Parameters
    ----------
    x_history : np.ndarray
        The history of the positions of the particles. Shape is (T, N, 2) where T
        is the number of time steps, N is the number of particles, and the last
        dimension are the X and Y coordinates.

    v_history : np.ndarray
        The history of the velocities of the particles. Shape is (T, N, 2) where T
        is the number of time steps, N is the number of particles, and the last
        dimension are the velocities in the X and Y directions. Its worth mentioning that
        the velocities are expected to be flipped in the Y axis (if seen in a plot, Y = 0
        is in the top of the plot). This is why the velocities are flipped in the Y axis
        when plotting them.

    v_t : np.ndarray
        The velocity information of the Philippine Archipelago. Shape is (T, X, Y, 2),
        where T is the number of time steps, X are the X-coordinates, Y are the Y-coordinates,
        and the last dimension are the velocities in the X and Y directions.

    land_mask : np.ndarray
        A binary mask indicating the land and sea areas of the Philippines. Shape is (X, Y).

    end_timestep : int
        The time step to plot the simulation at. Should match the number of time steps used 
        in the history arrays, as well as the velocity array.
    """

    # If no custom axis is given, create a new figure
    if custom_ax is None:
        _, ax = plt.subplots()
    else:
        ax = custom_ax

    # Number of particles
    N = x_history.shape[1]

    # ==================== SPEED =================== #

    # Get the magnitude of the velocity (speed)
    v_x = v_t[:, :, :, 1]
    v_y = v_t[:, :, :, 0]
    speed = np.sqrt(v_x**2 + v_y**2)

    # The last two dimensions of the speed are flipped, so we need to transpose
    # them to get the correct shape in the map ([time, Y, X] -> [time, X, Y])
    speed = np.transpose(speed, (0, 2, 1))

    # The position and velocity histories contain 1 extra time step that can
    # be considered as t= -1. However, the speed only contains the time steps
    # from t=0 to t=T-1. We duplicate the last time step of the speed to match
    # the number of time steps in the position and velocity histories.
    speed = np.concatenate(
        (
            speed,
            speed[-1, :, :].reshape(1, speed.shape[1], speed.shape[2])
        ),
        axis=0
    )

    # Plot the speed at the given time step (inverted grey scale)
    ax.imshow(speed[end_timestep, :, :], cmap='gray_r')

    # ================ TRAJECTORIES ================ #

    # Get the X and Y coordinates of the particles
    x_coords = x_history[:(end_timestep+1), :, 1]
    y_coords = x_history[:(end_timestep+1), :, 0]

    # Plot the trajectories of the particles up to the given time step
    for _ in range(N):
        ax.plot(x_coords, y_coords, linewidth=0.1)

    # Plot the end positions of the particles as yellow dots
    ax.scatter(
        x_coords[-1], y_coords[-1],
        marker='o',
        color='orange',
        label='End position',
        s=10
    )

    # ================ END VELOCITY ================ #

    if quivers:

        # Get the end positions of the particles
        xt_last = x_history[end_timestep, :, :]
        pos_x_last = xt_last[:, 1]
        pos_y_last = xt_last[:, 0]

        # Get the end velocities of the particles
        # (Since we already converted the X_history array back to indexes, the positions
        # can be used to directly index the Vx and Vy arrays)
        v_x_end = v_history[end_timestep, :, 1]
        v_y_end = v_history[end_timestep, :, 0]

        # The Y-axis velocities are flipped, so we need to flip them back
        v_y_end = -v_y_end

        # # Get the magnitude (speed) of the end velocities
        speed = np.sqrt(v_x_end**2 + v_y_end**2)

        # # If the magnitude of the end velocity is 0, set it to 1 to avoid division by 0
        speed[speed == 0] = 1

        # Normalize the end velocities
        v_x_end = (v_x_end / speed)
        v_y_end = (v_y_end / speed)

        # Plot the direction of the velocity at the end of the simulation
        # (Divide by 3 to convert from km/h to index/h)
        ax.quiver(
            pos_x_last, pos_y_last,
            v_x_end, v_y_end,
            color='red',
            scale=20,
            width=0.004,
        )

    # ==================== LAND ==================== #

    # Create a custom color map that appears black for 1 and transparent for 0
    custom_cmap = ListedColormap([
        (0, 0, 0, 1),
        (0, 0, 0, 0)
    ])

    # The land mask is also flipped, so we need to transpose its last
    # two dimensions to get the correct shape in the map ([Y, X] -> [X, Y])
    flipped_mask = np.transpose(land_mask, (1, 0))

    # Plot the mask of the land in black
    ax.imshow(flipped_mask, cmap=custom_cmap)

    # ============= FINAL PLOT SETTINGS ============ #

    ax.set_title(f'Particle Trajectories (t = {end_timestep*3}h)')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')

    # If no custom axis is given, show the plot
    if custom_ax is None:
        plt.show()

    return
