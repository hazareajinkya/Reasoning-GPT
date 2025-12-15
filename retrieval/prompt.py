SYSTEM_PROMPT = (
    "You are a CAT DILR expert following Gaurav Kapoor's teaching methodology. "
    "Your solutions MUST be educational and teach students HOW to approach and solve problems step-by-step. "
    "CRITICAL: The step_by_step solution MUST follow this EXACT format:\n"
    "1. 📊 TABLE 1: DATA EXTRACTION [ASCII table]\n"
    "   EXPLANATION: [3-5 sentences explaining what was extracted]\n"
    "2. 📊 TABLE 2: INITIAL LOGIC APPLICATION [ASCII table with progression]\n"
    "   EXPLANATION: [3-5 sentences explaining the logic applied]\n"
    "3. 📊 TABLE 3: PROGRESSIVE DEDUCTION [ASCII table with more filled cells]\n"
    "   EXPLANATION: [3-5 sentences explaining deductions made]\n"
    "4. 📊 TABLE 4: INTERMEDIATE STATE [ASCII table partially filled]\n"
    "   EXPLANATION: [3-5 sentences explaining current state and next steps]\n"
    "5. 📊 TABLE 5: FINAL SOLUTION [Complete ASCII table]\n"
    "   FINAL EXPLANATION: [2-3 sentences verifying solution]\n\n"
    "RULES:\n"
    "- Table 1: Fill ALL given information from the question (do not leave cells empty if question states them)\n"
    "- Tables 2-5: Each MUST show MORE filled cells than the previous table\n"
    "- DO NOT jump to conclusions - build up incrementally\n"
    "- DO NOT repeat the same table - each must show visible progress\n"
    "- After EACH table, write 'EXPLANATION:' followed by 3-5 sentences\n"
    "- Explanations must explain: WHAT logic, WHY it was applied, HOW it filled specific cells\n"
    "- Use proper ASCII tables with | and +--- characters\n"
    "- Do NOT use escaped characters like \\n - use actual newlines\n"
    "- Tables and explanations are MANDATORY - both must be present\n"
    "- Use all 5 tables effectively - do not rush to final answer\n"
    "- NEVER show a table without a detailed explanation BEFORE or AFTER it\n"
    "- ALWAYS provide context and reasoning BEFORE jumping to visual representations\n"
    "- If you show a pie chart, bar chart, or diagram, explain WHAT it represents and WHY it's useful FIRST\n\n"
    "Return four outputs: 1) direct answer, 2) detailed step_by_step with 4-5 progressive tables AND explanations, "
    "3) simplest intuitive approach, 4) shortcut/exam hack. "
    "Always show HOW to solve using visual aids (tables, grids, Venn diagrams) in text format. "
    "Match the exact methodology from the reference examples provided. "
    "Be thorough and educational - students should learn the approach, not just see the answer."
)


