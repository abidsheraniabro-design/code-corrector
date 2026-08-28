import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class PythonCodeCorrector:
    """
    A comprehensive Python code correction tool that detects and fixes:
    - Syntax errors
    - Logic errors
    - Style/formatting issues
    - Common mistakes
    - Performance problems
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.corrections = []
    
    def read_file(self, filepath: str) -> str:
        """Read Python file and return content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found!")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    
    def check_syntax_errors(self, code: str) -> List[Dict]:
        """Check for syntax errors using AST parser."""
        syntax_issues = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            syntax_issues.append({
                'type': 'SyntaxError',
                'line': e.lineno,
                'message': e.msg,
                'text': e.text,
                'offset': e.offset
            })
        return syntax_issues
    
    def check_style_issues(self, code: str) -> List[Dict]:
        """Check for PEP 8 style violations and formatting issues."""
        style_issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length (PEP 8: max 79 chars)
            if len(line) > 79 and line.strip() and not line.strip().startswith('#'):
                style_issues.append({
                    'type': 'StyleWarning',
                    'line': i,
                    'message': f'Line too long ({len(line)} > 79 characters)',
                    'severity': 'warning'
                })
            
            # Check for trailing whitespace
            if line != line.rstrip():
                style_issues.append({
                    'type': 'StyleWarning',
                    'line': i,
                    'message': 'Trailing whitespace detected',
                    'severity': 'warning'
                })
            
            # Check for multiple spaces before comment
            if '  #' in line and not line.strip().startswith('#'):
                style_issues.append({
                    'type': 'StyleWarning',
                    'line': i,
                    'message': 'Multiple spaces before inline comment',
                    'severity': 'info'
                })
        
        return style_issues
    
    def check_logic_errors(self, code: str) -> List[Dict]:
        """Check for common logic errors."""
        logic_issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for comparison to None (should use 'is')
            if '==' in line and 'None' in line and 'is None' not in line:
                if re.search(r'==\s*None|None\s*==', line):
                    logic_issues.append({
                        'type': 'LogicError',
                        'line': i,
                        'message': "Use 'is None' instead of '== None'",
                        'suggestion': line.replace('== None', 'is None').replace('None ==', 'is not'),
                        'severity': 'error'
                    })
            
            # Check for comparison to True/False
            if ('== True' in line or '== False' in line) and not line.strip().startswith('#'):
                logic_issues.append({
                    'type': 'LogicError',
                    'line': i,
                    'message': "Avoid comparison to True/False, use 'if x:' or 'if not x:'",
                    'severity': 'warning'
                })
            
            # Check for bare except
            if line.strip() == 'except:':
                logic_issues.append({
                    'type': 'LogicError',
                    'line': i,
                    'message': "Bare 'except:' is too broad, specify exception type",
                    'suggestion': "except Exception as e:",
                    'severity': 'error'
                })
            
            # Check for mutable default arguments
            if 'def ' in line and ('=[]' in line or '={}' in line):
                logic_issues.append({
                    'type': 'LogicError',
                    'line': i,
                    'message': 'Mutable default argument detected (list or dict)',
                    'suggestion': 'Use None as default and initialize inside function',
                    'severity': 'error'
                })
        
        return logic_issues
    
    def check_performance_issues(self, code: str) -> List[Dict]:
        """Check for common performance problems."""
        perf_issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for string concatenation in loops
            if ('for ' in line or 'while ' in line) and ('+= ' in line or '+ ' in line) and '"' in line:
                # Simple heuristic
                if any(x in line for x in ['str', '"', "'"]):
                    perf_issues.append({
                        'type': 'PerformanceWarning',
                        'line': i,
                        'message': 'String concatenation in loop detected, use list and join()',
                        'severity': 'warning'
                    })
        
        return perf_issues
    
    def analyze_code(self, code: str) -> Dict:
        """Run all checks on the code."""
        results = {
            'syntax_errors': self.check_syntax_errors(code),
            'logic_errors': self.check_logic_errors(code),
            'style_issues': self.check_style_issues(code),
            'performance_issues': self.check_performance_issues(code)
        }
        return results
    
    def suggest_corrections(self, code: str, analysis: Dict) -> str:
        """Generate corrected code based on analysis."""
        corrected = code
        lines = corrected.split('\n')
        
        # Apply corrections
        for error in analysis['logic_errors']:
            if 'suggestion' in error:
                line_num = error['line'] - 1
                if line_num < len(lines):
                    lines[line_num] = error['suggestion']
        
        return '\n'.join(lines)
    
    def generate_report(self, filepath: str, code: str, analysis: Dict, corrected_code: str):
        """Generate a detailed correction report."""
        print("\n" + "="*70)
        print(f"PYTHON CODE CORRECTION REPORT")
        print(f"File: {filepath}")
        print("="*70)
        
        # Summary
        total_issues = (len(analysis['syntax_errors']) + 
                       len(analysis['logic_errors']) + 
                       len(analysis['style_issues']) + 
                       len(analysis['performance_issues']))
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Issues Found: {total_issues}")
        print(f"   - Syntax Errors: {len(analysis['syntax_errors'])}")
        print(f"   - Logic Errors: {len(analysis['logic_errors'])}")
        print(f"   - Style Issues: {len(analysis['style_issues'])}")
        print(f"   - Performance Issues: {len(analysis['performance_issues'])}")
        
        # Syntax Errors
        if analysis['syntax_errors']:
            print(f"\n❌ SYNTAX ERRORS ({len(analysis['syntax_errors'])}):")
            for error in analysis['syntax_errors']:
                print(f"   Line {error['line']}: {error['message']}")
                if error['text']:
                    print(f"   Code: {error['text'].strip()}")
        
        # Logic Errors
        if analysis['logic_errors']:
            print(f"\n⚠️  LOGIC ERRORS ({len(analysis['logic_errors'])}):")
            for error in analysis['logic_errors']:
                print(f"   Line {error['line']}: {error['message']}")
                if 'suggestion' in error:
                    print(f"   Suggestion: {error['suggestion']}")
        
        # Style Issues
        if analysis['style_issues']:
            print(f"\n📝 STYLE ISSUES ({len(analysis['style_issues'])}):")
            for error in analysis['style_issues'][:10]:  # Show first 10
                print(f"   Line {error['line']}: {error['message']}")
            if len(analysis['style_issues']) > 10:
                print(f"   ... and {len(analysis['style_issues']) - 10} more")
        
        # Performance Issues
        if analysis['performance_issues']:
            print(f"\n⚡ PERFORMANCE ISSUES ({len(analysis['performance_issues'])}):")
            for error in analysis['performance_issues']:
                print(f"   Line {error['line']}: {error['message']}")
        
        # Corrected Code
        print(f"\n✅ CORRECTED CODE:")
        print("-"*70)
        print(corrected_code)
        print("-"*70)
        print()
    
    def correct_file(self, filepath: str):
        """Main method to read, analyze, and correct a Python file."""
        print(f"🔍 Analyzing file: {filepath}")
        
        # Read file
        code = self.read_file(filepath)
        
        # Analyze
        analysis = self.analyze_code(code)
        
        # Generate corrections
        corrected_code = self.suggest_corrections(code, analysis)
        
        # Generate report
        self.generate_report(filepath, code, analysis, corrected_code)
        
        # Optionally save corrected code
        self.save_corrected_code(filepath, corrected_code)
    
    def save_corrected_code(self, filepath: str, corrected_code: str):
        """Optionally save the corrected code to a new file."""
        response = input("\n💾 Save corrected code? (y/n): ").strip().lower()
        if response == 'y':
            output_file = filepath.replace('.py', '_corrected.py')
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(corrected_code)
                print(f"✅ Corrected code saved to: {output_file}")
            except Exception as e:
                print(f"Error saving file: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python python_code_corrector.py <filepath>")
        print("Example: python python_code_corrector.py mycode.py")
        sys.exit(1)
    
    filepath = sys.argv[1]
    corrector = PythonCodeCorrector()
    corrector.correct_file(filepath)


if __name__ == "__main__":
    main()
