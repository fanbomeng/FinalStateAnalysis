'''

Interface to official corrections from the muon POG
===================================================

Interface: Evan K. Friis, UW Madison

https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonReferenceEffs

In general, there is a eta dependent correction for pt > 20, and a pt dependent
correction otherwise.

Available correctors::

make_muon_pog_PFTight_2011()
make_muon_pog_PFTight_2012()
make_muon_pog_PFRelIsoDB012_2012()
make_muon_pog_PFRelIsoDB02_2012()
make_muon_pog_PFRelIsoDB02_2011()
make_muon_pog_PFRelIsoDB012_2011()
make_muon_pog_Mu17Mu8_Mu17_2012()
make_muon_pog_Mu17Mu8_Mu8_2012()

which do what they say on the tin. Each of these returns a corrector object
that has a method "correction(pt, eta)". Note that the Mu17_Mu8 corrections are
only available for 2012.

The trigger efficiencies for 2011 are encoded in a C++ file::
interface/MuonPOG2011HLTEfficiencies.h

They are available as python functions (taking the eta of both muons) as::

muon_pog_Mu17Mu8_eta_eta_2011(eta1, eta2)
muon_pog_Mu13Mu8_eta_eta_2011(eta1, eta2)

'''

import os
import re
#from FinalStateAnalysis.Utilities.rootbindings import ROOT
import ROOT
import numpy as np
import array
_DATA_DIR = os.path.join(os.environ['CMSSW_BASE'], 'src',
                         "FinalStateAnalysis", "TagAndProbe", "data")

_DATA_FILES = {
    '2012ReReco' : {
        'SingleMuTrg' : os.path.join(_DATA_DIR, 'SingleMuonTriggerEfficiencies_eta2p1_Run2012ABCD_v5trees.root'),
        'PFID'        : os.path.join(_DATA_DIR, 'MuonEfficiencies_Run2012ReReco_53X.root'),
        'Iso'         : os.path.join(_DATA_DIR, 'MuonEfficiencies_ISO_Run_2012ReReco_53X.root'),
    },
    '2011'     : os.path.join(_DATA_DIR, 'MuonEfficiencies2011_42X_DataMC.root'),
    '2012'     : os.path.join(_DATA_DIR, 'MuonEfficiencies_11June2012_52X.root'), # Outdated!
    '2012ABCD' : os.path.join(_DATA_DIR, 'MuonEfficiencies_Run2012ReReco_53X.root'),  # For ID/Iso: combined in 1 WAS:'Muon_ID_iso_Efficiencies_Run_2012ABCD_53X.root'
    '2012AB'    : os.path.join(_DATA_DIR, 'MuonEfficiencies_Run_2012A_2012B_53X.root'), # For trigger: one each 
    '2012C'    : os.path.join(_DATA_DIR, 'MuonEfficiencies_Run_2012C_53X.root'),
    '2012D'    : os.path.join(_DATA_DIR, 'TriggerMuonEfficiencies_Run_2012D_53X.root'),
    '2015CD' : {
        'PFID'   : os.path.join(_DATA_DIR, 'MuonID_Z_RunCD_Reco76X_Feb15.root'),
        'Iso'    : os.path.join(_DATA_DIR, 'MuonIso_Z_RunCD_Reco76X_Feb15.root'),
        'Trigger': os.path.join(_DATA_DIR, 'SingleMuonTrigger_Z_RunCD_Reco76X_Feb15.root')
    },
    '2016B'  : {
        'PFID'   : os.path.join(_DATA_DIR, 'MuonID_Z_2016runB_2p6fb.root'),
        'Iso'    : os.path.join(_DATA_DIR, 'MuonISO_Z_2016runB_2p6fb.root'),
        'Trigger': os.path.join(_DATA_DIR, 'SingleMuonTrigger_Z_RunCD_Reco76X_Feb15.root'),
        'Tracking': os.path.join(_DATA_DIR, 'general_tracks_and_early_general_tracks_corr_ratio.root'),
        'TrggerIso22': os.path.join(_DATA_DIR, 'Muon_IsoMu22_eff_Spring16.root')
        
    }
}


