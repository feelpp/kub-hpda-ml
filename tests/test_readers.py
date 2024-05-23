from feelpp.ktirio.hpdaml.readers import *


class TestEnsightReader:
    filepath = "src/cases/case_reader/basic.case"
    ensight_reader = EnsightReader(filepath)
    
    def test_getTimeset(self):
        reader = self.ensight_reader.readCase()
        time, timesteps = self.ensight_reader.getTimeset()
        assert timesteps == 1
