##Test File
import sys,os,traceback,pickle
import numpy as np
from astropy.table import Table

_SRCDIR_ = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.append(_SRCDIR_)
import diffimageml


# Hard coding the test data filenames
_DIFFIM1_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'diff_pydia_1.fits.fz'))
_FAKEDIFFIM1_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'diff_pydia_1_fakegrid.fits'))
_SEARCHIM1_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'sky_image_1.fits.fz'))
_TEMPLATEIM1_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'template_1.fits.fz'))

_DIFFIM2_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'diff_pydia_2.fits.fz'))
_FAKEDIFFIM2_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'diff_pydia_2_fakegrid.fits'))
_SEARCHIM2_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'sky_image_2.fits.fz'))
_TEMPLATEIM2_ = os.path.abspath(os.path.join(
    _SRCDIR_, 'diffimageml', 'test_data', 'template_2.fits.fz'))

_GOFAST_ = True # Use this to skip slow tests

def test_pristine_data():
    """
    Check for existence of the pristine (level 0) test data
    located in the testdata directory
    """
    assert os.path.isfile(_DIFFIM1_)
    assert os.path.isfile(_SEARCHIM1_)
    assert os.path.isfile(_TEMPLATEIM1_)

    assert os.path.isfile(_DIFFIM2_)
    assert os.path.isfile(_SEARCHIM2_)
    assert os.path.isfile(_TEMPLATEIM2_)

    return 1

def test_fetch_gaia_sources():
    """ Check that an astroquery call to the Gaia db works"""
    # read in a fits file
    searchim1 = diffimageml.fakeplanting.FitsImage(_SEARCHIM1_)

    # fetch gaia data
    # NOte: we adjust the save_suffix so we can test saving of the output to
    # a file, but it will not conflict  with existence of a pre-baked gaia
    # catalog test file with the default suffix GaiaCat
    searchim1.fetch_gaia_sources(save_suffix='TestGaiaCat')

    # TODO : more informative test output?
    assert type(searchim1.gaia_source_table) == Table
    assert len(searchim1.gaia_source_table) > 0
    #assert os.path.isfile(searchim1.gaia_source_table.savefilename)

    return 1

def test_photometry_of_stars():
    """Check measuring photometry of known stars in the image"""
    fitsimageobject = diffimageml.FitsImage(_SEARCHIM1_)
    # TODO: must also get gaia sources, but that's a separate test, should
    #  do them in series, and pass the object along?
    fitsimageobject.fetch_gaia_sources()
    fitsimageobject.do_stellar_photometry(fitsimageobject.gaia_source_table)
    assert(fitsimageobject.stellar_phot_table is not None)
    return


def test_measure_zeropoint():
    """Check measuring of zeropoint from known stars in the image"""
    fitsimageobject = diffimageml.FitsImage(_SEARCHIM1_)
    # TODO: must also get gaia sources, but that's a separate test, should
    #  do them in series, and pass the object along?
    fitsimageobject.measure_zeropoint()
    assert(fitsimageobject.zeropoint is not None)
    return

def test_build_epsf_model(verbose=True):
    """Check construction of an ePSF model from Gaia stars.
    """
    fitsimageobject = diffimageml.FitsImage(_SEARCHIM1_)

    # Fetch gaia sources (read from disk if possible)
    fitsimageobject.fetch_gaia_sources(save_suffix='TestGaiaCat')

    # Build the ePSF model and save to disk
    fitsimageobject.build_epsf_model(
        verbose=verbose, save_suffix='TestEPSFModel')

    assert(fitsimageobject.epsf is not None)
    assert(fitsimageobject.epsf.data.sum()>0)

    # read in the ePSF model we just created
    fitsimageobject.read_epsf_model(save_suffix='TestEPSFModel')
    assert(fitsimageobject.epsf is not None)
    assert(fitsimageobject.epsf.data.sum()>0)

    return


def test_fakeplanter_class():
    """Create a FakePlanter object from the pristine (level 0) test data"""
    fakeplanterobject = diffimageml.FakePlanter(
        _DIFFIM1_, _SEARCHIM1_, _TEMPLATEIM1_)
    return 1


def test_fakeplanter(accuracy=0.05):
    # a fake planter object which has had fake planting done
    fakeplanterobject = diffimageml.FakePlanter(
        _DIFFIM1_, _SEARCHIM1_, _TEMPLATEIM1_)

    epsf = diffimageml.util.lco_epsf(fakeplanterobject)
    locations = diffimageml.util.get_lattice_positions(fakeplanterobject)
    pixels,skycoords = locations

    # TODO: this is gonna need debugging
    pre_imdata = fakeplanterobject.diffim.sci.data
    post_im = fakeplanterobject.plant_fakes(epsf,pixels)
    post_imdata = post_im.data

    fitsflux = np.sum(post_imdata - pre_imdata)
    # TODO: this should have SCA to stay general if plants are scaled differently
    epsfflux = int(post_im.header['N_fake'])*float(post_im.header['F_epsf'])
    #print(fitsflux,epsfflux)
    if np.abs(fitsflux-epsfflux)/epsfflux < accuracy:
        #print("plant was successful")
        return 1

def test_FitsImageClass():
    from astropy.io.fits import HDUList,PrimaryHDU
    FitsImageClassInstance = diffimageml.FitsImage(_SEARCHIM1_)
    assert( isinstance(FitsImageClassInstance.hdulist,HDUList))
    return FitsImageClassInstance

def test_source_detection(FitsImageTest):
    source_catalog = FitsImageTest.detect_sources()
    return FitsImageTest.has_detections()

