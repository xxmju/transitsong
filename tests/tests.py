from transitsong.main import Transit

# test that lightcurve downloads ok! 

def test_lc_download():
    tic = 124029677 
    sector = 33

    transit = Transit(tic, sector)

    assert len(transit.norm_flux) == len(transit.time), "Time and flux arrays are not the same length"
    assert len(transit.norm_flux) > 0, "norm flux array, time array is of length 0"
