# Written Report: Environmental Data and Gaussian Processes

## Part I - Ocean Flow

### Problem 2 (10 bonus points)

Rubric:

- (5 points): A map with the two points with correlations marked.
- (3 points): Provides an explanation of how the correlation was computed.
- (2 points): Provides a convincing commentary on why the two marked locations could be correlated.

NOT SOLVED FOR BEING OPTIONAL OR BONUS

### Problem 3.a (10 points)

#### Rubric

- (3 points): Provides an explanation of the simulation algorithm, with equations for the evolution of the particle trajectory.
- (2 points): Provides a plot of the initial state of the simulation.
- (3 points): Provides two plots of intermediate states of the simulation.
- (2 points): Provides a plot of the final state of the simulation.

#### Solution

1. Explanation of the simulation algorithm.

   - The simulation algorithm is very simple. It can be described as the implementation of a particle moving in uniform rectilinear motion across both the x and y axes:

        $$
        X_x(t) = X_{xo} + V_x t \\
        X_y(t) = X_{yo} + V_y t
        $$

        When implemented in software, each step in the particle's movement is calculated sequentially, meaning that the values of the previous step are used to calculate the next state of the particle.

        We start with our initial state, the position of the particle at time $t=0$: $(X_{xo}, X_{yo})$ and the velocity of the particle that corresponds to its current position: $(V_x, V_y)$. Since we are analyzing flow, the velocity applied is the velocity of the vector field at the current position of the particle. The velocity of the particle is constant for a given region, so we can think of this as a pseudo-uniform rectilinear motion.

        The next step is to calculate the future position of the particle after moving for a certain amount of time $t$. Since the velocity is only given at discrete points, we approximate current position of the particle to its closest velocity point. This is done by rounding the current position of the particle to the nearest integer on both axis. Once we have the velocity, we need $t$, which in our case simply consists of the time passed between the current step and previous step. The velocity measurements in the data set are take every 3 hours, so $t=3$ (since velocity is given in km/h and the position is in km).

        For a sample data point $(1,2)$ that always travels at a velocity of $V = (1, 1)$, the movement of the particle would look like this for the first three steps:

        | Time | Position | Velocity | Time Elapsed | New Position |
        | ---- | -------- | -------- | ------------ | ------------ |
        | 0    | ---      | ---      | 3            | (1, 2)       |
        | 3    | (1, 2)   | (1, 1)   | 3            | (4, 5)       |
        | 6    | (4, 5)   | (1, 1)   | 3            | (7, 8)       |

        $$
        X = (1, 2) \\
        V = (1, 1) \\
        $$
        $$
        X_x(3) = X_{xo} + V_x t = 1 + 1 \times 3 = 4 \\
        X_y(3) = X_{yo} + V_y t = 2 + 1 \times 3 = 5 \\
        X(3) = (4, 5)
        $$
        $$
        X_x(6) = X_{xo} + V_x t = 4 + 1 \times 3 = 7 \\
        X_y(6) = X_{yo} + V_y t = 5 + 1 \times 3 = 8 \\
        X(6) = (7, 8)
        $$

        At the end, by plotting the position history of the particle, we can see its trajectory. The trajectory would be a straight line for a regular uniform rectilinear motion, but since the velocity changes, the trajectory will consist of a series of straight lines. This could be smoothed out by introducing acceleration into the equation, but unfortunately, acceleration estimation would require things like flow density and mass, which are not given in the data set.

2. Plot of the initial state of the simulation.

    ![Initial Step](Images/flow_simulation_t0.png)

3. Two plots of intermediate states of the simulation.

    ![Intermediate Step 1](Images/flow_simulation_t25.png)

    ![Intermediate Step 2](Images/flow_simulation_t75.png)

4. Plot of the final state of the simulation.

    ![Final Step](Images/flow_simulation_t_last.png)

### Problem 3.b (10 points)

#### Rubric

- (3 points): Provides plots showing the state of the simulation at the times: $T=48$hrs, $72$hrs, $120$hrs. (Three plots required.)
- (3 points): Two or more additional choices of the variances were tried, and three plots of the state of the simulation at the above three times are provided. (Six additional plots required.)
- (4 points): Comments on where one should concentrate search activities based on the observed results.

#### Solution