def test_detection_efficiency():
    fakeplanterobject = diffimageml.FakePlanter(
        _FAKEDIFFIM2_)
    eff = fakeplanterobject.calculate_detection_efficiency()
    return eff

def test_host_galaxy_detection(Image=None):
    import numpy as np
    if Image == None:
        SkyImageClassInstance=diffimageml.FitsImage(_SEARCHIM1_)
        SkyImageClassInstance.detect_sources()
    elif not Image.has_detections():
        Image.detect_sources()
        SkyImageClassInstance = Image
    else:
        SkyImageClassInstance = Image
    pixel_x = 2012
    pixel_y = 2056
    ra = 17.3905276
    dec = 15.0091647
    ###Tests detect host galaxies with pixel coords
    SkyImageClassInstance.detect_host_galaxies(pixel_x , pixel_y)
    assert(len(SkyImageClassInstance.hostgalaxies) == 1)
    host_x = SkyImageClassInstance.hostgalaxies[0].xcentroid.value
    host_y = SkyImageClassInstance.hostgalaxies[0].ycentroid.value
    assert( np.sqrt( (pixel_x - host_x) ** 2 + (pixel_y - host_y) ** 2 ) < 10)

    ##Tests detect host galaxies with sky coords
    SkyImageClassInstance.detect_host_galaxies(ra , dec , pixel_coords = False)
    assert(len(SkyImageClassInstance.hostgalaxies) == 1)
    host_x = SkyImageClassInstance.hostgalaxies[0].xcentroid.value
    host_y = SkyImageClassInstance.hostgalaxies[0].ycentroid.value
    assert( np.sqrt( (pixel_x - host_x) ** 2 + (pixel_y - host_y) ** 2 ) < 10)

def test_diffimageml():
    if _GOFAST_:
        print("GO FAST!  SKIPPING SLOW TESTS")
    failed=0
    total=0
    skipped=0
    # Fill in tests here.  Put a separate try/except around each test and track
    # the count of total tests and failures
    try:
        print('Testing pristine data...', end='')
        total += 1
        test_pristine_data()
        print("Passed!")
    except Exception as e:
        print('Failed')
        print(traceback.format_exc())
        failed+=1

    try:
        FitsImage_Instance = None
        print('Testing FitsImage instantiation...', end='')
        total += 1
        FitsImage_Instance = test_FitsImageClass()
        print("Passed!")
    except Exception as e:
        print('Failed')
        print(traceback.format_exc())
        failed+=1


    try:
        if not _GOFAST_:
            print('Testing Gaia astroquery...', end='')
            total += 1
            test_fetch_gaia_sources()
            print("Passed Gaia astroquery!")
        else:
            skipped += 1
    except Exception as e:
        print('Failed Gaia astroquery')
        print(traceback.format_exc())
        failed+=1

    try:
        print('Testing measure the zeropoint from known stars...', end='')
        total += 1
        test_measure_zeropoint()
        print("Passed zeropoint measurement!")
    except Exception as e:
        print('Failed zeropoint measurement')
        print(traceback.format_exc())
        failed+=1

    try:
        if not _GOFAST_:
            print('Testing ePSF model construction...', end='')
            total += 1
            test_build_epsf_model()
            print("Passed ePSF model construction!")
        else:
            skipped += 1
    except Exception as e:
        print('Failed  ePSF model construction :(')
        print(traceback.format_exc())
        failed+=1

    try:
        print('Testing FakePlanter instantiation...', end='')
        total += 1
        test_fakeplanter_class()
        print("Passed FakePlanter instantiation!")
    except Exception as e:
        print('Failed FakePlanter instantiation')
        print(traceback.format_exc())
        failed+=1

    try:
        if not _GOFAST_:
            print('Testing FakePlanter planting...', end='')
            total += 1
            test_fakeplanter(accuracy=0.05)
            print("Passed  FakePlanter planting!")
        else:
            skipped += 1

    except Exception as e:
        print('Failed  FakePlanter planting')
        print(traceback.format_exc())
        failed+=1


    try:
        if not _GOFAST_:
            print('Testing SourceDetection...', end='')
            total += 1
            if FitsImage_Instance is not None:
                detected = test_source_detection(FitsImage_Instance)
            else:
                detected = test_source_detection(diffimageml.FitsImage(_SEARCHIM1_))
            if not detected:
                raise RuntimeError("Source detection successful, but no catalog found.")
            print("Passed source detection!")
        else:
            skipped += 1
    except Exception as e:
        print('Failed source detection')
        print(traceback.format_exc())
        failed+=1

    try:
        if not _GOFAST_:
            print ("Testing Host Galaxy Detection...", end='')
            total += 1
            test_host_galaxy_detection(Image=FitsImage_Instance)
            print ("Passed host galaxy detection!")
        else:
            skipped += 1
    except Exception as e:
        print('Failed host galaxy detection')
        print(traceback.format_exc())
        failed += 1

    try:
        if not _GOFAST_:
            print ("Testing Efficiency Calculation...", end='')
            total += 1
            test_detection_efficiency()
            print ("Passed Efficiency Calculation!")
        else:
            skipped += 1
    except Exception as e:
        print('Failed Efficiency Calculation')
        print(traceback.format_exc())
        failed += 1
    
    if _GOFAST_:
        print('Passed %i/%i tests, skipped %i slow tests.'%(total-failed,total,skipped))
    else:
        print('Passed %i/%i tests.'%(total-failed,total))

    return

if __name__ == '__main__':
    test_diffimageml()