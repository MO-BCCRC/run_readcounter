'''
Created on Jun 17, 2014

@author: dgrewal
##tests for the count_component
'''

import unittest
import component_reqs, component_main
import subprocess
import os
from collections import defaultdict

class args():
    def __init__(self):
        self.bam = '/share/lustre/dgrewal/Miscellaneous/component_tests/test_bam/DG1136a_5Mbp.bam'
        self.w = '1000'
        self.q = '0'
        self.out = './component_test/outfile'


class check_requirements(unittest.TestCase):
    def setUp(self):
        self.args = args()
        
    def test_verify_reqs(self):
        #make sure that the required fields are present in reqs file
        try:
            _ = component_reqs.env_vars
            _ = component_reqs.parallel
            _ = component_reqs.requirements
        except:
            self.assertEqual(True, False, 'Please complete the requirements file')
        
    #make sure that the required fields are present in reqs file
    def __get_version_main(self):
        main_stream = open('component_main.py')
        for line in main_stream:
            if 'self.version' in line:
                return eval(line.strip().split('=')[1])
        return None

    def test_version(self):
        main_version = self.__get_version_main() 
        version = component_reqs.version
        
        self.assertNotEqual(main_version, None, 'Could not retrieve the version from component_main')
        self.assertEqual(main_version, version, 'the version in component_main and component_reqs did not match') 

    #make sure that the required fields are present in reqs file
    def test_verify_reqs(self):
        try:
            _ = component_reqs.env_vars
            _ = component_reqs.interval_file
            _ = component_reqs.memory
            _ = component_reqs.parallel
            _ = component_reqs.parallel_params
            _ = component_reqs.requirements
            _ = component_reqs.version
            _ = component_reqs.seed_version
        except:
            self.assertEqual(True, False, 'Please complete the requirements file')
        
        try:
            _ = component_reqs.parallel_run
            self.assertEqual(True, False, 'The parallel_run option must be called parallel in compoenent')
        except:
            pass
        try:
            _ = component_reqs.parallel_mode
            self.assertEqual(True, False, 'The parallel_mode option has been removed')
        except:
            pass

    def test_component(self):
        component = component_main.Component()
        component.args = self.args
        component.run()

        import filecmp
        filecmp.cmp('./component_test/outfile', './component_test/outfile_ref')

        os.remove(self.args.out)


    def test_verify_python(self):
        #The python version must be atleast 2.7.0
        #get the python version
        cmd = component_reqs.requirements['python'] + ' -V'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmdout, cmderr = proc.communicate()
        
        if cmdout=='' and cmderr == '':
            self.assertEqual(True, False, 'Couldn\'t retreive the version information')
        elif cmdout != '' and cmderr != '':
            err = cmdout + ' ' +cmderr
            self.assertEqual(True, False, 'Couldn\'t retreive the version information: '+err)
        elif cmdout == '':
            #delete Python from version info
            val = cmderr.strip().split()[1].split('.') 
        elif cmderr == '':
            #delete Python from version info
            val = cmderr.strip().split()[1].split('.')
                       
        self.assertGreaterEqual(int(val[0]), 2, 'The major version of python must be 2 or greater')
        if int(val[0])>2:
            return
        
        self.assertGreaterEqual(int(val[1]), 7, 'The minor version of python must be 7 or greater')
        if int(val[0])>7:
            return
        
        self.assertGreaterEqual(int(val[1]), 5, 'The patch version of python must be 5 or greater')

    def test_make_cmd(self):
        comp = component_main.Component()
        comp.args = self.args
        cmd,cmd_args = comp.make_cmd()
        cmd_args = ' '.join(map(str,cmd_args))
        
        #The actual resulting command:
        real_command =  os.path.abspath('./component_seed')+'/readCounter'
        real_command_args = '/share/lustre/dgrewal/Miscellaneous/component_tests/test_bam/DG1136a_5Mbp.bam'+\
                            ' -w1000'+' -q0'+' | '+component_reqs.requirements['python']+\
                            ' '+os.path.abspath('./component_seed')+'/filter_chromosomes.py'+\
                            ' ./component_test/outfile'
        
        #Ensure that the commands match exactly
        self.assertEqual(real_command, cmd, 'Please recheck the cmd variable in make_cmd')
        
        print cmd_args
        print real_command_args 
        #Ensure that each of the args are present in the command args list
        #Exact match not possible since order can change 
        self.assertEqual(real_command_args,cmd_args,'Please recheck the cmd_args list in make_cmd')
                
    def test_params(self):
        try:
            from component_params import input_files,input_params,output_files,return_value
        except:
            self.assertEqual(True,False,'Please complete the params file')
        
        try:
            import component_ui   
        except:
            #cannot run this test if running in unittest mode as ui isn't available
            self.assertEqual(True, True, '') 
            return
            
        arg_act = defaultdict(tuple)
        for val in component_ui.parser._actions[1:]:
            arg_act[val.dest] = (val.required,val.default)
            if val.required == None:
                self.assertEqual(val.default, None, 'The optional argument: '+ val.dest+' has no default value')
        
        #merge all the dictionaries together
        params_dict = dict(input_files.items() + input_params.items() + output_files.items())
        
        for dest,(req,default) in arg_act.iteritems():
            if req == True:
                self.assertEqual(params_dict[dest], '__REQUIRED__', 'params and ui dont match')
            else:
                if not params_dict[dest] in [default,None]:
                    self.assertEqual(True, False, 'Please ensure that either default or ' +\
                                     '__OPTIONAL__ flag is provided for: '+params_dict[dest]) 
        
 
    
def run():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    checkreqs = loader.loadTestsFromTestCase(check_requirements)
    
    suite.addTests(checkreqs)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
