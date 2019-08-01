### Microscope_Receptor_Diffusion_Simulator
Code for generating simulated receptor diffusion signals detected by microscopes.

#The following code is to generate pure diffusion trajectories and then render these trajectories as output images of microscopes. The images can be used to configure and cross validate current particle tracking software. 

## Warning 
The code is build on ReaDDY and OpenCV packages. Sadly, in Python 3, there seems to be a clash in the HDF5 package for both these libraries, so the code is split into two different files which both need to be run in separate environments. ReaDDY (v2.0.2-29) needs python 3.7+  and OpenCV (2.4.12) was implemented on python 2.7+. This is really an inconvenience, there might be a more efficient way of managing this clash.  This is something to fix for future. 


##Requirements:

Trajectory_Generator.py
	Python 3.7+
	ReaDDY (v2.0.2-29)
	
Trajectory_Renderer.py
	Python 2.7+
	cv2 (2.4.12)
	tifffile (2019.6.18)
	Basic Scientific Python
