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

def Samples_On_A_Circle(Random_Points,radius=10,noise=1):

	X_Y_Z = np.empty_like(Random_Points)
	X_Y_Z[:,0] = (radius + Random_Points[:,1])*np.sin(Random_Points[:,0]*2*np.pi)
	X_Y_Z[:,1] = (radius + Random_Points[:,2])*np.cos(Random_Points[:,0]*2*np.pi)
	X_Y_Z[:,2] = 0.0 

	return X_Y_Z

def Make_Sims(particle_names, diffusion_constants,n_partices,name, dt=0.01, n_steps=999, interaction_distance=1.0):
	"""
	Parameters
	----------

	particle_names : list String
					Name of each of the particles being simulated

	diffusion_constant : list float
					The diffusion coefficient to evolve the system with

	n_particles : list int
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

	#### Initialising the domain

	system = readdy.ReactionDiffusionSystem(box_size=[50., 50., 5.], periodic_boundary_conditions=[False, False, False])

	for i in range(len(particle_names)):
		system.add_species(particle_names[i], diffusion_constant=diffusion_constants[i])

	origin = np.array([-23., -23., -0.001])
	extent = np.array([46., 46., 0.002])

	#### Fields and Boundary

	# Boundary Box for all Particles
	for i in range(len(particle_names)):
		system.potentials.add_box(particle_names[i], force_constant=1., origin=origin, extent=extent)

	# Moutain for Super Diffusion
	system.potentials.add_sphere(particle_type="Direct", inclusion = False, force_constant= 4., origin=[0,0,0], radius=35)

	# Trench for Sub Diffusion
	system.potentials.add_spherical_barrier( particle_type="Confined", height=-15.0, width=5.0, origin=[0,0,0], radius=10)

	simulation = system.simulation()

	simulation.output_file = "Sims.h5"

	### Particle position initialisation

	# Add particles uniformly distributed in the box

	for i in range(len(particle_names)):
		if particle_names[i] ==  'Direct':
			initial_positions = np.random.uniform(size=(n_partices[i], 3)) * np.divide(extent,4) - np.divide(extent,4)/2
		elif particle_names[i] == 'Confined':
			initial_positions = Samples_On_A_Circle(np.random.uniform(size=(n_partices[i], 3)),radius=10)
		else:
			initial_positions = np.random.uniform(size=(n_partices[i], 3)) * extent + origin
		simulation.add_particles(type=particle_names[i], positions=initial_positions)

	#### Observables

	# if you want to look at a video afterwards, also contains all positions
	simulation.record_trajectory(stride=1)

	# if you are only interested in positions of A particles
	simulation.observe.particle_positions(stride=1, types=particle_names)

	# delete output file if it already exists
	if os.path.exists(simulation.output_file):
		os.remove(simulation.output_file)

	# run the simulation
	simulation.run(n_steps=n_steps, timestep=dt)

	# obtain observed output
	trajectory = readdy.Trajectory(simulation.output_file)

	# this converts the trajectory to a format which VMD can read
	# view the trajectory via the commandline with "vmd -e sims.h5.xyz.tcl"
	for i in range(len(particle_names)):
		trajectory.convert_to_xyz(particle_radii={particle_names[i]: interaction_distance / 2.}, draw_box=True)

	times, positions = trajectory.read_observable_particle_positions()

	# Plotting the trajectories for later identification
	for i in range(np.sum(n_partices)):
		X = []
		Y = []
		for t in range(len(times)):
			X.append(positions[t][i]["x"])
			Y.append(positions[t][i]["y"])
		plt.plot(X,Y)
	plt.title("Simulated Trajectories| particle_names %s | diff Coeff %s | dt %f | n_steps %d"%(str(particle_names),str(diffusion_constants),dt,n_steps))
	plt.savefig("True_Trajecs_%s.pdf"%(name),format="pdf")

	X_es = []
	Y_es = []

	for t in range(len(times)):
		X_es.append(positions[t]["x"])
		Y_es.append(positions[t]["y"])

	# Store the positions of the particles so that we can render using openCV
	f = open("%s.pck"%(name),"wb")
	pickle.dump({"X":X_es, "Y":Y_es},f,protocol=2) 
	f.close()
   


if __name__ == '__main__':
	# Example of how to run the code.

	##
	#Params
	##
	interaction_distance = 1.0
	n_partices = [73,15,5,6] 
	diffusion_constants = [0.5,0.5,0.00003,1.0] 
	dt = 0.01
	n_steps = 999
	particle_names = ['Brown','Confined','Immob','Direct']

	num_replicates = 10

	for i in range(num_replicates):
		name = "Multi_Sims_D_ALL_numPart_%d_run_%d_"%(np.sum(n_partices),i+1)
		Make_Sims(particle_names,diffusion_constants,n_partices,name, dt=dt, n_steps=999)
	