# Load the 2011 muon HLT corrections and give the function a consistent name
#ROOT.gSystem.Load("libFinalStateAnalysisTagAndProbe")
#muon_pog_Mu13Mu8_eta_eta_2011 = ROOT.Eff_HLT_Mu13_Mu8_2011_TPfit_RunAB_EtaEta_DATAoverMC
#muon_pog_Mu17Mu8_eta_eta_2011 = ROOT.Eff_HLT_Mu17_Mu8_2011_TPfit_RunAB_EtaEta_DATAoverMC

def make_muon_pog_PFTight_2011():
    ''' Make PFTight DATA/MC corrector for 2011 '''
    return MuonPOG2011Combiner(
        MuonPOGCorrection(
            _DATA_FILES['2011'],
            "DATA/MC_PFTIGHT_nH10_2011A_pt__abseta<1.2",
            "DATA/MC_PFTIGHT_nH10_2011A_pt__abseta>1.2",
            "DATA/MC_PFTIGHT_nH10_2011A_eta__pt>20",
        ),
        MuonPOGCorrection(
            _DATA_FILES['2011'],
            "DATA/MC_PFTIGHT_nH10_2011B_pt__abseta<1.2",
            "DATA/MC_PFTIGHT_nH10_2011B_pt__abseta>1.2",
            "DATA/MC_PFTIGHT_nH10_2011B_eta__pt>20",
        )
    )

def make_muon_pog_PFTight_2012():
    ''' Make PFTight DATA/MC corrector for 2012 '''
    return BetterMuonPOGCorrection(
        _DATA_FILES['2012ReReco']['PFID'],
        [(0.9, 'DATA_over_MC_Tight_pt_abseta<0.9'   ),
         (1.2, 'DATA_over_MC_Tight_pt_abseta0.9-1.2'),
         (2.1, 'DATA_over_MC_Tight_pt_abseta1.2-2.1'),
         (2.4, 'DATA_over_MC_Tight_pt_abseta2.1-2.4')],
        'DATA_over_MC_Tight_eta_pt20-500'
    )

def make_muon_pog_PFTight_2012ABCD():
    ''' Make PFTight DATA/MC corrector for 2012 '''
    return MuonPOGCorrection3R(
        _DATA_FILES['2012ABCD'],
        "DATA_over_MC_Tight_pt_abseta<0.9_2012ABCD",
        "DATA_over_MC_Tight_pt_abseta0.9-1.2_2012ABCD",
        "DATA_over_MC_Tight_pt_abseta1.2-2.1_2012ABCD",
        "DATA_over_MC_Tight_eta_pt20-500_2012ABCD",
    )

def make_muon_pog_PFTight_2015CD():
    ''' Make PFTight DATA/MC corrector for 2012 '''
    return MuonPOGCorrection2D(
        _DATA_FILES['2015CD']['PFID'],
        "MC_NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio"
    )
def make_muon_pog_PFMedium_2015CD():
    ''' Make PFTight DATA/MC corrector for 2012 '''
    return MuonPOGCorrection2D(
        _DATA_FILES['2015CD']['PFID'],
        "MC_NUM_MediumID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio"
    )
def make_muon_pog_PFLoose_2015CD():
    return MuonPOGCorrection2D(
        _DATA_FILES['2015CD']['PFID'],
        "MC_NUM_LooseID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio"
    )

def make_muon_pog_LooseIso_2015CD():
    return MuonPOGCorrectionIso2D(
        _DATA_FILES['2015CD']['Iso'],
        "MC_NUM_LooseRelIso_DEN_LooseID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_LooseRelIso_DEN_MediumID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_LooseRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
    )
def make_muon_pog_MediumIso_2015CD():
    return MuonPOGCorrectionIso2D(
        _DATA_FILES['2015CD']['Iso'],
        "MC_NUM_MediumRelIso_DEN_LooseID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_MediumRelIso_DEN_MediumID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_MediumRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
    )
