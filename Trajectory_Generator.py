##
# Author : Vikram Sunkara. 
#         The ReaDDy code was writen by Christoph Frohner, which was then adapted by Vikram Sunkara.
##

import os
import numpy as np
import readdy
import matplotlib.pyplot as plt
import pdb
import pickle

def Make_Sims(diffusion_constant,n_partices,name, dt=0.01, n_steps=999, interaction_distance=1.0):
	"""
	Parameters
	----------

	diffusion_constant : float
					The diffusion coefficient to evolve the system with

	n_particles : int
					The total number of particles to be distributed over the domain
	
	name : str
					The file name to save the trajectories under

	dt : float
				The time step at which to sample the position of the particles

	n_steps : int
				The number of time samples to take

	interaction_distance : float
					The radius within which a reaction is registered (This is not used in this particular version)

	"""

	system = readdy.ReactionDiffusionSystem(box_size=[50., 50., 5.], periodic_boundary_conditions=[False, False, False])

	system.add_species("A", diffusion_constant=diffusion_constant)

	origin = np.array([-23., -23., -0.001])
	extent = np.array([46., 46., 0.002])
	system.potentials.add_box("A", force_constant=50., origin=origin, extent=extent)

	simulation = system.simulation()

	simulation.output_file = "Sims.h5"

	# add particles uniformly distributed in the box

	initial_positions = np.random.uniform(size=(n_partices, 3)) * extent + origin

	simulation.add_particles(type="A", positions=initial_positions)

	# observables

	# if you want to look at a video afterwards, also contains all positions
	simulation.record_trajectory(stride=1)

	# if you are only interested in positions of A particles
	simulation.observe.particle_positions(stride=1, types=["A"])

	# delete output file if it already exists
	if os.path.exists(simulation.output_file):
		os.remove(simulation.output_file)

	# run the simulation
	simulation.run(n_steps=n_steps, timestep=dt)

	# obtain observed output
	trajectory = readdy.Trajectory(simulation.output_file)

	# this converts the trajectory to a format which VMD can read
	# view the trajectory via the commandline with "vmd -e sims.h5.xyz.tcl"
	trajectory.convert_to_xyz(particle_radii={"A": interaction_distance / 2.}, draw_box=True)

	times, positions = trajectory.read_observable_particle_positions()

	# We plot the trajectories for later identification
	for i in range(n_partices):
		X = []
		Y = []
		for t in range(len(times)):
			X.append(positions[t][i]["x"])
			Y.append(positions[t][i]["y"])
		plt.plot(X,Y)
	plt.title("Simulated Trajectories| diff Coeff %f | dt %f | n_steps %d"%(diffusion_constant,dt,n_steps))
	plt.savefig("True_Trajecs_%s.pdf"%(name),format="pdf")

	X_es = []
	Y_es = []

	for t in range(len(times)):
		X_es.append(positions[t]["x"])
		Y_es.append(positions[t]["y"])

	# We Store the positions of the particles so that we can render using openCV
	f = open("%s.pck"%(name),"wb")
	pickle.dump({"X":X_es, "Y":Y_es},f,protocol=2) 
	f.close()
   


if __name__ == '__main__':
	# Example of how to run the code.

	##
	#Params
	##
	interaction_distance = 1.0
	n_partices = 100
	diffusion_constant = 0.5
	dt = 0.01
	n_steps = 999

	num_replicates = 5

	for i in range(num_replicates):
		name = "Sims_D_0p5_numPart_%d_run_%d_"%(n_partices,i+1)
		Make_Sims(diffusion_constant,n_partices,name, dt=0.01, n_steps=999)
	