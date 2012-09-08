'''

Define the MC2DATA corrections used in the VH analysis.

This script produces corrections.C, which can be

ROOT.gROOT.ProcessLine('.L corrections.C++')

to enable access to the functions in TTree::Draw

This file depends on mueg_trig_correction_results.json
which is generated by muEGTriggerMeasurement.py

Author: Evan K. Friis, UW Madison

'''

import json
import FinalStateAnalysis.Utilities.CppTools as cpp

# Make the class name easier to write
Bins = cpp.CppKinematicBinning
Func = cpp.CppFunctionWrapper

barrel = lambda x: ('eta', 0, 1.44, x)
endcap = lambda x: ('eta', 1.44, None, x)

barrel_e = lambda x: ('eta', 0, 1.44, x)
trans_e = lambda x: ('eta', 1.44, 1.57, x)
endcap_e = lambda x: ('eta', 1.57, None, x)

cfg = {
    'MuID' : Bins([
        ('pt', 0, 8, 1.0),
        ('pt', 8, 10, Bins([
            barrel(1.005),
            endcap(0.955),
        ])),
        ('pt', 10, 20, Bins([
            barrel(0.986),
            endcap(0.979),
        ])),
        ('pt', 20, 30, Bins([
            barrel(0.989),
            endcap(0.976),
        ])),
        ('pt', 30, 50, Bins([
            barrel(0.991),
            endcap(0.975),
        ])),
        ('pt', 50, 100, Bins([
            barrel(0.99),
            endcap(0.978),
        ])),
        ('pt', 100, None, Bins([
            barrel(0.99),
            endcap(0.978),
        ])),
    ]),
    'MuIso' : Bins([
        ('pt', 0, 8, 1.0),
        ('pt', 8, 10, Bins([
            barrel(0.968),
            endcap(0.936),
        ])),
        ('pt', 10, 20, Bins([
            barrel(0.992),
            endcap(0.990),
        ])),
        ('pt', 20, 30, Bins([
            barrel(1.0),
            endcap(0.998),
        ])),
        ('pt', 30, 50, Bins([
            barrel(1.0),
            endcap(0.998),
        ])),
        ('pt', 50, 100, Bins([
            barrel(1.0),
            endcap(1.0),
        ])),
        ('pt', 100, None, Bins([
            barrel(1.0),
            endcap(1.0),
        ])),
    ]),
    'MuHLT8' : Bins([
        ('pt', 0, 8, 1.0),
        ('pt', 8, 10, Bins([
            barrel(0.972),
            endcap(1.003),
        ])),
        ('pt', 10, 20, Bins([
            barrel(0.989),
            endcap(0.988),
        ])),
        ('pt', 20, 30, Bins([
            barrel(0.987),
            endcap(0.987),
        ])),
        ('pt', 30, 50, Bins([
            barrel(0.986),
            endcap(0.984),
        ])),
        ('pt', 50, 100, Bins([
            barrel(0.985),
            endcap(0.982),
        ])),
        ('pt', 100, None, Bins([
            barrel(0.982),
            endcap(0.982),
        ])),
    ]),
    # Electron efficiencies
    'EleID' : Bins([
        ('pt', 0, 10, 1.0),
        ('pt', 10, 20, Bins([
            barrel_e(1.024),
            trans_e(1.161),
            endcap_e(1.100),
        ])),
        ('pt', 20, 30, Bins([
            barrel_e(.989),
            trans_e(.995),
            endcap_e(1.004),
        ])),
        ('pt', 30, 40, Bins([
            barrel_e(.994),
            trans_e(1.00),
            endcap_e(.996),
        ])),
        ('pt', 40, 50, Bins([
            barrel_e(0.996),
            trans_e(.997),
            endcap_e(1.004),
        ])),
        ('pt', 50, 60, Bins([
            barrel_e(0.996),
            trans_e(.982),
            endcap_e(1.007),
        ])),
        ('pt', 60, 100, Bins([
            barrel_e(.996),
            trans_e(1.006),
            endcap_e(0.995),
        ])),
        ('pt', 100, None, Bins([
            barrel_e(.996),
            trans_e(1.006),
            endcap_e(0.995),
        ])),
    ]),
    'EleIso' : Bins([
        ('pt', 0, 10, 1.0),
        ('pt', 10, 20, Bins([
            barrel_e(1.008),
            trans_e(1.029),
            endcap_e(0.99),
        ])),
        ('pt', 20, 30, Bins([
            barrel_e(1.001),
            trans_e(0.967),
            endcap_e(0.995),
        ])),
        ('pt', 30, 40, Bins([
            barrel_e(1.00),
            trans_e(1.014),
            endcap_e(1.000),
        ])),
        ('pt', 40, 50, Bins([
            barrel_e(0.999),
            trans_e(.996),
            endcap_e(1.001),
        ])),
        ('pt', 50, 60, Bins([
            barrel_e(0.999),
            trans_e(.990),
            endcap_e(.998),
        ])),
        ('pt', 60, 100, Bins([
            barrel_e(.999),
            trans_e(1.019),
            endcap_e(0.998),
        ])),
        ('pt', 100, None, Bins([
            barrel_e(.999),
            trans_e(1.019),
            endcap_e(0.998),
        ])),
    ]),
}

# Get MuEG trigger corrections from separate file
with open('mueg_trig_correction_results.json') as mueg_results:
    mueg_trig_summary = json.load(mueg_results)
    eta_region_map = {
        'barrel' : barrel_e,
        'trans' : trans_e,
        'endcap' : endcap_e
    }
    bins = []
    for eta_region, eta_region_info in mueg_trig_summary.iteritems():
        function = '(%s)/(%s)' % (
            eta_region_info['data'], eta_region_info['mc'])
        bins.append(eta_region_map[eta_region](function.replace('x', 'pt')))
    cfg['MuEGTrig'] = Bins(bins)

with open('corrections.C', 'w') as output_file:
    output_file.write('//This file auto-generated by make_corrections.py\n')
    output_file.write('#include <iostream>\n')
    output_file.write('#include "TMath.h"\n')
    for name, data in cfg.iteritems():
        # Add some extra logic to detect if we are running on MC or DATA
        fixed_data = Bins([
            ('run', None, 2, data),
            ('run', 2, None, 1.0), # DATA scale factor is always 1.0
        ])
        func = Func(
            name, fixed_data, 'pt', 'eta', 'run',
            default=-999,
            warn='std::cerr << "Warning out of bounds in function {name}" << std::endl;\n'
        )
        output_file.write(str(func))
        output_file.write('\n')