def make_muon_pog_TightIso_2015CD():
    return MuonPOGCorrectionIso2D(
        _DATA_FILES['2015CD']['Iso'],
        "MC_NUM_TightRelIso_DEN_LooseID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_TightRelIso_DEN_MediumID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_TightRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
    )



def make_muon_pog_PFTight_2016B():
    ''' Make PFTight DATA/MC corrector for 2012 '''
    return MuonPOGCorrection2D(
        _DATA_FILES['2016B']['PFID'],
        "MC_NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio"
    )

#def make_muon_pog_PFMedium_2016B():
#    ''' Make PFTight DATA/MC corrector for 2012 '''
#    return MuonPOGCorrection2D(
#        _DATA_FILES['2016B']['PFID'],
#        "MC_NUM_MediumID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio"
#    )

def make_muon_pog_PFLoose_2016B():
    return MuonPOGCorrection2D(
        _DATA_FILES['2016B']['PFID'],
        "MC_NUM_LooseID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio"
    )
def make_muon_pog_Tracking_2016B():
    return MuonPOGCorrectioneta(
        _DATA_FILES['2016B']['Tracking'],
        "mutrksfptg10"
    )

def make_muon_pog_TriggerIso22_2016B():
    return MuonPOGTriggerCorrection(
        _DATA_FILES['2016B']['TrggerIso22']
    )

def make_muon_pog_LooseIso_2016B():
    return MuonPOGCorrectionIso2D(
        _DATA_FILES['2016B']['Iso'],
        "MC_NUM_LooseRelIso_DEN_LooseID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_LooseRelIso_DEN_MediumID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_LooseRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
    )

#def make_muon_pog_MediumIso_2016B():
#    return MuonPOGCorrectionIso2D(
#        _DATA_FILES['2016B']['Iso'],
#        "MC_NUM_MediumRelIso_DEN_LooseID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
#        "MC_NUM_MediumRelIso_DEN_MediumID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
#        "MC_NUM_MediumRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
#    )

def make_muon_pog_TightIso_2016B():
    return MuonPOGCorrectionIso2D(
        _DATA_FILES['2016B']['Iso'],
        "MC_NUM_TightRelIso_DEN_LooseID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_TightRelIso_DEN_MediumID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
        "MC_NUM_TightRelIso_DEN_TightID_PAR_pt_spliteta_bin1/pt_abseta_ratio",
    )





def make_muon_pog_PFRelIsoDB012_2012():
    return BetterMuonPOGCorrection(
        _DATA_FILES['2012ReReco']['Iso'],
        [(0.9, 'DATA_over_MC_combRelIsoPF04dBeta<012_Tight_pt_abseta<0.9'   ),
         (1.2, 'DATA_over_MC_combRelIsoPF04dBeta<012_Tight_pt_abseta0.9-1.2'),
         (2.1, 'DATA_over_MC_combRelIsoPF04dBeta<012_Tight_pt_abseta1.2-2.1'), 
         (2.4, 'DATA_over_MC_combRelIsoPF04dBeta<012_Tight_pt_abseta2.1-2.4')], 
        'DATA_over_MC_combRelIsoPF04dBeta<012_Tight_eta_pt20-500'
    )


def make_muon_pog_PFRelIsoDB012_2012ABCD():
    ''' Make PFTight DATA/MC corrector for 2012 '''
    return MuonPOGCorrection3R(
        _DATA_FILES['2012ABCD'],
        "DATA_over_MC_combRelIsoPF04dBeta<012_Tight_pt_abseta<0.9_2012ABCD",
        "DATA_over_MC_combRelIsoPF04dBeta<012_Tight_pt_abseta0.9-1.2_2012ABCD",
        "DATA_over_MC_combRelIsoPF04dBeta<012_Tight_pt_abseta1.2-2.1_2012ABCD",
        "DATA_over_MC_combRelIsoPF04dBeta<012_Tight_eta_pt20-500_2012ABCD",
    )



