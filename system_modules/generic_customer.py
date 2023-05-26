
# standard libs
import os
from abc import ABC, abstractmethod

# app modules
from system_modules import sys_utils
from system_modules import database_helper as pg_helper
from system_modules.message_logger import logger

if os.name == 'nt':
    VENV_BASE = os.environ['VIRTUAL_ENV']

    os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\fiona\\proj_data')
    os.environ['GDAL_DATA'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\fiona\\gdal_data')
    # os.environ["GDAL_DRIVER_PATH"] = os.path.join(GDAL_HOME, "gdal", "plugins")


# app modules
class Utility(ABC):
    def __init__(self, json_cfg, slug):
        self.cfg = json_cfg
        self.slug = slug
        pgdb = pg_helper.PostGISHelper()   # TODO take out of constructor
        engin =pgdb.connect()
        self.pgdb_engin = engin

        self.ov_layers = {}                 # holds the layername with bounds
        self.op_layers = {}
       
        # read the config file
        self.parse_cfg()

    def config_file(self):
        return self.cfg

    def pgdb_engin(self):
        return self.pgdb_engin

    def input_path(self):
        return self.input_path

    def customer_name(self):
        return self.customer_name

    def customer_id(self):
        return self.customer_id

    def customer_region(self):
        return self.customer_region

    def input_path(self):
        return self.input_path

    def output_path(self):
        return self.output_path

    def sld_outpath(self):
        return self.sld_outpath

    def input_types(self):
        return self.input_types

  
    def ov_layers(self):
        # dict[fc] = bbox
        return self.ov_layers
    
    
    def op_layers(self):
        # dict[fc] = bbox
        return self.op_layers


    def opsld_filenames(self):
        # dict[fc] = sldfilename
        self.opsld_filenames = {}
        # directory OUTPUT/SLD/slug/survey_name/layer.sld
        # output stylefile with the same name as the layer categorized by unique survey name
        for fc, geom,include,filter,legend in self.operations:
            stylefile = os.path.join(self.sld_outpath, self.slug + "_" + self.survey_name.lower() + "_" + fc.lower())
            self.opsld_filenames[fc] = stylefile + ".sld"    
        return self.opsld_filenames

    def survey_type_dict(self):
        return self.survey_type_dict

    def slug(self):
        return self.slug

    def survey_name(self):
        return self.survey_name

    def survey_copyright(self):
        return self.survey_copyright       


    def split_decoration(self, legend):
        # 
        # legends[("ControllableFitting", "Point")] = ["Legend:N", "Dialog:N", "Anno:SWGUID,"]
        # legend=no -> do not create legend, otherwise legend must exists or default legend
        # dialog=no -> do not create popup, otherwise go through all the prop
        # anno if empty, do not create textsymbole, otherwise textsymbol per anno
        style, dialog, anno = legend.split("|")
        sty = style.split(":")
        s = 0 if sty[1] == 'N' else 1            # 0 and 1 works better with javascript
        dia = dialog.split(":")
        d = 0 if dia[1] == 'N' else 1
        ann = anno.split(":") 
        a = ann[1][:-1].split(",") or []             # :-1 to remove the " when one anno
        decoration = [s,d,a]
        decoration_str = f"legend={s} dialog={d} annotation={a}" 
        return decoration, decoration_str


    def read_overlay_data(self):
        # this method should be invoked only after reading the config fie first - TODO: put error messaging
        input_path = self.input_path
        input_types = self.input_types
        overlay_list = self.overlays      # includes geometry type

        # local variable
        overlays = {}
        legends = {}
        msgs = ""

        # ["MHPSurvey", "Polygon", "All,", {"filter": "TODO"}, "Legend:N|Dialog:N|Anno:SWGUID,"] 
        # ["ControllableFitting", "Point", "INSTALLATI,MATERIAL,INSERVICED,SYMBOLROTA,PRESSURERA,SWGUID,FEATURETYP", {"filter": "TODO"}, "Legend:N|Dialog:N|Anno:SWGUID,"]
        for fc, geom,include,filter,legend in overlay_list:
            f = fc +".shp"
            # 
            decoration, decoration_str = self.split_decoration(legend)
            legends[(fc, geom)] = decoration             # list
            
            overlays[f] = (include.split(","), filter)   # tuple
            msg = f"    Readinging data for Overlay layer: {fc}\n"  
            msg += f"    With {geom} decoration {decoration_str}\n"
            msgs += msg
        
        return overlays, legends, msgs

        
    def read_operational_data(self):

        """Calling the customer generic class where this customer's configuration
        information, as determined by slug, is parsed and saved into this customer's object.

        Args:
            slugobj (object): an instance of this client's class

        Returns:
            operations: the dictionary of operational layer names as key and attributes, etc as values
            legends: the dictionary of the legends with layer name and geometry type as keys and
            other information as values, per layer
            msg: string of messages
        """

        operational_list = self.operations      # includes geometry type
        
        # local variable
        operationals = {}
        legends = {}
        msgs = ""

        #
        # we need to get the operational information to process the
        # data for this customer.
        #
        for fc, geom, include, filter,legend in operational_list:
            f = fc +".shp" 
            # 
            decoration, decoration_str = self.split_decoration(legend)
            legends[(fc, geom)] = decoration             # list

            operationals[f] = (include.split(","), filter)      # tuple
            msg = f"    Readinging data for Operational layer: {fc}\n"  
            msg += f"    With {geom} decoration {decoration_str}\n"
            msgs += msg

        return operationals, legends, msgs


    def parse_cfg(self):
        """This method is responsible for parsing contents of customer's
            configuration file. The query statements (filter) differs
            among customers but if passed as the complete sqlquery it
            should not matter. However, possibility of abstracting filter!!
            This method only parses keywords generically, other methods split
            things out into more detailed components
        """

        data_dict = sys_utils.load_customer_config(self.cfg)

        self.customer_name = data_dict["CUSTOMER_NAME"]
        self.customer_id = data_dict["CUSTOMER_ID"]
        self.customer_region = data_dict["CUSTOMER_REGION"]
        self.project_id = data_dict["PROJECT_ID"]
        self.input_path = data_dict["INPUT_PATH"]

        # this output path is customer's and differes from system output dir
        # as defined in sys.env. This absolut path needs to be checked and 
        # created if it does not exists here.
        output_path = data_dict["OUTPUT_PATH"]
        #
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
            msg = f"Creating customer's output path {output_path}\n"
            logger.info(msg)
        self.output_path = data_dict["OUTPUT_PATH"]

        # this SLD directory is where the program creates the dynamic slds
        # user's defined slds could go in INPUT, and the pre-processed slds
        # are under tenants/<slug>/sld
        #
        sld_outpath = os.path.join(output_path,"SLD")
        if not os.path.isdir(sld_outpath):
            os.makedirs(sld_outpath)
        self.sld_outpath = sld_outpath

        self.input_types = data_dict["INPUT_TYPES"]
        self.survey_copyright = data_dict["SURVEY_COPYRIGHT"]
        self.survey_name = data_dict["SURVEY_NAME"]   # used in naming packages and migration file names

        os.environ["OUTPUT_PATH"] = self.output_path  # for use in geoserver dbstore creation
        os.environ["SLD_OUTPATH"] = self.sld_outpath

        # asset_dic = data_dict["ASSETTYPES"]
        overlay_fcs = data_dict["Overlay"]
        self.overlays = overlay_fcs
        # logger.info(f"Overlays: {overlay_fcs}")
        operation_fcs = data_dict["Operational"]
        self.operations = operation_fcs
        # logger.info(f"Operation: {operation_fcs}")
        survey_dic = data_dict["SurveyTypes"]
        self.survey_type_dict = survey_dic
        # for key, values in survey_dic.items():
        #    logger.info(f"Survey: {key}\t{values}")

    
        
