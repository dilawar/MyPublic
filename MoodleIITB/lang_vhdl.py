import re
import io
import glob, os, subprocess, sys

class VHDL:

    def __init__(self):
        self.tbname = ''
        self.component = dict()
        self.component_expr = u''
        self.port = dict()
        self.src = ''
        self.srcDir = ''

    def dirName(self, dir):
        self.srcDir = dir

    def compile_testbench(self, dir, cxx):
        '''
        This function compiles the test_bench in given directory.
        
        '''
        os.chdir(dir)
        files = glob.glob('*.vhd')
        for file in files:
                f = open(file, "r")
                if f:
                    try:
                        self.src = f.read()
                    except EOFError:
                        print "EOF"
                    if not self.src: break
                    # This will match the testbech entity in given file.
                    m = re.search(r"entity\ +(\w+)\ +is[\ \n]+end\ +(\w*)\ *\w*[;]", self.src, re.I)
                    if m : 
                        test_bench = m.group(1)
                        self.tbname = test_bench
                        self.get_ports(test_bench, self.src);
                        self.create_testbench(self.component, self.port)

                        print("Compiling entity {0} using {1}".format(test_bench, cxx))
                        #print("In file {0}".format(f.name))
                        #print "cxx : {0}".format(cxx)
                        if cxx == 'ghdl':
                            vcdOption = "--vcd="+test_bench+".vcd"
                            subprocess.call(["ghdl", "-a", f.name] \
                                    , stdout=subprocess.PIPE)
                            subprocess.call(["ghdl", "-m", test_bench] \
                                    , stdout=subprocess.PIPE)
                            subprocess.call(["ghdl", "-r" \
                                    , test_bench, "--stop-time=1000ns" \
                                    , vcdOption] \
                                    , stdout=subprocess.PIPE)
                        elif cxx == 'vsim' :
                            pass

                    else : 
                        pass

    def get_ports(self, test_bench, data):
        print "Getting port information for {0} in file {1}".format(test_bench, file)
        m = re.search(r'''component\s+(\w+)\s*(is)*\s+
                port\s*[(]
                ((\s*\w+(\s*[,]\s*\w+\s*)*\s*[:]\s*
                (in|out)\s*\w+\s*([(]\s*\d+\s*\w+\s*\d+\s*[)])*\s*[;]*)*)
                \s*[)]\s*[;]
                \s+end\s+component\s*\w*[;]'''
                , data, re.I | re.VERBOSE)

        if m:
            text = m.group(3)
            self.component_expr = text
            self.component[m.group(1)] = text
            for pExpr in text.split(';'):
                if pExpr.strip() == '':
                    pass
                else:
                    [p, expr] = pExpr.split(':')
                    p = p.strip()
                    temp = expr.split()
                    type = temp[0].strip()
                    del temp[0]
                    for i in p.split(','):
                        expr = ' '.join(temp)
                        self.port[(i, m.group(1))] = (type, (expr))
        
        else:
            print ("Can not find any component in this file.")



    def create_testbench(self, component, port):
        '''
        This function create a testbench 
        '''
        for comp_name, comp_expr in self.component.iteritems():
            self.tb = io.StringIO()
            self.tb.write(u'''
-- This testbench is automatically generated using a python
-- script.
-- (c) Dilawar Singh, dilawar@ee.iitb.ac.in
--
LIBRARY IEEE;
USE IEEE.std_logic_1164.all;
USE STD.textio.all;
USE WORK.all;

ENTITY testbench IS 
end ENTITY testbench;

ARCHITECTURE stimulus OF testbench IS\n\tCOMPONENT ''')
            self.tb.write(unicode(comp_name)+u'\n')
            self.tb.write(u'\tPORT ( \n')
            self.tb.write(u'\t'+unicode(comp_expr)+u';\n')
            self.tb.write(u'\t);\nEND COMPONENT;\n')

            # Attach signal.
            for (name,comp), (a, expr) in self.port.iteritems():
                if comp == comp_name :
                    self.tb.write(u'\tSIGNAL '+unicode(name)+u' : '+unicode(expr))
                    self.tb.write(u';\n')
                else:
                    pass

            self.tb.write(u'BEGIN\n')
            self.tb.write(u'\tdut : '+unicode(comp_name)+u' \n\tPORT MAP (');

            for (name, comp), (a, expr) in self.port.iteritems():
                if comp == comp_name :
                    self.tb.write(unicode(name)+u', ')
                else:
                    pass
        
            
            pos = self.tb.tell()
            self.tb.seek(pos-2)
            self.tb.write(u' );\n')
            self.tb.write(u'\n\ttest : PROCESS \n')

            # Create variables.
            for (name,comp), (a, expr) in self.port.iteritems():
                if comp == comp_name :
                    self.tb.write(u'\t\tVARIABLE var_'+unicode(name.strip())+u' : '+unicode(expr))
                    self.tb.write(u';\n')
                else:
                    pass

            self.tb.write(u'\n\t\tfile vector_file : text is in \"'\
                    +unicode(self.tbname)+u'.txt\";\n')
            self.tb.write(u'''
\t\tVARIABLE l : LINE;
\t\tVARIABLE vector_time : TIME;
\t\tVARIABLE r : REAL;
\t\tVARIABLE good_number, good_val : BOOLEAN;
\t\tVARIABLE space : CHARACTER;
                    ''')

            self.tb.write(u'''
\t\tBEGIN
\t\tWHILE NOT endfile(vector_file) LOOP
\t\t\treadline(vector_file, l);
\t\t\tread(l, r, good => good_number);
\t\t\tNEXT WHEN NOT good_number;
\t\t\tvector_time := r * 1 ns;
\t\t\tIF (now < vector_time) THEN
\t\t\t\tWAIT FOR vector_time - now;
\t\t\tEND IF;
\t\t\tread(l, space);\n''')
            # read other variables and use them as input.
            for (name,comp), (a, expr) in self.port.iteritems():
                if comp == comp_name :
                    self.tb.write(u'\t\t\tread(l, var_'+unicode(name.strip())+\
                            u', good_val);\n') 
                    self.tb.write(u'\t\t\tASSERT good_val REPORT \"bad '+\
                            unicode(name)+u' value\"\n;')
                else:
                    pass
            # Assign these values to input ports.
            for (name,comp), (type, expr) in self.port.iteritems():
                if comp == comp_name :
                    if type.strip() == 'in' :
                        self.tb.write(u'\t\t\t'+unicode(name)+u' <= var_'+\
                                unicode(name.strip())+u';\n')
                else:
                    pass

            # ASSERT OUTPUT ports.
            for (name,comp), (type, expr) in self.port.iteritems():
                if comp == comp_name :
                    if type.strip() == 'out' :
                        self.tb.write(u'\t\t\tASSERT var_'+unicode(name.strip())+\
                                u' = '+unicode(name.strip())+\
                                u' REPORT \"vector mismatch\"'+\
                                u' SEVERITY WARNING;\n')
                else:
                    pass

            self.tb.write(u'\t\tEND LOOP;\n')
            self.tb.write(u'\t\tASSERT false REPORT \"Test complete\";\n')
            self.tb.write(u'\t\tWAIT;\n')
            self.tb.write(u'\t\tEND PROCESS;\n')
            self.tb.write(u'\tEND ARCHITECTURE;\n')
            if not os.path.isdir('./AUTO_GEN'):
                os.makedirs('./AUTO_GEN')
            tb_file = open("./AUTO_GEN/auto_"+self.tbname+".vhd", "w");
            tb_file.write(self.tb.getvalue())