def build_user_prompt(question: str, contexts: list[dict], max_context_length: int = 5000) -> str:
    """
    Build user prompt with retrieved contexts.
    Truncates contexts if too long to save tokens.
    Increased max_context_length to allow more reference examples for better learning.
    """
    import json
    ctx_txt = []
    total_length = 0
    
    for ctx in contexts:
        solutions = ctx.get('solutions', {})
        # Truncate long solutions to save tokens while keeping key info
        # Increased limit to show more table examples
        step_by_step = solutions.get('step_by_step', '')
        if len(step_by_step) > 1200:  # Increased from 800 to show more table examples
            step_by_step = step_by_step[:1200] + "...[truncated for brevity]"
        
        ctx_entry = (
            f"Example {ctx.get('id', 'unknown')}:\n"
            f"Q: {ctx.get('question', '')[:200]}\n"  # Limit question length
            f"Direct: {solutions.get('direct', '')[:150]}\n"  # Limit direct answer
            f"Steps: {step_by_step}\n"
            f"Intuitive: {solutions.get('intuitive', '')[:200]}\n"  # Limit intuitive
            f"Shortcut: {solutions.get('shortcut', '')[:200]}\n"  # Limit shortcut
        )
        
        # Check if adding this context would exceed limit
        if total_length + len(ctx_entry) > max_context_length and ctx_txt:
            break
        
        ctx_txt.append(ctx_entry)
        total_length += len(ctx_entry)
    
    ctx_joined = "\n---\n".join(ctx_txt)
    
    return (
        "Solve this CAT DILR problem using Gaurav Kapoor's teaching methodology.\n"
        "CRITICAL REQUIREMENT: The step_by_step solution MUST follow this EXACT structure with 4-5 progressive tables:\n\n"
        "STRUCTURE (MUST FOLLOW - DO NOT JUMP TO CONCLUSIONS):\n\n"
        "📊 TABLE 1: DATA EXTRACTION (Fill ALL given information)\n"
        "- Extract EVERY piece of information directly stated in the question\n"
        "- Fill in ALL cells that can be filled from the question text itself\n"
        "- This table should have the MAXIMUM possible information from the question\n"
        "- Do NOT leave cells empty if the question explicitly states their values\n"
        "- Then write detailed explanation: List every fact, constraint, and data point extracted\n\n"
        "EXPLANATION: [3-5 sentences]\n"
        "Explain: What information was directly given? What constraints exist? What relationships are stated?\n"
        "Be thorough - list every single piece of information from the question.\n\n"
        "📊 TABLE 2: APPLY DIRECT CONSTRAINTS (First logical deductions)\n"
        "- Use the constraints from the question to fill in more cells\n"
        "- Apply the most straightforward constraints first (e.g., 'never', 'always', 'did not train during X-Y')\n"
        "- Fill in cells that can be directly deduced from constraints\n"
        "- This table should show MORE filled cells than Table 1\n"
        "- Show clear progression - more information than Table 1\n\n"
        "EXPLANATION: [3-5 sentences]\n"
        "Explain: Which specific constraint did you apply? How did it help fill these cells? What is the reasoning?\n"
        "Be specific: 'Constraint X states Y, therefore cell Z must be...'\n\n"
        "📊 TABLE 3: PROGRESSIVE DEDUCTION (Use relationships and logic)\n"
        "- Use relationships between entities (e.g., 'were never Gurubhai', 'were Gurubhai for X years')\n"
        "- Apply logical deductions based on what you know so far\n"
        "- Fill in more cells using the information from Tables 1 and 2\n"
        "- This table should show SIGNIFICANTLY MORE filled cells than Table 2\n"
        "- Show clear progression - build on previous tables\n\n"
        "EXPLANATION: [3-5 sentences]\n"
        "Explain: What relationships did you use? How did you combine information from previous steps?\n"
        "Show your thinking: 'Since A and B were never Gurubhai, and we know A is with Guru X in year Y, therefore...'\n\n"
        "📊 TABLE 4: INTERMEDIATE DEDUCTIONS (Continue building)\n"
        "- Continue applying logic and constraints\n"
        "- Use elimination and logical reasoning\n"
        "- Fill in more cells based on what cannot be true\n"
        "- This table should show MORE progress than Table 3\n"
        "- Do NOT jump to final answer - show intermediate state\n\n"
        "EXPLANATION: [3-5 sentences]\n"
        "Explain: What additional deductions did you make? What possibilities did you eliminate?\n"
        "Show your reasoning process step-by-step.\n\n"
        "📊 TABLE 5: FINAL SOLUTION (Complete the table)\n"
        "- Fill in remaining cells using all available information\n"
        "- Verify all constraints are satisfied\n"
        "- This should be the COMPLETE table with all answers\n"
        "- Show the final state with all cells filled\n\n"
        "FINAL EXPLANATION: [3-5 sentences]\n"
        "Summarize: How did you reach the final solution? Verify all constraints. Present the answers to the questions.\n\n"
        "CRITICAL RULES (MUST FOLLOW):\n"
        "- Each table MUST be clearly labeled with '📊 TABLE X: [NAME]'\n"
        "- Each table MUST show CLEAR PROGRESSION - more cells filled than the previous table\n"
        "- Table 1: Fill ALL given information from the question (do not leave cells empty if question states them)\n"
        "- Tables 2-5: Each must show MORE filled cells than the previous one\n"
        "- DO NOT jump to conclusions - build up incrementally\n"
        "- DO NOT repeat the same table - each must show visible progress\n"
        "- BEFORE showing any table, chart, or diagram, you MUST provide context explaining:\n"
        "  * What information you're about to organize\n"
        "  * Why you're creating this visual representation\n"
        "  * What you expect to learn from it\n"
        "- After EACH table, you MUST write 'EXPLANATION:' followed by detailed textual explanations (3-5 sentences minimum)\n"
        "- Explanations must explain: WHAT logic was applied, WHY it was applied, HOW it led to filling specific cells\n"
        "- Be specific in explanations: mention exact constraints, relationships, and reasoning\n"
        "- NEVER show a final table or chart without first explaining the reasoning that led to it\n"
        "- If you show a pie chart or bar chart, explain what it represents and why it's useful BEFORE showing it\n"
        "- Tables must use proper ASCII format with | and +--- characters\n"
        "- DO NOT use Python arrays, dicts, JSON, or any code format like: tables: [{'table': '...'}]\n"
        "- DO NOT use any format other than plain ASCII text with | and + characters\n"
        "- Write tables directly as plain text, NOT as code or data structures\n"
        "- The explanations are MANDATORY - they teach students the reasoning process\n"
        "- Add blank lines between tables and explanations for readability\n"
        "- Use all 5 tables effectively - do not rush to the final answer\n"
        "- REMEMBER: Students need to understand the THINKING PROCESS, not just see the final result\n\n"
        "EXAMPLE FORMAT (write EXACTLY like this, as plain text):\n"
        "📊 TABLE 1: DATA EXTRACTION\n"
        "\n"
        "+------+------+------+\n"
        "|      | Col1 | Col2 |\n"
        "+------+------+------+\n"
        "| Row1 |  A   |  ?   |  <- Fill ALL given info\n"
        "| Row2 |  ?   |  B   |  <- Fill ALL given info\n"
        "+------+------+------+\n"
        "\n"
        "EXPLANATION: From the question, we extract the following information: [List EVERY fact]. Specifically, the question states that Row1-Col1 is A and Row2-Col2 is B. We also note constraints: [list all constraints]. This initial extraction gives us the foundation.\n\n"
        "📊 TABLE 2: APPLY DIRECT CONSTRAINTS\n"
        "\n"
        "+------+------+------+\n"
        "|      | Col1 | Col2 |\n"
        "+------+------+------+\n"
        "| Row1 |  A   |  X   |  <- More filled than Table 1\n"
        "| Row2 |  Y   |  B   |  <- More filled than Table 1\n"
        "+------+------+------+\n"
        "\n"
        "EXPLANATION: We apply constraint 1 which states [specific constraint]. This tells us that Row1-Col2 cannot be [value], so it must be X. Similarly, constraint 2 states [specific constraint], which means Row2-Col1 must be Y. This is the first logical deduction based on direct constraints.\n\n"
        "📊 TABLE 3: PROGRESSIVE DEDUCTION\n"
        "\n"
        "+------+------+------+\n"
        "|      | Col1 | Col2 |\n"
        "+------+------+------+\n"
        "| Row1 |  A   |  X   |\n"
        "| Row2 |  Y   |  B   |\n"
        "| Row3 |  Z   |  W   |  <- Even more filled\n"
        "+------+------+------+\n"
        "\n"
        "EXPLANATION: Now we use relationships. Since Row1 and Row2 have relationship R, and we know Row1-Col2 is X, we can deduce that Row3-Col1 must be Z because [specific reasoning]. This builds on the information from previous tables.\n\n"
        f"Reference examples:\n{ctx_joined}\n\n"
        f"Question:\n{question}\n\n"
        "CRITICAL: Return your response as JSON with keys: direct, step_by_step, intuitive, shortcut\n"
        "For step_by_step, write it as a PLAIN TEXT STRING containing:\n"
        "- 4-5 ASCII tables (using | and +--- characters, NOT arrays or dicts)\n"
        "- Explanations between each table (plain text, NOT code)\n"
        "- Do NOT use Python syntax like tables: [...] or {'table': '...'}\n"
        "- Write tables directly as ASCII art in the text, like the examples above\n"
        "The step_by_step field should be a single string containing all tables and explanations.\n"
        "Example of CORRECT format for step_by_step:\n"
        '\"📊 TABLE 1: DATA EXTRACTION\\n\\n+------+------+\\n| Col1 | Col2 |\\n+------+------+\\n|  ?   |  ?   |\\n+------+------+\\n\\nEXPLANATION: ...\"\n'
        "Example of WRONG format (DO NOT USE):\n"
        '\"tables: [{\\\"table\\\": \\\"+------+\\n| Col1 |\\n+------+\\\"}]\"\n'
        "Now solve this problem following the EXACT structure above."
    )


def json_block(obj: dict) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)

