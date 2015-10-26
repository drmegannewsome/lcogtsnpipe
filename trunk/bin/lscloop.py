#!/opt/epd/bin/python
description = "> process lsc data  "
usage = "%prog  -e epoch [-s stage -n name -f filter -d idnumber]\n available stages [wcs, psf, psfmag, zcat, abscat," \
        " mag,local,getmag]\n"

import os
import re
import sys
import glob
import string
from numpy import take, argsort, asarray, array
from optparse import OptionParser
import datetime
import lsc
# ###########################################################################

if __name__ == "__main__":   # main program
    parser = OptionParser(usage=usage, description=description, version="%prog 1.0")
    parser.add_option("-e", "--epoch", dest="epoch", default='20121212', type="str",
                      help='epoch to reduce  \t [%default]')
    parser.add_option("-T", "--telescope", dest="telescope", default='all', type="str",
                      help='-T telescope ' + ', '.join(lsc.telescope0['all']) + ', '.join(
                          lsc.site0) + ', fts, ftn, 1m0, kb, fl, fs, sinistro, sbig \t [%default]')
    parser.add_option("--instrument", dest="instrument", default='', type="str",
                      help='--instrument ' + ' kb, fl, fs, sinistro, sbig \t [%default]')
    parser.add_option("-R", "--RA", dest="ra", default='', type="str",
                      help='-R  ra    \t [%default]')
    parser.add_option("-D", "--DEC", dest="dec", default='', type="str",
                      help='-D dec   \t [%default]')
    parser.add_option("-n", "--name", dest="name", default='', type="str",
                      help='-n image name   \t [%default]')
    parser.add_option("-d", "--id", dest="id", default='', type="str",
                      help='-d identification id   \t [%default]')
    parser.add_option("-f", "--filter", dest="filter", default='', type="str",
                      help='-f filter [sloan,landolt, apass, u, g, r, i, z, U, B, V, R, I] \t [%default]')
    parser.add_option("-F", "--force", dest="force", action="store_true")
    parser.add_option("-b", "--bad", dest="bad", default='', type="str",
                      help='-b bad stage [wcs, psf, psfmag, zcat, abscat, mag, goodcat, getmag, merge,'
                           ' diff, template, cosmic] \t [%default]')
    parser.add_option("-s", "--stage", dest="stage", default='', type="str",
                      help='-s stage [wcs, psf, psfmag, zcat, abscat, mag, getmag, merge, diff, makestamp,'
                           ' template, apmag, cosmic, ingestsloan, ingestps1] \t [%default]')
    parser.add_option("--RAS", dest="ras", default='', type="str",
                      help='-RAS  ra    \t [%default]')
    parser.add_option("--DECS", dest="decs", default='', type="str",
                      help='-DECS dec   \t [%default]')
    parser.add_option("--RA0", dest="ra0", default='', type="str",
                      help='-RA0  ra    \t [%default]')
    parser.add_option("--DEC0", dest="dec0", default='', type="str",
                      help='-DEC0 dec   \t [%default]')
    parser.add_option("-x", "--xord", dest="xord", default=3, type=int,
                      help='-x order for bg fit   \t [%default]')
    parser.add_option("-y", "--yord", dest="yord", default=3, type=int,
                      help='-y order for bg fit \t [%default]')
    parser.add_option("--bkg", dest="bkg", default=4, type=float,
                      help=' bkg radius for the fit  \t [%default]')
    parser.add_option("--size", dest="size", default=7, type=float,
                      help='size of the stamp for the fit \t [%default]')
    parser.add_option("-t", "--threshold", dest="threshold", default=5.,
                      type='float', help='Source detection threshold \t\t\t %default')
    parser.add_option("-i", "--interactive", action="store_true",
                      dest='interactive', default=False, help='Interactive \t\t\t [%default]')
    parser.add_option("--show", action="store_true",
                      dest='show', default=False, help='show psf fit \t\t\t [%default]')
    parser.add_option("-c", "--center", action="store_false",
                      dest='recenter', default=True, help='recenter \t\t\t [%default]')
    parser.add_option("--fix", action="store_false",
                      dest='fix', default=True, help='fix color \t\t\t [%default]')
    parser.add_option("--cutmag", dest="cutmag", default=99., type="float",
                      help='--cutmag  [magnitude instrumental cut for zeropoint ]  \t [%default]')
    parser.add_option("--field", dest="field", default='', type="str",
                      help='--field  [landolt, sloan, apass]  \t [%default]')
    parser.add_option("--ref", dest="ref", default='', type="str",
                      help='--ref  sn22_20130303_0111.sn2.fits get sn position from this file \t [%default]')
    parser.add_option("--catalogue", dest="catalogue", default='', type="str",
                      help='--catalogue  sn09ip.cat    \t [%default]')
    parser.add_option("--calib", dest="calib", default='', type="str",
                      help='--calib  (sloan,natural,sloanprime)   \t [%default]')
    parser.add_option("--type", dest="type", default='fit', type="str",
                      help='--type mag for zero point   [fit,ph,mag]    \t [%default]')
    parser.add_option("--standard", dest="standard", default='', type="str",
                      help='--standard namestd  \t use the zeropoint from this standard    \t [%default]')
    parser.add_option("--xshift", dest="xshift", default=0, type="int",
                      help='x shift in the guess astrometry \t [%default]')
    parser.add_option("--fwhm", dest="fwhm", default='', type="str",
                      help='fwhm (in pixel)  \t [%default]')
    parser.add_option("--mode", dest="mode", default='sv', type="str",
                      help='mode for wcs (sv,astrometry)  \t [%default]')
    parser.add_option("--combine", dest="combine", default=1e-10, type="float",
                      help='range to combine (in days)  \t [%default]')
    parser.add_option("--datamax", dest="dmax", default=51000, type="float",
                      help='data max for saturation (counts)  \t [%default]')
    parser.add_option("--datamin", dest="dmin", default=-500, type="float",
                      help='data min for saturation (counts)  \t [%default]')
    parser.add_option("--yshift", dest="yshift", default=0, type="int",
                      help='y shift in the guess astrometry \t [%default]')
    parser.add_option("--filetype", dest="filetype", default=1, type="int",
                      help='filetype  1 [single], 2 [merge], 3 differences \t [%default]')
    parser.add_option("-o", "--output", dest="output", default='', type="str",
                      help='--output  write magnitude in the output file \t [%default]')
    parser.add_option("--tempdate", dest="tempdate", default='', type="str",
                      help='--tempdate  tamplate date \t [%default]')
    parser.add_option("--normalize", dest="normalize", default='i', type="str",
                      help='--normalize image [i], template [t] \t hotpants parameter  \t [%default]')
    parser.add_option("--convolve", dest="convolve", default='', type="str",
                      help='--convolve force convolution with image [i], template [t] \t hotpants parameter  \t [%default]')
    parser.add_option("-X", "--xwindow", action="store_true",
                      dest='xwindow', default=False, help='xwindow \t\t\t [%default]')
    parser.add_option("--z1", dest="z1", default=None, type="int",
                      help='z1 \t [%default]')
    parser.add_option("--z2", dest="z2", default=None, type="int",
                      help='z2 \t [%default]')
    parser.add_option("--groupidcode", dest="groupidcode", default=None, type="int",
                      help='groupidcode \t [%default]')
    parser.add_option("--ps1frames", dest="ps1frames", default='', type="str",
                      help='--ps1frames list of ps1 frames \t (download them manually) \t [%default]')
    parser.add_option('--zcatnew', action='store_true', help='use fitcol3 for the zero point and color term')
    parser.add_option("--bgo", dest="bgo", default=3, type=float,
                      help=' bgo parameter for hotpants  \t [%default]')
    parser.add_option("-p", "--psf", dest="psf", default='', type=str, help='psf image for template \t\t\t %default')
    parser.add_option("--mag", dest="mag", type=float, default=0, help='mag to subtract from template image \t\t [%default]')
    parser.add_option("--uncleaned", dest="clean", action='store_false', default=True, help='do not use cosmic ray cleaned image as template \t\t [%default]')
    parser.add_option("--subtract-mag-from-header", action='store_true', help='automatically subtract mag from header of template image \t\t [%default]')
    parser.add_option("--fixpix", dest="fixpix", action="store_true", default=False,
                      help='Run fixpix on the images before doing image subtraction')

    option, args = parser.parse_args()
    _instrument=option.instrument
    _telescope = option.telescope
    _type = option.type
    _stage = option.stage
    _bad = option.bad
    _mode = option.mode
    _groupid=option.groupidcode
    _filetype = option.filetype
    _ps1frames = option.ps1frames
    _bgo = option.bgo

    if not _groupid:
        _groupid=''
    _normalize = option.normalize
    _convolve = option.convolve
    if _telescope not in lsc.telescope0['all'] + lsc.site0 + ['all', 'ftn', 'fts', '1m0', '2m0', 'kb', 'fl', 'fs','sinistro','sbig']:
        sys.argv.append('--help')
    if option.force == None:
        _redo = False
    else:
        _redo = True
    if option.recenter == False:
        _recenter = True
    else:
        _recenter = False
    if _type not in ['fit', 'ph', 'mag']:
        sys.argv.append('--help')
    if _normalize not in ['i', 't']:
        sys.argv.append('--help')
    if _stage:
        if _stage in ['checkwcs', 'checkpsf', 'checkmag', 'checkquality', 'checkpos', 'checkcat',
                      'checkmissing', 'checkfvd', 'checkcosmic', 'checkdiff']:
            newargs = ['lsccheck.py']+['"'+arg+'"' if ' ' in arg else arg for arg in sys.argv[1:]] # in case you had quotes
            newcommand = ' '.join(newargs)
            os.system(newcommand) # redo this command with lsccheck.py instead of lscloop.py
            sys.exit()
        elif _stage not in ['wcs', 'psf', 'psfmag', 'zcat', 'abscat', 'mag', 'local', 'getmag', 'merge', 'diff',
                            'template', 'makestamp', 'apmag', 'cosmic', 'ingestsloan', 'ingestps1']:
            sys.argv.append('--help')
    if _bad:
        if _bad not in ['wcs', 'psf', 'psfmag', 'zcat', 'abscat', 'mag', 'goodcat', 'quality', 'cosmic', 'diff']:
            sys.argv.append('--help')
        if _bad=='diff' and _filetype!=1: sys.exit('can only check for -b diff on original images (--filetype 1)')
    if _mode not in ['sv','astrometry']:
            sys.argv.append('--help')
    option, args = parser.parse_args()
    _id = option.id
    _filter = option.filter
    _ra = option.ra
    _dec = option.dec
    _ras = option.ras
    _ra0 = option.ra0
    _dec0 = option.dec0
    _output = option.output
    _decs = option.decs
    _name = option.name
    _fwhm = option.fwhm
    _xord = option.xord
    _yord = option.yord
    _bkg = option.bkg
    _size = option.size
    _standard = option.standard
    _threshold = option.threshold
    _interactive = option.interactive
    _xwindow = option.xwindow
    _show = option.show
    _fix = option.fix
    _catalogue = option.catalogue
    _calib = option.calib
    _ref = option.ref
    _field = option.field
    _cutmag = option.cutmag
    _xshift = option.xshift
    _yshift = option.yshift
    _bin = option.combine
    _dmax = option.dmax
    _dmin = option.dmin
    _tempdate = option.tempdate
    _z1 = option.z1
    _z2 = option.z2
    zcatnew = option.zcatnew
    _fixpix = option.fixpix
    _mag = option.mag
    _clean = option.clean
    _subtract_mag_from_header = option.subtract_mag_from_header
    _psf = option.psf

    if _xwindow:
        from stsci.tools import capable

        capable.OF_GRAPHICS = False
        import matplotlib

        matplotlib.use('Agg')
        XX = ' -X '
    else:
        XX = ''

    if _filter:
        if _filter not in ['landolt', 'sloan', 'apass', 'u', 'g', 'r', 'i', 'z', 'U', 'B', 'V', 'R', 'I',
                           'SDSS-I', 'SDSS-G', 'SDSS-R', 'Pan-Starrs-Z', 'Bessell-B', 'Bessell-V',
                           'Bessell-R', 'Bessell-I', 'SDSS-G,SDSS-R,SDSS-I', 'Bessell-B,Bessell-V,Bessell-R',
                           'u,g', 'g,r', 'g,r,i', 'g,r,i,z', 'r,i,z', 'B,V,R', 'B,V', 'B,V,R,I', 'V,R,I']:
            sys.argv.append('--help')
        else:
            try:
                _filter = lsc.sites.filterst(_telescope)[_filter]
            except:
                pass

    if _filter and not _field:
        if _filter == 'landolt':
            _field = 'landolt'
        elif _filter == 'sloan':
            _field = 'sloan'
        elif _filter == 'apass':
            _field = 'apass'
    if _field and not _filter:
        if _field == 'landolt':
            _filter = 'landolt'
        elif _field == 'sloan':
            _filter = 'sloan'
        elif _field == 'apass':
            _filter = 'apass'

    option, args = parser.parse_args()
    epoch = option.epoch
    if '-' not in str(epoch):
        epoch0 = datetime.date(int(epoch[0:4]), int(epoch[4:6]), int(epoch[6:8]))
        listepoch = [re.sub('-', '', str(epoch0))]
    else:
        epoch1, epoch2 = string.split(epoch, '-')
        start = datetime.date(int(epoch1[0:4]), int(epoch1[4:6]), int(epoch1[6:8]))
        stop = datetime.date(int(epoch2[0:4]), int(epoch2[4:6]), int(epoch2[6:8]))
        listepoch = [re.sub('-', '', str(i)) for i in [start + datetime.timedelta(days=x)
                                                       for x in range(0, 1 + (stop - start).days)]]

    if not _stage or _stage in ['local', 'getmag', 'wcs', 'psf', 'psfmag', 'makestamp', 'cosmic', 'apmag','ingestsloan', 'ingestps1']:
        if len(listepoch) == 1:
            lista = lsc.mysqldef.getlistfromraw(lsc.myloopdef.conn, 'photlco', 'dayobs', str(listepoch[0]), '', '*',
                                                _telescope)
        else:
            lista = lsc.mysqldef.getlistfromraw(lsc.myloopdef.conn, 'photlco', 'dayobs', str(listepoch[0]),
                                                str(listepoch[-1]), '*', _telescope)
        if lista:
            ll0 = {}
            for jj in lista[0].keys():
                ll0[jj] = []
            for i in range(0, len(lista)):
                for jj in lista[0].keys():
                    ll0[jj].append(lista[i][jj])
            inds = argsort(ll0['mjd'])  # sort by mjd
            for i in ll0.keys():
                ll0[i] = take(ll0[i], inds)

            ll0['ra'] = ll0['ra0'][:]
            ll0['dec'] = ll0['dec0'][:]

            ll = lsc.myloopdef.filtralist(ll0, _filter, _id, _name, _ra, _dec, _bad, _filetype,_groupid, _instrument)
            print '##' * 50
            print '# IMAGE                                    OBJECT           FILTER           WCS            ' \
                  ' PSF           PSFMAG    APMAG       ZCAT          MAG      ABSCAT'
            for i in range(0, len(ll['filename'])):
                try:
                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                          (str(re.sub('.fits', '', ll['filename'][i])), str(ll['objname'][i]), str(ll['filter'][i]),
                           str(ll['wcs'][i]), str(re.sub('.fits', '', ll['psf'][i])), \
                           str(round(ll['psfmag'][i], 4)), str(ll['apmag'][i]), str(re.sub('.cat', '', ll['zcat'][i])),
                           str(round(ll['mag'][i], 4)), str(re.sub('.cat', '', ll['abscat'][i])))
                except:
                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                          (str(ll['filename'][i]), str(ll['objname'][i]), str(ll['filter'][i]), str(ll['wcs'][i]),
                           str(ll['psf'][i]), \
                           str(ll['psfmag'][i]), str(ll['apmag'][i]), str(ll['zcat'][i]), str(ll['mag'][i]),
                           str(ll['abscat'][i]))
            print '\n###  total number = ' + str(len(ll['filename']))
            # ####################################
            if _stage == 'local':  # calibrate local sequence from .cat files
                lsc.myloopdef.run_local(ll['filename'], _field, _interactive)
            elif _stage == 'getmag':  # get final magnitude from mysql
                if not _field:
                    sys.exit('use option --field landolt or sloan')
                else:
                    fields = [_field]
                for ff in fields:
                    lsc.myloopdef.run_getmag(ll['filename'], _field, _output, _interactive, _show, _bin, _type)
            elif _stage == 'psf':
                lsc.myloopdef.run_psf(ll['filename'], _threshold, _interactive, _fwhm, _show, _redo, XX, _fix, _catalogue, 'photlco')
            elif _stage == 'psfmag':
                lsc.myloopdef.run_fit(ll['filename'], _ras, _decs, _xord, _yord, _bkg, _size, _recenter, _ref,
                                      _interactive, _show, _redo, _dmax,_dmin,'photlco',_ra0,_dec0)
            elif _stage == 'wcs':
                lsc.myloopdef.run_wcs(ll['filename'], _interactive, _redo, _xshift, _yshift, _catalogue,'photlco',_mode)
            elif _stage == 'makestamp':
                lsc.myloopdef.makestamp(ll['filename'], 'photlco', _z1, _z2, _interactive, _redo, _output)
            elif _stage == 'apmag':
                lsc.myloopdef.run_apmag(ll['filename'], 'photlco')
            elif _stage == 'cosmic':
                lsc.myloopdef.run_cosmic(ll['filename'], 'photlco', 4.5, 0.2, 4, _redo)
            elif _stage == 'ingestsloan':
                listfile = [k + v for k, v in zip(ll['filepath'], ll['filename'])]
                lsc.myloopdef.run_ingestsloan(listfile, 'sloan')
            elif _stage == 'ingestps1':
                #if not _ps1frames:
                #    sys.exit('ERROR: list of PS1 frames not provided ')
                listfile = [k + v for k, v in zip(ll['filepath'], ll['filename'])]
                lsc.myloopdef.run_ingestsloan(listfile, 'ps1', _ps1frames)
        else:
            print '\n### no data selected'
    # ################################################
    else:
        for epo in listepoch:
            print '\n#### ' + str(epo)
            lista = lsc.mysqldef.getlistfromraw(lsc.myloopdef.conn, 'photlco', 'dayobs', str(epo), '', '*', _telescope)
            if lista:
                ll0 = {}
                for jj in lista[0].keys():
                    ll0[jj] = []
                for i in range(0, len(lista)):
                    for jj in lista[0].keys():
                        ll0[jj].append(lista[i][jj])

                inds = argsort(ll0['mjd'])  # sort by mjd
                for i in ll0.keys():
                    ll0[i] = take(ll0[i], inds)
                ll0['ra'] = ll0['ra0'][:]
                ll0['dec'] = ll0['dec0'][:]
                print _filter, _id, _name, _ra, _dec
                ll = lsc.myloopdef.filtralist(ll0, _filter, _id, _name, _ra, _dec, _bad, _filetype,_groupid, _instrument)
                if len(ll['filename']) > 0:
                    # print '##'*50
                    #                 print '# IMAGE                                    OBJECT           FILTER           WCS             PSF           PSFMAG          ZCAT          MAG      ABSCAT'
                    for i in range(0, len(ll['filename'])):
                        print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                              (str(ll['filename'][i]), str(ll['objname'][i]), str(ll['filter'][i]), str(ll['wcs'][i]),
                               str(ll['psf'][i]),
                               str(ll['psfmag'][i]), str(ll['zcat'][i]), str(ll['mag'][i]), str(ll['abscat'][i]))
                    print '\n###  total number = ' + str(len(ll['filename']))
                if _stage and len(ll['filename']) > 0:
                    print '##' * 50
                    print _stage
                    ll3 = {}
                    for ii in ll.keys():       ll3[ii] = ll[ii]
                    if _stage == 'zcat':
                        if not _field:
                            if _filter in ['U', 'B', 'V', 'R', 'I', 'landolt']:
                                _field = 'landolt'
                            elif _filter in ['u', 'g', 'r', 'i', 'z', 'sloan']:
                                _field = 'sloan'
                            elif _filter in ['apass']:
                                _field = 'apass'
                            else:
                                _field = 'sloan'

                        if not _name:
                            sys.exit('''name not selected, if you want to do zeropoint,
                                        you need to specify the name of the object''')
                        else:
                            if not _catalogue:
                                namesql = _name.replace(' ','%')
                                data = lsc.mysqldef.query(['select targetid from targetnames where name like "%' + namesql + '%"'], lsc.conn)
                                if data: _targetid = data[0]['targetid'] # pick the first result
                                else:    sys.exit('Target not found in database. Try "SN YYYYaa" with a space.')
                                data = lsc.mysqldef.query(['select name from targetnames where targetid="' + str(_targetid) + '"'],lsc.conn)
                                names = [targ['name'].replace(' ','').lower() for targ in data] # remove spaces & make lower case
                                catlist = glob.glob(lsc.__path__[0] + '/standard/cat/' + _field + '/*')
                                catnames = [os.path.basename(cat).split('_')[0].lower() for cat in catlist]
                                name_match = set(names) & set(catnames)
                                cat_match = [catlist[catnames.index(n)] for n in name_match]
                                print 'found', len(cat_match), 'matching catalogues'
                                if cat_match:
                                    _catalogue = cat_match[0] # pick the first result
                                    print 'using catalogue', _catalogue
                        if _field == 'apass':
                            ww0 = asarray([i for i in range(len(ll3['filter'])) if (ll['filter'][i] in ['V', 'B'])])
                            ww1 = asarray(
                                [i for i in range(len(ll3['filter'])) if (ll['filter'][i] in ['gp', 'rp', 'ip'])])
                            ww2 = asarray([i for i in range(len(ll3['filter'])) if
                                           (ll['filter'][i] in ['SDSS-G', 'SDSS-R', 'SDSS-I'])])

                            _color = ''
                            if len(ww0) >= 1:
                                for jj in ['B', 'V']:
                                    if jj in list(set(ll3['filter'])):
                                        _color = _color + lsc.sites.filterst1(_telescope)[jj]
                                print _color, _calib, _field
                                lsc.myloopdef.run_zero(ll3['filename'][ww0], _fix, _type, _field, _catalogue, _color,
                                                       _interactive, _redo, _show, _cutmag, 'photlco', _calib, zcatnew)
                            _color = ''
                            if len(ww1) >= 1:
                                for jj in ['gp', 'rp', 'ip']:
                                    if jj in list(set(ll3['filter'])):
                                        _color = _color + lsc.sites.filterst1(_telescope)[jj]
                                print _color, _calib, _field
                                lsc.myloopdef.run_zero(ll3['filename'][ww1], _fix, _type, _field, _catalogue, _color,
                                                       _interactive, _redo, _show, _cutmag, 'photlco', _calib, zcatnew)
                            _color = ''
                            if len(ww2) >= 1:
                                for jj in ['SDSS-G', 'SDSS-R', 'SDSS-I']:
                                    if jj in list(set(ll3['filter'])):
                                        _color = _color + lsc.sites.filterst1(_telescope)[jj]
                                print _color, _calib, _field
                                lsc.myloopdef.run_zero(ll3['filename'][ww2], _fix, _type, _field, _catalogue, _color,
                                                       _interactive, _redo, _show, _cutmag, 'photlco', _calib, zcatnew)

                        elif _field == 'landolt':
                            ww0 = asarray([i for i in range(len(ll3['filter'])) if
                                           (ll['filter'][i] in ['U', 'I', 'R', 'V', 'B'])])
                            _color = ''
                            if len(ww0) >= 1:
                                for jj in ['U', 'I', 'R', 'V', 'B']:
                                    if jj in list(set(ll3['filter'])):
                                        _color = _color + lsc.sites.filterst1(_telescope)[jj]
                                print _color, _calib, _field
                                lsc.myloopdef.run_zero(ll3['filename'][ww0], _fix, _type, _field, _catalogue, _color,
                                                       _interactive, _redo, _show, _cutmag, 'photlco', _calib, zcatnew)
                        elif _field == 'sloan':
                            ww0 = asarray([i for i in range(len(ll3['filter'])) if
                                           (ll['filter'][i] in ['up', 'gp', 'rp', 'ip', 'zs', 'SDSS-G', 'SDSS-R', 'SDSS-I'])])
                            _color = ''
                            if len(ww0) >= 1:
                                for jj in ['gp', 'up', 'rp', 'ip', 'zs']:
                                    if jj in list(set(ll3['filter'])):
                                        _color = _color + lsc.sites.filterst1(_telescope)[jj]
                                print _color, _calib, _field
                                lsc.myloopdef.run_zero(ll3['filename'][ww0], _fix, _type, _field, _catalogue, _color,
                                                       _interactive, _redo, _show, _cutmag, 'photlco', _calib, zcatnew)
                        else:
                            print 'warning: field not defined, zeropoint not computed'
                    elif _stage == 'abscat':  #    compute magnitudes for sequence stars > img.cat
                        if _standard:
                            mm = lsc.myloopdef.filtralist(ll0, _filter, '', _standard, '', '', '', _filetype,_groupid, _instrument)
                            if len(mm['filename']) > 0:
                                for i in range(0, len(mm['filename'])):
                                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                                          (str(mm['filename'][i]), str(mm['objname'][i]), str(mm['filter'][i]),
                                           str(mm['wcs'][i]), str(mm['psf'][i]),
                                           str(mm['psfmag'][i]), str(mm['zcat'][i]), str(mm['mag'][i]),
                                           str(mm['abscat'][i]))
                                lsc.myloopdef.run_cat(ll3['filename'], mm['filename'], _interactive, 1, _type, _fix,
                                                      'photlco', _field)
                            else:
                                print '\n### warning : standard not found for this night ' + str(epo)
                        else:
                            lsc.myloopdef.run_cat(ll3['filename'], '', _interactive, 1, _type, _fix, 'photlco', _field)
                    elif _stage == 'mag':  #    compute final magnitude using:   mag1  mag2  Z1  Z2  C1  C2
                        if _standard:
                            mm = lsc.myloopdef.filtralist(ll0, _filter, '', _standard, '', '', '', _filetype,_groupid, _instrument)
                            if len(mm['filename']) > 0:
                                for i in range(0, len(mm['filename'])):
                                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                                          (str(mm['filename'][i]), str(mm['objname'][i]), str(mm['filter'][i]),
                                           str(mm['wcs'][i]), str(mm['psf'][i]),
                                           str(mm['psfmag'][i]), str(mm['zcat'][i]), str(mm['mag'][i]),
                                           str(mm['abscat'][i]))
                                lsc.myloopdef.run_cat(ll3['filename'], mm['filename'], _interactive, 2, _type, False,
                                                      'photlco', _field)
                            else:
                                print '\n### error: standard not found for this night' + str(epo)
                        else:
                            lsc.myloopdef.run_cat(ll3['filename'], '', _interactive, 2, _type, False, 'photlco', _field)
                    elif _stage == 'merge':  #    merge images using lacos and swarp
                        listfile = [k + v for k, v in zip(ll['filepath'], ll['filename'])]
                        lsc.myloopdef.run_merge(array(listfile), _redo)
                    elif _stage == 'diff':  #    difference images using hotpants
                        if not _name:
                            sys.exit('you need to select one object: use option -n/--name')
                        if _telescope=='all':
                            sys.exit('you need to select one type of instrument -T [fs, fl ,kb]')
                        if _tempdate:
                            startdate = _tempdate.split('-')[0]
                            enddate   = _tempdate.split('-')[-1]
                        else:
                            startdate = '20120101'
                            enddate   = '20150101'

                        if _telescope == 'kb':
                            _temptel = 'sbig'
                        elif _telescope == 'fs':
                            _temptel = 'spectral'
                        elif _telescope == 'fl':
                            _temptel = 'sinistro'
                        print _temptel

                        lista1 = lsc.mysqldef.getlistfromraw(lsc.myloopdef.conn, 'photlco', 'dayobs', startdate, enddate, '*', _telescope)
                        if lista1:
                            ll00 = {}
                            for jj in lista1[0].keys():
                                ll00[jj] = []
                            for i in range(0, len(lista1)):
                                for jj in lista1[0].keys():
                                    ll00[jj].append(lista1[i][jj])
                            inds = argsort(ll00['mjd'])  #  sort by mjd
                            for i in ll00.keys():
                                ll00[i] = take(ll00[i], inds)
                            lltemp1 = lsc.myloopdef.filtralist(ll00, _filter, '', _name, _ra, _dec, '', 4, _groupid, '')
                        else:
                            lltemp1=()

                        lista2 = lsc.mysqldef.getlistfromraw(lsc.myloopdef.conn, 'photlco', 'dayobs', startdate, enddate, '*', _temptel)
                        if lista2:
                            ll00 = {}
                            for jj in lista2[0].keys():
                                ll00[jj] = []
                            for i in range(0, len(lista2)):
                                for jj in lista2[0].keys():
                                    ll00[jj].append(lista2[i][jj])
                            inds = argsort(ll00['mjd'])  #  sort by mjd
                            for i in ll00.keys():
                                ll00[i] = take(ll00[i], inds)
                            lltemp2 = lsc.myloopdef.filtralist(ll00, _filter, '', _name, _ra, _dec, '', 4, _groupid, '')
                        else:
                            lltemp2=()

                        if lltemp1:
                            lltemp = lltemp1
                        elif lltemp2:
                            lltemp = lltemp2
                        else:
                            sys.exit('template not found')

                        listtar = [k + v for k, v in zip(ll['filepath'], ll['filename'])]
                        listtemp = [k + v for k, v in zip(lltemp['filepath'], lltemp['filename'])]

                        lsc.myloopdef.run_diff(array(listtar), array(listtemp), _show, _redo, _normalize, _convolve, _bgo, _fixpix)
                        if len(listtemp) == 0 or len(listtar) == 0:
                            sys.exit('no data selected ')
                    elif _stage == 'template':  #    merge images using lacos and swarp
                        listfile = [k + v for k, v in zip(ll['filepath'], ll['filename'])]
                        lsc.myloopdef.run_template(array(listfile), _show, _redo, _interactive, _ra, _dec, _psf, _mag, _clean, _subtract_mag_from_header)
                    else:
                        print _stage + ' not defined'
                else:
                    print '\n### no data selected'