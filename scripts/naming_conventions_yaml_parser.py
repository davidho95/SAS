'''
This is an experimental prototype that generates naming convention checkers from a .yaml file. Currently the templates
used to identify the object being checked are stored in /afs/cern.ch/user/d/daho/yaml/templates.

David Ho
August 2016
'''

import yaml
import argparse
import os
import datetime
import re

class ConventionReader(object):
    """Reader class"""
    def __init__(self, yamlfile):
        super(ConventionReader, self).__init__()
        self.yamlfile = yamlfile
        self.rules = {}
        self.project_name = ""
        self.known_clang_types= {
            "Function": "FunctionDecl",
            "Type": "TypeDecl",
            "DataMember": "FieldDecl",
            "Const": "VarDecl",
            "Enumerator": "EnumDecl",
            "Namespace": "NamespaceDecl"
        }
        self.template_directory = "/afs/cern.ch/user/d/daho/yaml/templates/identifiers"
        self.identifiers = {}
        for file in os.listdir(self.template_directory):
            file_name, file_extension = os.path.splitext(file)
            if file_extension == ".template":
                template_name = os.path.splitext(file_name)[0]
                with open(os.path.join(self.template_directory, file), "r") as fobj:
                    self.identifiers[template_name] = fobj.read()
        with open("/afs/cern.ch/user/d/daho/yaml/templates/DefaultIdentifier.template", "r") as fobj:
            self.default_template = fobj.read()

    def check(self, name, regex):
        # is the regex valid?
        try:
            re.compile(regex)
        except:
            print("Invalid regex for '{name}'; checker not written".format(name=name))
            return False
        # is there a known Clang type associated with the name?
        try:
            self.known_clang_types[name]
        except KeyError:
            print("Unable to find Clang type for '{name}'; checker not written".format(name=name))
            return False
        return True

    def read(self):
        with open(self.yamlfile, 'r') as yamlfile:
            content = yaml.load(yamlfile)
        if "project" in content.keys():
            self.project_name = content["project"]["name"]
            self.project_author = content["project"]["author"]
        if "conventions" in content.keys():
            conventions = content["conventions"]
            for convention_name in conventions.keys():
                name = conventions[convention_name]["name"]
                regex = conventions[convention_name]["regex"]
                desc = conventions[convention_name]["description"]
                if "clangType" in conventions[convention_name].keys():
                    self.known_clang_types[name] = conventions[convention_name]["clangType"]
                if self.check(name, regex):
                    clang_type = self.known_clang_types[name]
                    self.rules[name] = [regex, clang_type, desc]
                else: continue
                if not name in self.identifiers.keys():
                    print("No identifier template found for '{name}'; using default template".format(name=name))
                    self.identifiers[name] = self.default_template


if __name__ == "__main__":
    argparser = argparse.ArgumentParser("convention creator", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument("file_name", type=str, help=".yaml file containing checker details")
    argparser.add_argument("destination", type=str, help="where the checker classes are generated")
    args = argparser.parse_args()

    year = datetime.date.today().strftime("%Y")
    reader = ConventionReader(args.file_name)
    reader.read()

    with open(os.path.join(args.destination, "Rules.h"), "w") as fobj:
        for name in reader.rules.keys():
            fobj.write("#include \"{name}Checker.h\"\n".format(name=name))

    for name, attributes in reader.rules.iteritems():
        with open("/afs/cern.ch/user/d/daho/yaml/templates/CheckerBase.cpp.template", "r") as fobj:
            base_template = fobj.read()
        checker_code = base_template.format(author=reader.project_author,
            year=year,
            name=name,
            project=reader.project_name,
            regex=attributes[0],
            clang_type=attributes[1],
            report_description=attributes[2],
            identifier_code=reader.identifiers[name])
        with open("/afs/cern.ch/user/d/daho/yaml/templates/CheckerHeader.h.template", "r") as fobj:
            header_template = fobj.read()
        header_code = header_template.format(author=reader.project_author,
            year=year,
            name=name,
            name_caps=name.upper(),
            project=reader.project_name,
            clang_type=attributes[1],
            description=attributes[2])
        with open(os.path.join(args.destination, name + "Checker.cpp"), "w") as fobj:
            fobj.write(checker_code)
        with open(os.path.join(args.destination, name + "Checker.h"), "w") as fobj:
            fobj.write(header_code)
        print(name + " checker created.")