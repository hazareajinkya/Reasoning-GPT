"""
Helper to generate ASCII tables for DILR problems based on problem structure.
Also includes chart/diagram generation capabilities.
"""

from retrieval.chart_generator import (
    generate_pie_chart_ascii,
    generate_bar_chart_ascii,
    generate_venn_diagram_ascii
)


def generate_table_for_problem(question: str, step_by_step: str) -> str:
    """
    Enhance step_by_step with tables if missing.
    Detects problem type and generates appropriate table structure.
    Now checks for multiple progressive tables (4-5 tables as per Gaurav Kapoor's methodology).
    
    IMPORTANT: This function should NOT interfere if the LLM already generated proper tables.
    Only add tables if completely missing.
    """
    question_lower = question.lower()
    step_lower = step_by_step.lower()
    
    # Count existing tables (look for table markers)
    table_count = step_by_step.count("+---") + step_by_step.count("+===")
    # Also check for explicit table markers like "TABLE 1", "Table 1", etc.
    import re
    table_markers = len(re.findall(r'(?i)(table\s*\d+|📊\s*table\s*\d+)', step_by_step))
    
    # Check for explanations between tables (look for "EXPLANATION" or paragraphs after tables)
    has_explanations = bool(re.search(r'(?i)(explanation|from the question|based on|we can|therefore|thus)', step_by_step))
    
    # If we have tables with markers AND explanations, trust the LLM output completely
    if table_markers >= 2 and has_explanations:
        return step_by_step  # LLM followed the format, don't interfere
    
    # If we have 4+ table separators, likely has multiple tables
    if table_count >= 4:
        return step_by_step  # Already has multiple progressive tables
    
    # If we have some tables but not enough, we might want to enhance
    # But for now, if LLM already generated some tables, trust it
    if "|" in step_by_step and ("---" in step_by_step or "+" in step_by_step):
        # Has some tables but maybe not enough - let's check if it follows the pattern
        # If it mentions "Table 1", "Table 2" etc., it's probably following the format
        if table_markers >= 2:
            return step_by_step  # Has progressive tables, just not all 5
    
    # No tables or insufficient tables - add a note
    # Note: The LLM should generate tables based on the enhanced prompts
    # This is just a fallback reminder
    if table_count == 0 and table_markers == 0:
        note = (
            "\n\n[NOTE: This solution should include 4-5 progressive tables showing: "
            "1) Data extraction, 2) Initial logic application, 3) Progressive deduction, "
            "4) Intermediate state, 5) Final solution. The LLM should generate these tables.]\n\n"
        )
        enhanced = step_by_step + note
    else:
        enhanced = step_by_step
    
    # Fallback: Add basic table structure if completely missing (rare case)
    # This should not be needed if prompts are working correctly
    if table_count == 0 and any(keyword in question_lower for keyword in ["table", "grid", "distribution", "assign", "allocate"]):
        table_header = "\n\n📊 TABLE 1: DATA EXTRACTION\n"
        table_header += "Extract all given information:\n"
        table_header += "+--------+--------+--------+--------+\n"
        table_header += "|        | Col1   | Col2   | Col3   |\n"
        table_header += "+--------+--------+--------+--------+\n"
        table_header += "| Row1   |   ?    |   ?    |   ?    |\n"
        table_header += "+--------+--------+--------+--------+\n"
        table_header += "| Row2   |   ?    |   ?    |   ?    |\n"
        table_header += "+--------+--------+--------+--------+\n"
        table_header += "| Row3   |   ?    |   ?    |   ?    |\n"
        table_header += "+--------+--------+--------+--------+\n\n"
        table_header += "Note: This is a basic template. The solution should show 4-5 progressive tables.\n\n"
        
        if not step_by_step.startswith("📊") and not step_by_step.startswith("TABLE"):
            enhanced = table_header + step_by_step
    
    # Circular arrangement problems
    elif any(keyword in question_lower for keyword in ["circular", "around", "table", "arrangement", "sitting"]):
        table_header = "\n\nStep 1: Create arrangement table (circular positions)\n"
        table_header += "Position:  12  1  2  3  4  5  6  7  8  9  10  11\n"
        table_header += "          (Top)                    (Bottom)\n"
        table_header += "Person:    ?   ?  ?  ?  ?  ?  ?  ?  ?  ?   ?   ?\n\n"
        table_header += "Fill positions based on constraints.\n\n"
        
        if "position" not in step_lower and "arrangement" not in step_lower:
            enhanced = table_header + step_by_step
    
    # Venn diagram problems
    elif any(keyword in question_lower for keyword in ["venn", "set", "overlap", "intersection", "union"]):
        table_header = "\n\nStep 1: Create Venn diagram structure\n"
        table_header += "Set A:     [        ]\n"
        table_header += "Set B:     [        ]\n"
        table_header += "Set C:     [        ]\n"
        table_header += "Overlap:   [  A∩B   ] [  B∩C   ] [  A∩C   ] [ A∩B∩C ]\n\n"
        table_header += "Fill in based on given information.\n\n"
        
        if "venn" not in step_lower and "set" not in step_lower:
            enhanced = table_header + step_by_step
    
    # Ranking/Ordering problems
    elif any(keyword in question_lower for keyword in ["rank", "order", "position", "first", "last", "before", "after"]):
        table_header = "\n\nStep 1: Create ranking table\n"
        table_header += "+--------+--------+--------+--------+--------+\n"
        table_header += "| Rank   | Person | Info   | Constraint |\n"
        table_header += "+--------+--------+--------+--------+--------+\n"
        table_header += "| 1st    |   ?    |        |            |\n"
        table_header += "+--------+--------+--------+--------+--------+\n"
        table_header += "| 2nd    |   ?    |        |            |\n"
        table_header += "+--------+--------+--------+--------+--------+\n"
        table_header += "| 3rd    |   ?    |        |            |\n"
        table_header += "+--------+--------+--------+--------+--------+\n\n"
        table_header += "Fill in rankings based on constraints.\n\n"
        
        if "rank" not in step_lower and "table" not in step_lower:
            enhanced = table_header + step_by_step
    
    return enhanced

