// Author: David Ho (2016)

// Checks whether local variable names start with a lowercase letter

#ifndef SAS_CHECKERS_LocalVariableLowercase_H
#define SAS_CHECKERS_LocalVariableLowercase_H

#include "SasChecker.h"

namespace sas {
namespace CodingConventions {
namespace FCCSW {
class LocalVariableLowercaseTraits : public CommonCheckerTraits {
public:
  static constexpr const char* Name="sas.CodingConventions.FCCSW.LocalVariableLowercase";
  static constexpr const char* Description="Local variables names start with a lowercase letter.";
};

class LocalVariableLowercaseChecker : public SasChecker<LocalVariableLowercaseTraits,
                                                        clang::ento::check::ASTDecl<clang::VarDecl>> {
public:
  void checkASTDecl(const clang::VarDecl* D, 
                    clang::ento::AnalysisManager& Mgr, 
                    clang::ento::BugReporter& BR) const;
};
}
}
} // end namespace sas

#endif