When simulating the crash for 120 hours (5 days), it's expected that the higher the variance, the more the search will need to widen in order to find the debris after its movement, as the possible landing site will include more and more of the area surrounding its mean.

This was very clearly seen in the simulation, with the search area increasing only a small amount due to the currents not being particularly strong around the mean of the landing site. However, one crucial thing to note is that, when the variance starts reaching the 100km mark, some of the possible landing sites start to include both the inner section of the Philippine archipelago and part of its land masses. Considering the fact that the currents in this inner section of the archipelago are stronger than the ones found in the east, and the fact that land masses are also possible, the search effort for this toy plane would need to get much bigger in order to cover all the possible landing sites.

The wisest choice would be to concentrate in the east section, as the mean is found there. If not found there, the search could then move on to the inner section of the archipelago. If everything else fails, the search would need to move to the islands between the east and middle sections of the archipelago. This would cover all possible landing sites in order of probability.

![sigma 10](Images/crash_sigma_10.png)
![sigma 50](Images/crash_sigma_50.png)
![sigma 100](Images/crash_sigma_100.png)
![sigma 150](Images/crash_sigma_150.png)

----

## Part II - Estimating Flows with Gaussian Processes

### Problem 4.a (10 points)

Rubric:

- (1 point): States the choice of kernel function and provides a justification for this choice.
- (1 point): Identifies the parameters of the kernel function.
- (1 point): Explicitly states the search space for each kernel parameter.
- (1 point): Explicitly states the number of folds () for the cross-validation.
- (3 points): Provides the optimal kernel parameters from the search.
- (3 points): Provides a plot of the computed cost/performance metric over the search space for the kernel parameters.

### Problem 4.b (5 points)

Rubric:

- (3 points): Provides the optimal kernel values for three new location that are different from the location in Problem 4.a. (Plots do not need to be provided.)
- (2 points): For each kernel parameter, states if a pattern was observed.

### Problem 4.c (5 points)

Rubric:

- (1 point): Provides the optimal kernel values for at least two new choices of .
- (2 points): A plot showing the cost/optimization target is provided for the search space, for each choice of .
- (2 points): Comments on whether these results differ from those found in Problem 4.a, and on whether results from the choices of  in the problem differ from each other.

### Problem 4.d (10 points)

Rubric:

- (2 points): Provides the optimal kernel parameters as found through the software library.
- (2 points): Provides details on the library used.
- (2 points): Comments on whether these results differ from those found in Problem 4.a.
- (2 points): The results are the same, or, the results are different and an explanation is provided.
- (2 points): A plot showing the cost/optimization target is provided for the search space, or a plot comparing the predictions generated (in problem 5) if the results are different.

### Problem 5 (15 points)

Rubric:

- (2 points): Clearly states the choice of time-stamps at which to create predictions, and states why the choice was made.
- (2 points): Clearly states the method by which the prior means were chosen.
- (2 points): Provides a plot with a prediction for the horizontal velocity component at the chosen location.
- (2 points): Provides a plot with a prediction for the vertical velocity component at the chosen location.
- (3 points): Both plots have a labelled prediction for the mean for all of the time-stamps chosen.
- (3 points): Both plots have a labelled  band around the predicted mean for all of the time-stamps chosen.
- (1 point): Both plots have the observations included.

### Problem 6.a (15 points)

Rubric:

- (2 points): Provides a plot with the initial state of the simulation.
- (2 points): Provides a plot with an intermediate state of the simulation.
- (2 points): Provides a plot with the final state of the simulation.
- (2 points): Marks a location on the coast of the final state of the simulation where one should search for debris and provides a justification.
- (2 points): Marks a location over the ocean of the final state of the simulation where one should search for debris and provides a justification.
- (5 points): Provides three plots (initial, intermediate, final) for one other choice of , and comments on results (either to state why conclusions should change or why they should not).

### Problem 6.b (14 points)

Rubric:

- (2 points): Provides a plot with the initial state of the simulation, there should be no particles on land.
- (2 points): Provides a plot with an intermediate state of the simulation.
- (2 points): Provides a plot with the final state of the simulation.
- (4 points): Marks three locations on the final state of the simulation where monitoring stations should be placed.
- (4 points): Provides a convincing explanation for choosing these locations.
