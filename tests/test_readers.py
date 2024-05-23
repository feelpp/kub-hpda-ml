from feelpp.ktirio.hpdaml.readers import *


class TestEnsightReader:
    filepath = "src/cases/case_reader/basic.case"
    ensight_reader = EnsightReader()
    
    def test_getTimeset(self):
        reader = self.ensight_reader.readCase(self.filepath)
        time, timesteps = self.ensight_reader.getTimeset()
        assert timesteps == 1
