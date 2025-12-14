"""
Script to re-extract solutions from videos with focus on tables/grids.
This creates better dataset examples that include proper table-based solutions.
"""

import json
import os
from pathlib import Path
import httpx

# This script would re-process the draft files with a better extraction prompt
# that specifically asks for table-based solutions matching Gaurav Kapoor's style

IMPROVED_EXTRACTION_PROMPT = """
Extract the DILR puzzle solution from this video frame/transcript.

CRITICAL: The solution MUST include:
1. ASCII tables/grids showing the solving process
2. Step-by-step table creation and filling
3. Visual representations (tables, Venn diagrams, arrangement grids)
4. Complete methodology matching Gaurav Kapoor's teaching style

For each step, show the actual table/grid structure, not just descriptions.

Format the solution with:
- Initial table setup
- Step-by-step table filling
- Constraint application shown in tables
- Final solution table

Return JSON with: question, answer, solutions (direct, step_by_step with tables, intuitive, shortcut)
"""

# This would be integrated into the vision extraction pipeline
# For now, it's a reference for what needs to be done