def make_muon_pog_PFRelIsoDB02_2012():
    return MuonPOGCorrection(
        _DATA_FILES['2012'],
        'DATA/MC_combRelIsoPF04dBeta<02_Tight_pt_abseta<1.2',
        'DATA/MC_combRelIsoPF04dBeta<02_Tight_pt_abseta>1.2',
        'DATA/MC_combRelIsoPF04dBeta<02_Tight_eta_pt20-100',
    )

def make_muon_pog_PFRelIsoDB02_2011():
    return MuonPOG2011Combiner(
        MuonPOGCorrection(
            _DATA_FILES['2011'],
            'DATA/MC_combRelPFISO20_2011A_pt__abseta<1.2',
            'DATA/MC_combRelPFISO20_2011A_pt__abseta>1.2',
            'DATA/MC_combRelPFISO20_2011A_eta__pt>20',
        ),
        MuonPOGCorrection(
            _DATA_FILES['2011'],
            'DATA/MC_combRelPFISO20_2011B_pt__abseta<1.2',
            'DATA/MC_combRelPFISO20_2011B_pt__abseta>1.2',
            'DATA/MC_combRelPFISO20_2011B_eta__pt>20',
        ),
    )

def make_muon_pog_PFRelIsoDB012_2011():
    return MuonPOG2011Combiner(
        MuonPOGCorrection(
            _DATA_FILES['2011'],
            'DATA/MC_combRelPFISO12_2011A_pt__abseta<1.2',
            'DATA/MC_combRelPFISO12_2011A_pt__abseta>1.2',
            'DATA/MC_combRelPFISO12_2011A_eta__pt>20',
        ),
        MuonPOGCorrection(
            _DATA_FILES['2011'],
            'DATA/MC_combRelPFISO12_2011B_pt__abseta<1.2',
            'DATA/MC_combRelPFISO12_2011B_pt__abseta>1.2',
            'DATA/MC_combRelPFISO12_2011B_eta__pt>20',
        ),
    )


# These are only measured in 2012
def make_muon_pog_Mu17Mu8_Mu17_2012():
    return MuonPOGCorrection(
        _DATA_FILES['2012'],
        'DATA/MC_DoubleMu17Mu8_Mu17_Tight_pt_abseta<1.2',
        'DATA/MC_DoubleMu17Mu8_Mu17_Tight_pt_abseta>1.2',
        'DATA/MC_DoubleMu17Mu8_Mu17_Tight_eta_pt20-100',
    )
def make_muon_pog_Mu17Mu8_Mu8_2012():
    return MuonPOGCorrection(
        _DATA_FILES['2012'],
        'DATA/MC_DoubleMu17Mu8_Mu8_Tight_pt_abseta<1.2',
        'DATA/MC_DoubleMu17Mu8_Mu8_Tight_pt_abseta>1.2',
        'DATA/MC_DoubleMu17Mu8_Mu8_Tight_eta_pt20-100',
    )

def make_muon_pog_IsoMu24eta2p1_2012_early():
    return MuonPOGCorrection(
        _DATA_FILES['2012'],
        'DATA/MC_IsoMu24_eta2p1_TightIso_pt_abseta<1.2',
        'DATA/MC_IsoMu24_eta2p1_TightIso_pt_abseta>1.2',
        'DATA/MC_IsoMu24_eta2p1_TightIso_abseta_pt26-100',
        pt_thr = 26,
    )

def make_muon_pog_IsoMu24eta2p1_2012():
   # Taking into account the Muon Pt Dependence of the trigger until 26, from then on assuming eta dependence 
   # To accont for the turn on. That value could be adjusted 
    return MuonPOGCorrection3R(
        _DATA_FILES['2012ReReco']['SingleMuTrg'],
        'IsoMu24_eta2p1_DATA_over_MC_TightID_IsodB_PT_ABSETA_Barrel_0to0p9_pt25-500_2012ABCD',
        'IsoMu24_eta2p1_DATA_over_MC_TightID_IsodB_PT_ABSETA_Transition_0p9to1p2_pt25-500_2012ABCD', 
        'IsoMu24_eta2p1_DATA_over_MC_TightID_IsodB_PT_ABSETA_Endcaps_1p2to2p1_pt25-500_2012ABCD',
        'IsoMu24_eta2p1_DATA_over_MC_TightID_IsodB_ETA_0to0p9_0p9to1p2_1p2to2p1_pt25-500_2012ABCD',
        pt_thr = 25,
    )

