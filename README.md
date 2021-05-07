What is VASP_Raman_Peaks
------------------------
Calculate Raman active mode using VASP hessian calculation. 


Special Notes
-------------

This Repo is created based on https://github.com/raman-sc/VASP repo. please visit this original repo to learn about theory behind this implementation. and please cite there paper D. Porezag, M.R. Pederson, PRB, 54, 7830 (1996).

just to cleaify I reimplemented this code because original code execute in a serial mannar which takes lot of time. I completely rewrote the code to run all calculation parallely. This code is written and tested in PBS cluster. If you have any question regarding methodology please contact original author. if you found any problem with my implementation, please feel free to reach out irajibdu@gmail.com. 

