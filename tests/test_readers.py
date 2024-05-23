from feelpp.ktirio.hpdaml.readers import *

def test_read_case():
    filepath = "src/cases/case_reader/basic.case"
    reader = read_case(filepath)
    timeset=reader.GetTimeSets()
    time=timeset.GetItem(0)
    timesteps=time.GetSize()
    assert timesteps == 1