def make_muon_pog_IsoMu20oIsoTkMu20_2015():
    return MuonPOGCorrectionTrig2D_weighted(
            _DATA_FILES['2015CD']['Trigger'],
            ["runD_IsoMu20_OR_IsoTkMu20_HLTv4p2_PtEtaBins/pt_abseta_ratio","runD_IsoMu20_OR_IsoTkMu20_HLTv4p3_PtEtaBins/pt_abseta_ratio"]
        )



class MuonPOGCorrection(object):
    '''

Muon POG corrections are generally by eta dependent for pt > 20,
and pt dependent for pt < 20, split by barrel and endcap.

'''

    def __init__(self, file, pt_barrel, pt_endcap, eta_pt20, abs_eta=False, pt_thr=20):
        self.filename = file
        self.file = ROOT.TFile.Open(file)
        self.abs_eta = abs_eta
        self.pt_thr = pt_thr

        # Map the functions to the appropriate TGraphAsymmErrors
        self.correct_by_pt_barrel = self.load_graph_eval_func(pt_barrel)
        self.correct_by_pt_endcap = self.load_graph_eval_func(pt_endcap)
        self.correct_by_eta_pt20 = self.load_graph_eval_func(eta_pt20)

    def load_graph_eval_func(self, name):
        ''' Load a graph with a given name form the file '''
        key = self.file.GetKey(name)
        if not key:
            raise IOError("Object with name %s d.n.e. in file %s" %
                          (name, self.filename))
        obj = key.ReadObj()
        if not obj:
            raise IOError("Object with key name %s d.n.e. can't be read" % name)
        return obj.Eval

    def __call__(self, pt, eta):
        if pt < self.pt_thr:
            if abs(eta) < 1.2:
                return self.correct_by_pt_barrel(pt)
            else:
                return self.correct_by_pt_endcap(pt)
        else:
            if self.abs_eta:
                eta = abs(eta)
            return self.correct_by_eta_pt20(eta)


class BetterMuonPOGCorrection(object):
    '''

Muon POG corrections are generally by eta dependent for pt > 20,
and pt dependent for pt < 20, split by barrel and endcap. Accepts any number of segmentation

'''

    def __init__(self, file, pt_corections, eta_correction, pt_thr=20, abs_eta=False):
        self.filename = file
        self.file = ROOT.TFile.Open(file)
        self.abs_eta = abs_eta
        self.pt_thr = pt_thr

        # Map the functions to the appropriate TGraphAsymmErrors
        self.correct_by_pt = [(thr, self.load_graph_eval_func(graph_name)) 
                              for thr, graph_name in pt_corections]
        self.correct_by_eta= self.load_graph_eval_func(eta_correction)

    def load_graph_eval_func(self, name):
        ''' Load a graph with a given name form the file '''
        key = self.file.GetKey(name)
        if not key:
            raise IOError("Object with name %s d.n.e. in file %s" %
                          (name, self.filename))
        obj = key.ReadObj()
        if not obj:
            raise IOError("Object with key name %s d.n.e. can't be read" % name)
        return obj.Eval

    def __call__(self, pt, eta):
        if pt < self.pt_thr:
            for thr, correction in self.correct_by_pt:
                if abs(eta) < thr:
                    return correction(pt)
        else:
            compute_eta = eta
            if self.abs_eta:
                compute_eta = abs(eta)
            return self.correct_by_eta(compute_eta)



