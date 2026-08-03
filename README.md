# ATC Simulator

## Air Traffic Control (ATC) Simulator – A-Level Computer Science NEA project

### Description:

Air Traffic Control is notorious for being one of the most stressful jobs in the world,
requiring strong communication and workload management skills under high-pressure
situations, with potentially thousands of lives on the line if mistakes are made. Large
commercial airports such as London Gatwick (LGW) operate hundreds of flights every
day, making safety and real-time decision-making even more crucial. This is what my
ATC training simulator addresses.

The system is a classroom-based simulation tool designed to be used in ATC schools. Instructors
can simulate various landing scenarios on this system, such as what to do if more aircraft
are ready to land than the maximum landing rate for that runway. The aim is that, by
demonstrating these scenarios visually, the confidence and understanding of the students
will improve, leading to fewer mistakes on the job and hence improving overall safety
within aviation.

### How to Run

sim.py contains all the code for this project. Given how long this file is, it has made me gain an appreciation for the usefulness of splitting modules of the program up into separate files. I incorporated this learning into my next major coding project (the Formula 1 tyre degradation simulator, which you can also view on my GitHub profile).

Alongside this file, all you need to run this simulator are the four png files for the compass and each of the playtime buttons. All the other graphics (settings sliders, radar interface, messages output box etc.) were designed using Python's tkinter library. Note that all the libraries you need to run the program are already imported at run time.
