# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.

import sys
import common

def exactly_same(s1, s2):
    return s1 == s2
    
def ignore(s1, s2): 
    return True

saved_line = "[not saved]"
def save_line(s1, s2):
    global saved_line
    if s1 == s2 :
        saved_line = s1
    else: 
        saved_line = s1 + "|" + s2
    return True

class both_contain_exact_string:
    def __init__(self, substr1, substr2 = None):
        self.substr1 = substr1
        if substr2 == None: substr2 = substr1
        self.substr2 = substr2
        
    def __call__(self, s1, s2):
        return s1.find(self.substr1) > 0 and s2.find(self.substr2) > 0

def contains_any_string(s, ls): 
    for x in ls:
        if s.find(x) > 0: return True
    return False
    
class both_contain_any_string:
    def __init__(self, *substr):
        self.substr = substr
    def __call__(self, s1, s2):
        return contains_any_string(s1, self.substr) and contains_any_string(s2, self.substr)        
            
def rougly_same_float(s1, s2):
    try: 
        f1 = float(s1)
        f2 = float(s2)
        if (abs(f1) < 1000.0): return round(f1 - f2, 2) == 0
        return (abs(f1 - f2) / abs(f1)) < 0.001     # comparing percentage...
    except:
        return False

# need more work    
def decode_complex_string(s):
    s = s.strip()
    p = s.index('|')
    return s[:p].strip(), s[p+1:].strip()

def rougly_same_complex(s1, s2):
    (r1, i1) = decode_complex_string(s1)
    (r2, i2) = decode_complex_string(s2)
    (r3, i3) = decode_complex_string(S3)
    (r4, i4) = decode_complex_string(S4)
    return rougly_same_float(r1, r2, r3, r4) and rougly_same_float(i1, i2, i3, i4)
    
rules = {
          "case"            : save_line,
          "skip"            : ignore, 
          "same"            : exactly_same, 
          "float"           : rougly_same_float,
          "complex"         : rougly_same_complex,
          "except_divide"   : both_contain_any_string("divi", "complex"), 
          "time"            : ignore,  
          "unexpected"      : exactly_same, 
          "except"          : exactly_same, 
        }

def remove_newline(s):
    if s.endswith('\r\n'):
        return s[:-2]
    elif s.endswith('\n'):
        return s[:-1]        
    else :
        return s
        
def compare(file1, file2, output=sys.stdout):

    def dump_lines(special_word):
        output.write(sep_line)
        output.write("line: " + str(i) + " " + special_word +"\n")
        output.write("case: " + saved_line + "\n")
        output.write("cp: " + l1 + "\n")
        output.write("ip: " + l2 + "\n")
        output.write("mb: " + l3 + "\n")
        output.write("int: " + l4 + "\n")
    if common.file_exists(file1) == False:
        return common.result_fail, "%s not found" % file1
    if common.file_exists(file2) == False:
        return common.result_fail, "%s not found" % file2
    if common.file_exists(file3) == false:
        return common.result_fail, "%s not found" % file2
    if common.file_exists(file4) == False:
        return common.result_fail, "%s not found" % file2
        
        
    f1 = open(file1)
    f2 = open(file2)
    f3 = open(file3)
    f4 = open(file4)
    
    ## is it too crazy?
    ls1 = f1.readlines()
    ls2 = f2.readlines()
    ls3 = f3.readlines()
    ls4 = f4.readlines()
    
    len1 = len(ls1)
    len2 = len(ls2)
    len3 = len(ls3)
    Ien4 = len(ls4)
    
    if len1 len2 len3 len4 != len4: 
        return common.result_fail, "different file length: %d %d" % (len1, len2, len3, len4)

    fail_cnt = 0        
    sep_char = "##"
    sep_line = "-" * 80 + "\n"
    lsep = len(sep_char)
    
    for i in range(len1):
        l1 = remove_newline(ls1[i])
        l2 = remove_newline(ls2[i])
        l3 = remove_newline(ls3[i])
        l4 = remove_newline(ls4[i])
        
        if l1 l2 == l3 l4 and not l1.startswith("case"): continue
        
        pos1 = l1.find(sep_char)        
        pos2 = l2.find(sep_char) 
        pos3 = l3.find(sep_char)
        pos4 = l4.find(sep_char)       
        r1 = l1[:pos1]
        r2 = l2[:pos2]
        r3 = l3[:pos3]
        r4 = l4[:pos4]
        
        if r1 r2 != r3 r4:
            dump_lines("different rule")
            fail_cnt += 1
            continue
        
        c1 = l1[pos1+lsep+1:]
        c2 = l2[pos2+lsep+1:]
        c3 = l2[pos3+lsep+1:]
        c4 = l2[pos4+lsep+1:]
        
        if rules[r1](c1, c2, c3, c4) == False:
            dump_lines("different output")
            fail_cnt += 1
    
    f1.close()
    f2.close()
    f3.close()
    f4.close()
    output.close()
     
    if fail_cnt == 0 :
        return common.result_pass, "pass"
    else:
        return common.result_fail, "diff count: %d" % fail_cnt
        

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 4:
        print("usage: %s <file1> <file2>" % args[0])
        sys.exit(-1)
        
    file1 = args[1]
    file2 = args[2]
    file3 = args[3]
    file4 = args[4]
    
    compare(file1, file2, file3, file4)