class MuonPOGCorrection3R(object):
    '''

    Muon POG corrections are generally by eta dependent for pt > 20,
    and pt dependent for pt < 20, split by barrel, overlap and endcap.

    '''

    def __init__(self, file, pt_barrel, pt_overlap, pt_endcap, eta_pt20, pt_thr=20):
        self.filename = file
        self.file = ROOT.TFile.Open(file)
        self.pt_thr  = pt_thr

        # Map the functions to the appropriate TGraphAsymmErrors
        self.correct_by_pt_barrel = self.load_graph_eval_func(pt_barrel)
        self.correct_by_pt_overlap = self.load_graph_eval_func(pt_overlap)
        self.correct_by_pt_endcap = self.load_graph_eval_func(pt_endcap)
        self.correct_by_eta_pt20 = self.load_graph_eval_func(eta_pt20)

    def load_graph_eval_func(self, name):
        ''' Load a graph with a given name form the file '''
        key = self.file.GetKey(name)
        if not key:
            raise IOError("Object with name %s d.n.e. in file %s" %
                          (name, self.filename))
        obj = key.ReadObj()
        if not obj:
            raise IOError("Object with key name %s d.n.e. can't be read" % name)
        return obj.Eval

    def __call__(self, pt, eta):

        if pt < self.pt_thr:
            if abs(eta) < 0.9:
                return self.correct_by_pt_barrel(pt)
            elif abs(eta)<1.2:
                return self.correct_by_pt_overlap(pt)
            elif abs(eta) >= 1.2:
                return self.correct_by_pt_endcap(pt)
        else:
            return self.correct_by_eta_pt20(eta)

class MuonPOGCorrection2D(object):
    '''

    Muon POG corrections are generally by eta dependent for pt > 20,
    and pt dependent for pt < 20, split by barrel, overlap and endcap.

    '''

    def __init__(self, file, pt_abseta):
        self.filename = file
        self.file = ROOT.TFile.Open(file)
        #self.pt_thr  = pt_thr
        self.histopath = pt_abseta
        self.correct_by_pt_abseta = {}

    def __call__(self, pt, eta):
        if pt >= 120: pt = 115.
        if pt < 20. : pt = 20.
        key = self.file.Get(self.histopath)
        self.correct_by_pt_abseta =key.GetBinContent(key.FindFixBin(pt, eta))
        #print 'Mu ID/Tr correction :', pt, eta,  self.correct_by_pt_abseta
        return self.correct_by_pt_abseta


class MuonPOGCorrectioneta(object):
    '''

    Muon POG corrections are generally by eta dependent for pt > 20,
    and pt dependent for pt < 20, split by barrel, overlap and endcap.

    '''

    def __init__(self, file, etahist):
        self.filename = file
        self.file = ROOT.TFile.Open(file)
        #self.pt_thr  = pt_thr
        self.histopath =etahist
        self.correct_by_eta = {}

    def __call__(self,eta):
        if eta>= 2.4: eta =2.234  #read the average number from the root file
        if eta <= -2.4 : eta =-2.231 
        key = self.file.Get(self.histopath)
        self.correct_by_eta =key.GetBinContent(key.FindFixBin(eta))
        #print 'Mu ID/Tr correction :', pt, eta,  self.correct_by_pt_abseta
        return self.correct_by_eta


class MuonPOGTriggerCorrection(object):
    '''

    Muon POG corrections are generally by eta dependent for pt > 20,
    and pt dependent for pt < 20, split by barrel, overlap and endcap.

    '''

    def __init__(self, file):
        self.filename = file
        self.fileIn = ROOT.TFile.Open(file)
        self.pt_thr  =0
        #self.histopath =etahist
        self.correct_by_eta_pt = {}
        self.HistoBaseName = "ZMass"
        self.nEtaBins=0
        self.etaBinsH=self.fileIn.Get("etaBinsH")
        self.eff_data={}
        self.eff_mc={}
    def __call__(self,pt,eta):
        self.nEtaBins = self.etaBinsH.GetNbinsX()
        for iBin in range(0,self.nEtaBins):
            etaLabel = self.etaBinsH.GetXaxis().GetBinLabel(iBin+1)
            GraphName = self.HistoBaseName+etaLabel+"_Data"
            self.eff_data[etaLabel] = self.fileIn.Get(GraphName)
            self.SetAxisBins(self.eff_data[etaLabel])
#            GraphName = self.HistoBaseName+etaLabel+"_MC" 
            #self.eff_mc[etaLabel] = self.fileIn.Get(GraphName)
            #self.SetAxisBins(self.eff_mc[etaLabel])
