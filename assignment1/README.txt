# Assignment 1

This project contains a jupyter notebook with the solution for the Assignment 1 (assignment1.ipynb)
The file (day_ahead.py) contains the function that solves the LP optimization problem using the libray PuLP.
Make sure you install the libraries described in (requirements.txt).

## How to run:

Inside the project folder, create a new Python 3 virtual environment called venv:

``` python -m venv venv ```

Then activate it:

``` venv/Scripts/activate.bat ```

Now install the requirements:

``` pip install -r requirements.txt ```

Now install a new kernel called assignment1:

``` ipython kernel install --user --name=assignment1 ```

Start jupyter notebook and open the file assignment.ipynb:

``` jupyter notebook ```

P.S: Make sure that you select the Kernel "assignment1" that you have just created inside the jupyter notebook.