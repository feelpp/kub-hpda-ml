from vtk import  *
import numpy as np

def read_case(filepath):
    """
    Read the Ensight Gold case file and return the reader object

    Parameters
    ----------
    filepath : str
        The path to the Ensight Gold case file

    Returns
    -------
    reader : vtkEnSightGoldBinaryReader
        The reader object
    """
    reader = vtkEnSightGoldBinaryReader()
    reader.SetCaseFileName(filepath)
    reader.Update()
    return reader