#            sameBinning = self.check_SameBinning(self.eff_data[etaLabel], self.eff_mc[etaLabel])
#            if not sameBinning:
#                 print "ERROR in ScaleFactor::init_ScaleFactor(TString inputRootFile)"
        effciency=self.get_EfficiencyData(pt,eta) 
#        print "efficiency is   %f " %effciency
        return effciency            
    
    def SetAxisBins(self,graph):
        NPOINTS = graph.GetN()
        AXISBINS=array.array('f',[]) 
        #AXISBINS [NPOINTS+1] =[]
        for i in range(0,NPOINTS):
            AXISBINS.append(graph.GetX()[i] - graph.GetErrorXlow(i))
        AXISBINS.append(graph.GetX()[NPOINTS-1] + graph.GetErrorXhigh(NPOINTS-1))
        graph.GetXaxis().Set(NPOINTS, AXISBINS)
    def FindEtaLabel(self,Eta):
        Eta = abs(Eta)
        binNumber = self.etaBinsH.GetXaxis().FindFixBin(Eta) 
        EtaLabel = self.etaBinsH.GetXaxis().GetBinLabel(binNumber)
      #  it={}
   #     it =  self.eff_data.find(EtaLabel)
   #     if it==self.eff_data.end():
   #         print " no object corresponding to eta label"
   #     else:
     #   print "Etalable is ******"
     #   print EtaLabel
        return EtaLabel



    def get_EfficiencyData(self,pt,eta):

        label = self.FindEtaLabel(eta)
        ptbin = self.FindPtBin(self.eff_data[label],pt)
#        print "the ptbin for this is %f and the pt is%f  and eta is %f" %(ptbin,pt,eta)
        if ptbin==-99:
            eff=1
        else :
            eff = self.eff_data[label].GetY()[ptbin-1]
         #   print "the efficiency is %f"  %eff
        if eff>1.0:
            print "Returned efficiency in data > 1"
        if eff<0.0:
            print "Returned negative efficiency in data" 
        return eff
    def FindPtBin(self,eff_data,Pt):
        Npoints = eff_data.GetN()
        ptMAX = (eff_data.GetX()[Npoints-1])+(eff_data.GetErrorXhigh(Npoints-1))
        ptMIN = (eff_data.GetX()[0])-(eff_data.GetErrorXlow(0))
        if Pt>=ptMAX:
           print "bigger"
           return Npoints
        elif Pt<ptMIN:
           print "pT too low"
           return -99
        else:
           return eff_data.GetXaxis().FindFixBin(Pt)
   

    def check_SameBinning(self,graph1,graph2):       
        haveSameBins = False
        n1 = graph1.GetXaxis().GetNbins()
        n2 = graph2.GetXaxis().GetNbins()
        if n1!=n2:
           return false
        else:
           haveSameBins = True
           nbins = n1
           for i in range(0, nbins):
               x1 = (graph1.GetXaxis().GetXbins()).GetArray()[i]
               x2 = (graph2.GetXaxis().GetXbins()).GetArray()[i]
               haveSameBins = haveSameBins and (x1== x2)
        return haveSameBins
class MuonPOGCorrectionTrig2D_weighted(object):
    '''

    Muon POG corrections are generally by eta dependent for pt > 20,
    and pt dependent for pt < 20, split by barrel, overlap and endcap.
    
    Call to this returns the trigger corrections weighted by luminosity
    ( Two hlt paths *4p2(Run2015D,upto 257933) and  *4p3(run 257933-260627) )    
    
    '''

    def __init__(self, file, pt_abseta):
        self.filename = file
        self.file = ROOT.TFile.Open(file)
        #self.pt_thr  = pt_thr
        self.histopath_4p2 = pt_abseta[0]
        self.histopath_4p3 = pt_abseta[1]
        self.correct_by_pt_abseta_4p3 = {}
        self.correct_by_pt_abseta_4p2 = {}
        self.correct_by_pt_abseta_weighted = {}

    def __call__(self, pt, eta):
        if pt >= 120: pt = 115.
        if pt < 20. : pt = 20.
        key_4p2 = self.file.Get(self.histopath_4p2)
        key_4p3 = self.file.Get(self.histopath_4p3)
        self.correct_by_pt_abseta_4p2 =key_4p2.GetBinContent(key_4p2.FindFixBin(pt, eta))
        self.correct_by_pt_abseta_4p3 =key_4p3.GetBinContent(key_4p3.FindFixBin(pt, eta))
        self.correct_by_pt_abseta_weighted =(1.899*self.correct_by_pt_abseta_4p3+0.401*self.correct_by_pt_abseta_4p2)/2.3
        return self.correct_by_pt_abseta_weighted

