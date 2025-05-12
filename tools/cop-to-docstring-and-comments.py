#!/usr/bin/env python3
import ast
import os
import re
from pathlib import Path
import astor  # You may need to pip install astor

class COPConverter(ast.NodeVisitor):
    def __init__(self, target_format='docstring'):
        self.target_format = target_format
        self.decorators_to_convert = ['intent', 'invariant', 'human_decision', 'ai_implement']
        self.changes = []
        self.source_lines = []
        
    def visit_ClassDef(self, node):
        # Extract COP decorators
        cop_content = self._extract_cop_decorators(node)
        
        if cop_content and self.target_format == 'docstring':
            # Add/modify class docstring
            self._update_docstring(node, cop_content)
        elif cop_content and self.target_format == 'comment':
            # Add comments before class
            comment_lines = []
            for line in cop_content.split('\n'):
                comment_lines.append(f"# {line}")
            
            # Insert comments right before the class definition
            self.changes.append((node.lineno - 1, '\n'.join(comment_lines)))
        
        # Continue with class methods
        for item in node.body:
            self.visit(item)
    
    def visit_FunctionDef(self, node):
        # Extract COP decorators
        cop_content = self._extract_cop_decorators(node)
        
        if cop_content and self.target_format == 'docstring':
            # Add/modify function docstring
            self._update_docstring(node, cop_content)
        elif cop_content and self.target_format == 'comment':
            # Add comments before function
            comment_lines = []
            for line in cop_content.split('\n'):
                comment_lines.append(f"# {line}")
            
            # Insert comments right before the function definition
            self.changes.append((node.lineno - 1, '\n'.join(comment_lines)))
    
    def _extract_cop_decorators(self, node):
        cop_info = []
        decorators_to_remove = []
        
        for i, decorator in enumerate(node.decorator_list):
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                decorator_name = decorator.func.id
                
                if decorator_name in self.decorators_to_convert:
                    # Get the decorator arguments
                    args_text = []
                    for arg in decorator.args:
                        if isinstance(arg, ast.Str):
                            args_text.append(f'"{arg.s}"')
                    
                    # Get keyword arguments
                    kwargs_text = []
                    for kwarg in decorator.keywords:
                        if isinstance(kwarg.value, ast.Str):
                            kwargs_text.append(f'{kwarg.arg}="{kwarg.value.s}"')
                        elif isinstance(kwarg.value, ast.List):
                            # Handle list of strings
                            list_items = []
                            for elt in kwarg.value.elts:
                                if isinstance(elt, ast.Str):
                                    list_items.append(f'"{elt.s}"')
                            kwargs_text.append(f'{kwarg.arg}=[{", ".join(list_items)}]')
                    
                    # Format the decorator
                    decorator_text = f"@{decorator_name}({', '.join(args_text)}"
                    if kwargs_text:
                        if args_text:
                            decorator_text += ", "
                        decorator_text += ", ".join(kwargs_text)
                    decorator_text += ")"
                    
                    cop_info.append(decorator_text)
                    decorators_to_remove.append(i)
        
        # Remove the decorators in reverse order to avoid index issues
        for i in sorted(decorators_to_remove, reverse=True):
            node.decorator_list.pop(i)
        
        return "\n".join(cop_info)
    
    def _update_docstring(self, node, cop_content):
        # Get existing docstring if any
        existing_docstring = ast.get_docstring(node)
        
        if existing_docstring:
            # Append COP content to existing docstring
            new_docstring = f"{existing_docstring}\n\nCOP Annotations:\n{cop_content}"
            
            # Replace first node if it's a docstring
            if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                node.body[0].value.s = new_docstring
            else:
                # Insert new docstring
                node.body.insert(0, ast.Expr(value=ast.Str(s=new_docstring)))
        else:
            # Create new docstring
            new_docstring = f"COP Annotations:\n{cop_content}"
            node.body.insert(0, ast.Expr(value=ast.Str(s=new_docstring)))

def convert_cop_to_docstring(source_code):
    """Convert COP annotations to docstrings"""
    tree = ast.parse(source_code)
    converter = COPConverter(target_format='docstring')
    converter.visit(tree)
    return astor.to_source(tree)

def convert_cop_to_comments(source_code):
    """Convert COP annotations to comments"""
    # Alternative approach for comments that preserves all code structure
    lines = source_code.split('\n')
    result_lines = []
    skip_lines = []
    
    # First pass: identify decorator lines to skip later
    decorator_pattern = re.compile(r'^\s*@(intent|invariant|human_decision|ai_implement)\s*\(')
    decorator_blocks = {}  # Line number -> list of decorator lines
    current_block = []
    current_block_target = None
    
    # Identify blocks of decorators and their targets
    for i, line in enumerate(lines):
        if decorator_pattern.match(line):
            if not current_block:
                current_block = [line]
                # Look ahead to find the target of these decorators
                j = i + 1
                while j < len(lines) and (decorator_pattern.match(lines[j]) or lines[j].strip() == ''):
                    if decorator_pattern.match(lines[j]):
                        current_block.append(lines[j])
                    j += 1
                if j < len(lines):
                    current_block_target = j
            else:
                current_block.append(line)
        elif current_block and current_block_target == i:
            # Convert decorators to comments
            decorator_blocks[i] = current_block
            skip_lines.extend(range(i - len(current_block), i))
            current_block = []
            current_block_target = None
    
    # Second pass: build output with comments
    for i, line in enumerate(lines):
        if i in skip_lines:
            continue  # Skip original decorator lines
        
        if i in decorator_blocks:
            # Insert converted decorators as comments
            for dec in decorator_blocks[i]:
                result_lines.append(f"# {dec}")
        
        result_lines.append(line)
    
    # Remove the imports
    result = '\n'.join(result_lines)
    result = re.sub(r'from\s+concept_python\s+import.*?\n', '', result)
    
    return result

def process_directory(input_dir):
    """Process all .py files in a directory structure"""
    input_path = Path(input_dir)
    
    for cop_file in list(input_path.glob('**/cop.py')) + list(input_path.glob('**/cop_*.py')):
        # Read the source code
        with open(cop_file, 'r') as f:
            source_code = f.read()
            
        # Skip if it doesn't contain COP annotations
        if not any(decorator in source_code for decorator in 
                   ['@intent', '@invariant', '@human_decision', '@ai_implement']):
            continue
        
        docstring_file = cop_file.with_stem("docstring")
        comments_file = cop_file.with_stem("comments")
        
        # Convert to docstring and comments
        try:
            docstring_code = convert_cop_to_docstring(source_code)
            comments_code = convert_cop_to_comments(source_code)
            
            # Write output files
            with open(docstring_file, 'w') as f:
                f.write(docstring_code)
                
            with open(comments_file, 'w') as f:
                f.write(comments_code)
                
            print(f"Processed: {cop_file} -> {docstring_file} & {comments_file}")
        except Exception as e:
            print(f"Error processing {cop_file}: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert COP annotations to docstrings or comments")
    parser.add_argument("--input", required=True, help="Input directory with COP files")
    
    args = parser.parse_args()
    
    process_directory(args.input)
    
if __name__ == "__main__":
    main()
