"""
REPORTING MODULE FOR COP VERIFICATION

This module provides tools for generating reports from
COP verification results.
"""

import os
import json
import datetime
from typing import List, Dict, Any, Set, Optional

def generate_verification_report(violations, covered_components, contexts=None, output_path=None, format="markdown"):
    """
    Generate a verification report from collected data.
    
    Args:
        violations: List of verification violations
        covered_components: Set of components covered by tests
        contexts: Optional list of context records
        output_path: Optional path to write the report
        format: Output format (markdown, json, html)
        
    Returns:
        str: The generated report
    """
    if format == "markdown":
        report = _generate_markdown_report(violations, covered_components, contexts)
    elif format == "json":
        report = _generate_json_report(violations, covered_components, contexts)
    elif format == "html":
        report = _generate_html_report(violations, covered_components, contexts)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)
    
    return report

def _generate_markdown_report(violations, covered_components, contexts):
    """Generate a Markdown verification report."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        "# COP Verification Report",
        f"Generated: {now}\n",
        "## Summary",
        f"- Components tested: {len(covered_components)}",
        f"- Violations found: {len(violations)}",
    ]
    
    if contexts:
        # Count contexts by type
        context_counts = {}
        for ctx in contexts:
            ctx_type = ctx.annotation_type.__name__
            if ctx_type not in context_counts:
                context_counts[ctx_type] = 0
            context_counts[ctx_type] += 1
        
        lines.append("- Context annotations:")
        for ctx_type, count in context_counts.items():
            lines.append(f"  - {ctx_type}: {count}")
    
    if violations:
        lines.append("\n## Violations")
        
        # Group violations by type
        by_type = {}
        for violation in violations:
            v_type = violation.get("type", "unknown")
            if v_type not in by_type:
                by_type[v_type] = []
            by_type[v_type].append(violation)
        
        for v_type, v_list in by_type.items():
            lines.append(f"\n### {v_type.title()} Violations")
            
            for i, violation in enumerate(v_list, 1):
                component = violation.get("component", "unknown")
                component_name = (
                    component.__name__ if hasattr(component, "__name__") 
                    else str(component)
                )
                test = violation.get("test", "unknown")
                details = violation.get("details", "No details provided")
                
                lines.append(f"\n**Violation {i}: {component_name}**")
                lines.append(f"- Test: {test}")
                lines.append(f"- Details: {details}")
    
    if contexts:
        lines.append("\n## Context Coverage")
        
        # Group contexts by file
        by_file = {}
        for ctx in contexts:
            source_info = ctx.source_info or {}
            file_path = source_info.get("file", "unknown")
            
            if file_path not in by_file:
                by_file[file_path] = []
                
            by_file[file_path].append(ctx)
        
        for file_path, file_contexts in by_file.items():
            file_name = os.path.basename(file_path)
            lines.append(f"\n### {file_name}")
            
            # Group by annotation type
            by_type = {}
            for ctx in file_contexts:
                ctx_type = ctx.annotation_type.__name__
                if ctx_type not in by_type:
                    by_type[ctx_type] = []
                by_type[ctx_type].append(ctx)
            
            for ctx_type, ctx_list in by_type.items():
                lines.append(f"\n#### {ctx_type}")
                for ctx in ctx_list:
                    source_info = ctx.source_info or {}
                    line_no = source_info.get("line", "unknown")
                    function = source_info.get("function", "unknown")
                    
                    # Extract additional context-specific info
                    details = []
                    if hasattr(ctx.annotation_instance, "status"):
                        details.append(f"status={ctx.annotation_instance.status}")
                    if hasattr(ctx.annotation_instance, "description"):
                        details.append(f"description=\"{ctx.annotation_instance.description}\"")
                    if hasattr(ctx.annotation_instance, "severity"):
                        details.append(f"severity={ctx.annotation_instance.severity}")
                    
                    details_str = ", ".join(details)
                    if details_str:
                        details_str = f" ({details_str})"
                    
                    lines.append(f"- Line {line_no}, in {function}{details_str}")
    
    return "\n".join(lines)

def _generate_json_report(violations, covered_components, contexts):
    """Generate a JSON verification report."""
    # Convert sets to lists for JSON serialization
    covered = list(str(c) for c in covered_components)
    
    # Convert context objects to dictionaries
    context_data = []
    if contexts:
        for ctx in contexts:
            context_dict = {
                "type": ctx.annotation_type.__name__,
                "source_info": ctx.source_info,
                "start_time": ctx.start_time,
                "end_time": ctx.end_time,
                "duration": ctx.duration()
            }
            
            # Add annotation-specific attributes
            for attr in dir(ctx.annotation_instance):
                if not attr.startswith("_") and attr not in ("args", "kwargs"):
                    try:
                        value = getattr(ctx.annotation_instance, attr)
                        # Only include serializable values
                        if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                            context_dict[attr] = value
                    except:
                        pass
            
            context_data.append(context_dict)
    
    report = {
        "generated": datetime.datetime.now().isoformat(),
        "summary": {
            "components_tested": len(covered_components),
            "violations_found": len(violations)
        },
        "violations": violations,
        "covered_components": covered,
        "contexts": context_data
    }
    
    return json.dumps(report, indent=2)

def _generate_html_report(violations, covered_components, contexts):
    """Generate an HTML verification report."""
    # Convert markdown to HTML
    markdown = _generate_markdown_report(violations, covered_components, contexts)
    
    try:
        import markdown as md
        html_body = md.markdown(markdown)
    except ImportError:
        # Fallback to simple HTML conversion
        html_body = markdown.replace("\n", "<br>")
    
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>COP Verification Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #444; margin-top: 20px; }}
            h3 {{ color: #555; }}
            .violation {{ background-color: #fff0f0; padding: 10px; margin: 10px 0; border-left: 3px solid #f00; }}
            .context {{ background-color: #f0f8ff; padding: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    return html

def generate_security_report(contexts, security_tests, output_path=None):
    """
    Generate a security-focused report.
    
    Args:
        contexts: List of context records
        security_tests: Dictionary mapping components to security test results
        output_path: Optional path to write the report
        
    Returns:
        str: The generated report
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        "# COP Security Verification Report",
        f"Generated: {now}\n",
        "## Security Risk Summary"
    ]
    
    # Extract security risks from contexts
    security_risks = []
    for ctx in contexts:
        if ctx.annotation_type.__name__ == "security_risk":
            security_risks.append({
                "description": getattr(ctx.annotation_instance, "description", "Unknown"),
                "severity": getattr(ctx.annotation_instance, "severity", "UNKNOWN"),
                "source_info": ctx.source_info
            })
    
    # Count risks by severity
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    for risk in security_risks:
        severity = risk["severity"]
        if severity in severity_counts:
            severity_counts[severity] += 1
        else:
            severity_counts["UNKNOWN"] += 1
    
    # Add severity counts to report
    lines.append("Risks by severity:")
    for severity, count in severity_counts.items():
        if count > 0:
            lines.append(f"- {severity}: {count}")
    
    lines.append("\n## Security Risks")
    
    # Group risks by severity
    by_severity = {}
    for risk in security_risks:
        severity = risk["severity"]
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(risk)
    
    # Sort severities in order of importance
    for severity in ["HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
        if severity in by_severity:
            lines.append(f"\n### {severity} Severity Risks")
            
            for risk in by_severity[severity]:
                source = risk["source_info"] or {}
                file_name = os.path.basename(source.get("file", "unknown"))
                line_no = source.get("line", "unknown")
                function = source.get("function", "unknown")
                
                lines.append(f"\n**{risk['description']}**")
                lines.append(f"- Location: {file_name}, line {line_no}, in {function}")
                
                # Add test coverage information if available
                component_key = f"{file_name}:{function}"
                if component_key in security_tests:
                    test_info = security_tests[component_key]
                    if test_info.get("covered", False):
                        lines.append(f"- Test Coverage: ✅ YES")
                        if "test_name" in test_info:
                            lines.append(f"  - Test: {test_info['test_name']}")
                    else:
                        lines.append(f"- Test Coverage: ❌ NO")
                else:
                    lines.append(f"- Test Coverage: ❓ UNKNOWN")
    
    report = "\n".join(lines)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)
    
    return report
