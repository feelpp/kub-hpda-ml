from vtk import  *
import numpy as np
import requests
import os
import zipfile
import io


class CkanDownloader:
    """A class to download files from CKAN
    Currently only supports zip files
    """

    def __init__(self,base_ckan_url,org_id,package_id,resource_filename):
        self.base_ckan_url = base_ckan_url
        self.org_id = org_id
        self.package_id = package_id
        self.resource_filename = resource_filename

        self.local_filename = None

    def download(self, is_zipped=True):
        """Downloads and writes to disc a file from CKAN

        Args:
            is_zipped (bool, optional): True if the downloaded file is compressed. Defaults to True.

        Raises:
            NotImplementedError: Only zip files are supported for now

        Returns:
            string: The local filename of the downloaded file. 
            If the file is zipped, the name of the folder is returned
        """
        #Downlaod file contents
        #TODO: Handle private access
        response = requests.get(
            f"{self.base_ckan_url}/{self.org_id}/resource/{self.package_id}/download/{self.resource_filename}",
            stream=True
        )

        if is_zipped:
            #extract zipfile
            z = zipfile.ZipFile(io.BytesIO(response.content))
            z.extractall()
            self.local_filename = z.namelist()[0]
            return self.local_filename
        else:
            raise NotImplementedError("Only zip files are supported for now")

    def delete(self):
        """Deletes the downloaded file
        """
        #TODO: Handle deletion more carefully
        if self.local_filename is not None:
            os.remove(self.local_filename)
            self.local_filename = None

class EnsightReader:
    """Wrapper class to read Ensight Gold Binary files using VTK
    """

    def __init__(self):
        self.reader = None
        self.mesh_cells = None

        #TODO: Support multiple scalar fields
        self.scalar_field = "solar_shading_coeff"

    def readCase(self,filepath):
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
        self.reader = reader
        return self.reader
    
    
    def getTimeset(self):
        """Get the timeset information from the reader object

        Raises:
            ValueError: Reader object is not set. Call readCase first

        Returns:
            tuple(vtkEnSightReaderTimeSet, int): The time object and the number of timesteps
        """
        if self.reader is None:
            raise ValueError("Reader object is not set. Call readCase first")
        
        #TODO: Support multiple timesets
        timeset = self.reader.GetTimeSets()
        time = timeset.GetItem(0)

        return time, time.GetSize()
    
    def getMesh(self):
        """Get the mesh from the reader object in numpy format

        Raises:
            ValueError: Reader object is not set. Call readCase first

        Returns:
            np.array: The mesh in numpy format. It is a 3D array : (number of cells (triangles), points of the cell, coordinates of each point)
        """
        #Use under the assumption that mesh is invariant in time
        if self.reader is None:
            raise ValueError("Reader object is not set. Call readCase first")
        
        output = self.reader.GetOutput().GetBlock(0)
        self.mesh_cells = np.empty((output.GetNumberOfCells(),3,3)) 
        for i in range(output.GetNumberOfCells()):
            #TODO: Slow, there should be a better way to convert to numpy
            cell = output.GetCell(i)
            cell_points = cell.GetPoints()
            self.mesh_cells[i] = np.array([cell_points.GetPoint(i) for i in range(cell_points.GetNumberOfPoints())])

        return self.mesh_cells
    
    def readTimestep(self, timestep):
        """Read the scalar field at a given timestep, using the class attribute scalar_field. 
            It returns the scalar field in numpy format. The shape of the array is the same as the number of cells in the mesh, and have a one to one correspondence with the cells.

        Args:
            timestep (int): The timestep to read 

        Raises:
            ValueError: Reader object is not set. Call readCase first

        Returns:
            np.array(): The scalar field in numpy format (number of cells, 1)
        """
        if self.reader is None:
            raise ValueError("Reader object is not set. Call readCase first")
        if self.mesh_cells is None:
            raise ValueError("Mesh object is not set. Call getMesh first")

        self.reader.SetTimeValue(timestep)
        self.reader.Update()

        #TODO: Support multiple blocks and multiple scalar fields
        output = self.reader.GetOutput().GetBlock(0)
        cell_data = output.GetCellData()
        
        field_vtk_array = cell_data.GetArray(self.scalar_field)
        scalar_field_array = np.empty((output.GetNumberOfCells()))
        for i in range(output.GetNumberOfCells()):
            #Assuming its the first value of tuple
            cell_value = field_vtk_array.GetTuple(i)[0]
            scalar_field_array[i] = cell_value

        return np.array(scalar_field_array)