class MuonPOGCorrectionIso2D(object):
    def __init__(self, file, IDLoose, IDMedium, IDTight):
        self.filename = file
        self.file = ROOT.TFile.Open(file)
        #self.pt_thr  = pt_thr
        self.histopathLOOSE = IDLoose
        self.histopathMEDIUM= IDMedium
        self.histopathTIGHT = IDTight
        self.correct_by_pt_abseta = {}
 
    def __call__(self, mid, pt, eta):
        if pt >= 120: pt = 115.
        if pt < 20. : pt = 20.
        if mid == 'Tight':
             key = self.file.Get(self.histopathTIGHT)
             self.correct_by_pt_abseta =key.GetBinContent(key.FindFixBin(pt, eta))
            
        if mid == 'Medium':
             key = self.file.Get(self.histopathMEDIUM)
             self.correct_by_pt_abseta =key.GetBinContent(key.FindFixBin(pt, eta))
            

        if mid == 'Loose':
             key = self.file.Get(self.histopathLOOSE)
             self.correct_by_pt_abseta =key.GetBinContent(key.FindFixBin(pt, eta))

        #print 'Mu Iso correction :', pt, eta,  self.correct_by_pt_abseta 
        return self.correct_by_pt_abseta 





class MuonPOG2011Combiner(object):
    ''' They provide 2011 A and B separate, we have to combine them '''
    def __init__(self, corrector2011A, corrector2011B):
        self.corrA = corrector2011A
        self.corrB = corrector2011B

    def __call__(self, pt, eta):
        # Weighted average, by int. lumi
        return self.corrA(pt, eta)*(2.1/4.6) + \
                self.corrB(pt, eta)*(2.5/4.6)



class MuonPOG2012Combiner(object):
    ''' They provide 2012 A, B, C, D separate, we have to combine them '''
    def __init__(self, corrector2012A, corrector2012B, corrector2012C, corrector2012D):
        self.corrA = corrector2012A
        self.corrB = corrector2012B
        self.corrC = corrector2012C
        self.corrD = corrector2012D

    def __call__(self, pt, eta):
        # Weighted average, by int. lumi
        return self.corrA(pt, eta)*(1./19.) + self.corrB(pt, eta)*(4./19.) + self.corrC(pt, eta)*(6./19.) + self.corrD(pt, eta)*(8./19.)
                # CHECK THE NUMBERS!!! - Lumi split by ranges just a guess right now


if __name__ == "__main__":
    make_muon_pog_PFTight_2011()
    make_muon_pog_PFTight_2012()
    #make_muon_pog_PFTight_2015CD()
    #make_muon_pog_PFMedium_2015CD()
    #make_muon_pog_PFLoose_2015CD()
    make_muon_pog_PFRelIsoDB012_2012()
    make_muon_pog_PFRelIsoDB02_2012()
    make_muon_pog_PFRelIsoDB02_2011()
    make_muon_pog_PFRelIsoDB012_2011()
    #make_muon_pog_TightIso_2015CD()
    #make_muon_pog_MediumIso_2015CD()
    #make_muon_pog_LooseIso_2015CD()
    make_muon_pog_Mu17Mu8_Mu17_2012()
    make_muon_pog_Mu17Mu8_Mu8_2012()
    make_muon_pog_IsoMu24eta2p1_2012()
    #make_muon_pog_IsoMu20oIsoTkMu20_2015()
