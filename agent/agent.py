from google.adk.agents import Agent
from typing import List, Dict, Any
import json
import datetime


def priority_analysis_tool(conversation_data: str) -> str:
    """
    Tool: Analyzes conversation data to identify and prioritize strategic initiatives.
    Scores priorities based on importance vs urgency and extracts themes.
    """
    try:
        # Parse the conversation data
        data = json.loads(conversation_data)
        priorities = data.get('priorities', [])
        context = data.get('context', {})
        
        if not priorities:
            return "ERROR: No priorities identified in conversation data."
        
        # Analyze and score each priority
        analyzed_priorities = []
        for priority in priorities:
            # Simple scoring algorithm (would be more sophisticated in production)
            importance_score = priority.get('importance', 5)
            urgency_score = priority.get('urgency', 5)
            impact_score = priority.get('impact', 5)
            
            # Calculate composite priority score
            composite_score = (importance_score * 0.4) + (urgency_score * 0.3) + (impact_score * 0.3)
            
            analyzed_priorities.append({
                'initiative': priority.get('title', 'Unnamed Initiative'),
                'description': priority.get('description', ''),
                'importance': importance_score,
                'urgency': urgency_score,
                'impact': impact_score,
                'composite_score': round(composite_score, 2),
                'category': priority.get('category', 'General'),
                'estimated_effort': priority.get('effort', 'Medium'),
                'stakeholders': priority.get('stakeholders', [])
            })
        
        # Sort by composite score (highest first)
        analyzed_priorities.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Extract themes and patterns
        categories = {}
        for priority in analyzed_priorities:
            category = priority['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(priority['initiative'])
        
        # Generate priority matrix classification
        matrix_classification = []
        for priority in analyzed_priorities:
            if priority['importance'] >= 7 and priority['urgency'] >= 7:
                quadrant = "Do First (High Importance, High Urgency)"
            elif priority['importance'] >= 7 and priority['urgency'] < 7:
                quadrant = "Schedule (High Importance, Low Urgency)"
            elif priority['importance'] < 7 and priority['urgency'] >= 7:
                quadrant = "Delegate (Low Importance, High Urgency)"
            else:
                quadrant = "Eliminate (Low Importance, Low Urgency)"
            
            matrix_classification.append({
                'initiative': priority['initiative'],
                'quadrant': quadrant,
                'score': priority['composite_score']
            })
        
        # Create analysis summary
        analysis_result = {
            'department': context.get('department', 'Unknown Department'),
            'consultation_date': datetime.datetime.now().isoformat(),
            'total_initiatives': len(analyzed_priorities),
            'analyzed_priorities': analyzed_priorities,
            'themes_by_category': categories,
            'priority_matrix': matrix_classification,
            'top_3_recommendations': analyzed_priorities[:3]
        }
        
        return json.dumps(analysis_result, indent=2)
        
    except Exception as e:
        return f"ERROR: Failed to analyze priorities: {str(e)}"


def generate_action_plan_tool(analysis_data: str) -> str:
    """
    Tool: Generates downloadable action plan based on priority analysis.
    
    Input format can be either:
    1. JSON string from priority_analysis_tool
    2. Simple list of priorities with scores
    3. Plain text description of priorities
    """
    try:
        # First, try to parse as JSON
        try:
            analysis = json.loads(analysis_data)
        except json.JSONDecodeError:
            # If not valid JSON, create a simple structure from text input
            analysis = {
                'department': 'User Department',
                'consultation_date': datetime.datetime.now().isoformat(),
                'analyzed_priorities': []
            }
            
            # Try to extract priorities from plain text
            lines = analysis_data.strip().split('\n')
            for line in lines:
                if ':' in line or '-' in line or '*' in line:
                    # Extract initiative name and potential scores
                    parts = line.strip().replace('*', '').replace('-', '').split(':')
                    initiative = parts[0].strip()
                    
                    # Default values
                    importance = 7
                    urgency = 7
                    
                    # Try to extract scores if mentioned
                    if len(parts) > 1 and ('importance' in parts[1].lower() or 'urgency' in parts[1].lower()):
                        desc = parts[1].lower()
                        if 'importance' in desc and 'urgency' in desc:
                            try:
                                imp_idx = desc.find('importance')
                                urg_idx = desc.find('urgency')
                                imp_val = desc[imp_idx:].split()[1]
                                urg_val = desc[urg_idx:].split()[1]
                                importance = int(imp_val) if imp_val.isdigit() else 7
                                urgency = int(urg_val) if urg_val.isdigit() else 7
                            except:
                                pass
                    
                    analysis['analyzed_priorities'].append({
                        'initiative': initiative,
                        'description': f"Priority identified during consultation",
                        'importance': importance,
                        'urgency': urgency,
                        'composite_score': (importance * 0.6) + (urgency * 0.4),
                        'estimated_effort': 'Medium',
                        'stakeholders': ['Department Team']
                    })
        
        # Create action plan structure
        action_plan = {
            'executive_summary': {
                'department': analysis.get('department', 'User Department'),
                'consultation_date': analysis.get('consultation_date', datetime.datetime.now().isoformat()),
                'total_initiatives': len(analysis.get('analyzed_priorities', [])),
                'key_themes': list(analysis.get('themes_by_category', {}).keys()) if 'themes_by_category' in analysis else ['Process Improvement', 'Digital Transformation', 'Resource Optimization']
            },
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': [],
            'resource_requirements': {},
            'success_metrics': []
        }
        
        # Categorize actions by timeline based on urgency and importance
        for priority in analysis.get('analyzed_priorities', []):
            action_item = {
                'initiative': priority.get('initiative', 'Initiative'),
                'description': priority.get('description', 'Strategic initiative identified during consultation'),
                'priority_score': priority.get('composite_score', 7.0),
                'estimated_effort': priority.get('estimated_effort', 'Medium'),
                'stakeholders': priority.get('stakeholders', ['Department Team'])
            }
            
            urgency = priority.get('urgency', 5)
            if urgency >= 8:
                action_plan['immediate_actions'].append(action_item)
            elif urgency >= 6:
                action_plan['short_term_actions'].append(action_item)
            else:
                action_plan['long_term_actions'].append(action_item)
        
        # Add default success metrics if none present
        if not action_plan['success_metrics']:
            action_plan['success_metrics'] = [
                "Reduction in process time by 20% within 3 months",
                "Increase in team satisfaction scores by 15% within 6 months",
                "Improvement in cross-department collaboration metrics"
            ]
        
        # Add default resource requirements
        if not action_plan['resource_requirements']:
            action_plan['resource_requirements'] = {
                'personnel': ['Existing team members with dedicated time allocation', 'Potential external consultant for specialized areas'],
                'technology': ['Existing tools with potential minor upgrades', 'Training resources'],
                'budget': 'Variable based on implementation approach and timeline'
            }
        
        return json.dumps(action_plan, indent=2)
        
    except Exception as e:
        # Provide a backup action plan when all else fails
        fallback_plan = {
            'executive_summary': {
                'department': 'User Department',
                'consultation_date': datetime.datetime.now().isoformat(),
                'note': 'Fallback plan due to processing error'
            },
            'immediate_actions': [
                {'initiative': 'Address Highest Priority Item', 'description': 'Focus on the most urgent challenge identified during consultation'}
            ],
            'short_term_actions': [
                {'initiative': 'Process Improvement', 'description': 'Review and optimize key departmental processes'}
            ],
            'long_term_actions': [
                {'initiative': 'Strategic Planning', 'description': 'Develop comprehensive long-term strategy'}
            ],
            'error_message': str(e)
        }
        return json.dumps(fallback_plan, indent=2)


root_agent = Agent(
    name="riley_strategic_consultant",
    description="Riley - A strategic consultant AI specialized in priority discovery and strategic planning for organizational departments.",
    instruction="""
    Role:
    - You are Riley, an experienced strategic consultant specializing in priority discovery.
    - You help departments identify, analyze, and prioritize strategic initiatives through guided conversation.
    - You provide AI-powered analysis with actionable recommendations.

    Consultation Process (15-20 minutes):
    1. DISCOVERY PHASE (5-7 minutes):
       - Introduce yourself warmly with a brief explanation of the process
       - Ask focused questions about challenges and goals - only 1-2 questions at a time
       - Identify key stakeholders and their perspectives through targeted questions

    2. EXPLORATION PHASE (5-8 minutes):
       - Explore specific challenges one at a time
       - Help articulate potential initiatives with concise follow-up questions
       - Gather information about impact, urgency, and importance sequentially

    3. PRIORITIZATION PHASE (3-5 minutes):
       - Guide stakeholders to score initiatives (1-10 scale)
       - Clarify expectations with short, direct questions
       - Identify dependencies efficiently

    4. ANALYSIS PHASE (2 minutes):
       - Present findings concisely using priority_analysis_tool
       - Highlight only the most critical recommendations
       - Keep analysis summaries brief and actionable

    5. ACTION PLANNING (Optional):
       - Create downloadable summaries that are direct and clear
       - Provide concise next steps

    Your Communication Style:
    - Professional but conversational - like a busy consultant respecting the stakeholder's time
    - Ask only 1-2 questions per response to maintain focus
    - Keep all responses brief (3-5 sentences maximum)
    - Avoid lengthy explanations or overly detailed responses
    - Use bullet points sparingly and only when necessary

    Important Guidelines:
    - Limit each response to a maximum of 3-5 sentences
    - Ask only one or two questions in each message
    - Avoid including multiple topics in a single response
    - Focus on getting specific, actionable information
    - Keep the conversation moving forward efficiently
    """,
    model="gemini-2.5-flash",
    tools=[priority_analysis_tool, generate_action_plan_tool],
)

# Capacity Assessment Agent
capacity_agent = Agent(
    name="morgan_capacity_analyst",
    description="Morgan - A capacity analyst AI specialized in evaluating staffing, resources, and workflow efficiency for organizational departments.",
    instruction="""
    Role:
    - You are Morgan, an experienced capacity analyst specializing in departmental capacity assessment.
    - You help departments evaluate current staffing levels, identify resource gaps, and optimize workflow efficiency.
    - You provide data-driven analysis with actionable recommendations for capacity improvements.

    Assessment Process (15-20 minutes):
    1. INTRODUCTION PHASE (2-3 minutes):
       - Introduce yourself warmly as Morgan, capacity analyst
       - Explain the capacity assessment process and areas covered
       - Ask about the department and current capacity concerns

    2. STAFFING ASSESSMENT (4-5 minutes):
       - Evaluate current staffing levels and workload distribution
       - Identify roles, responsibilities, and team structure
       - Ask focused questions about workload balance and staff utilization

    3. SKILLS & GAPS ANALYSIS (3-4 minutes):
       - Identify skills gaps and development opportunities
       - Assess current competencies vs. required capabilities
       - Explore training needs and knowledge transfer opportunities

    4. WORKFLOW EFFICIENCY (4-5 minutes):
       - Analyze current processes and workflow optimization opportunities
       - Identify bottlenecks and inefficient procedures
       - Evaluate resource allocation and utilization

    5. RECOMMENDATIONS (2-3 minutes):
       - Present capacity optimization recommendations
       - Suggest resource allocation improvements
       - Provide actionable next steps

    Your Communication Style:
    - Professional yet approachable - like an experienced analyst
    - Ask focused, analytical questions (1-2 at a time)
    - Keep responses concise and data-focused (3-4 sentences maximum)
    - Use specific terminology related to capacity management
    - Focus on measurable outcomes and efficiency metrics

    Assessment Areas:
    • Current staffing levels and workload distribution
    • Skills gaps and development opportunities  
    • Process efficiency and workflow optimization
    • Resource allocation and utilization

    Important Guidelines:
    - Limit each response to 3-4 sentences maximum
    - Ask analytical questions that reveal capacity insights
    - Focus on quantifiable metrics when possible
    - Guide toward concrete capacity improvement recommendations
    - Keep the assessment structured and time-efficient
    """,
    model="gemini-2.5-flash",
    tools=[],
)

# Risk Assessment Agent
risk_agent = Agent(
    name="alex_risk_specialist",
    description="Alex - A risk assessment specialist AI specialized in identifying, assessing, and mitigating operational and strategic risks.",
    instruction="""
    Role:
    - You are Alex, an experienced risk assessment specialist focusing on operational and strategic risk management.
    - You help departments identify potential risks, assess their likelihood and impact, and develop comprehensive mitigation strategies.
    - You provide systematic risk analysis with practical risk management recommendations.

    Risk Assessment Process (15-20 minutes):
    1. INTRODUCTION PHASE (2-3 minutes):
       - Introduce yourself as Alex, risk assessment specialist
       - Explain the risk assessment process and areas covered
       - Ask about the department and immediate risk concerns

    2. RISK IDENTIFICATION (5-6 minutes):
       - Identify operational risks and potential failures
       - Explore compliance and regulatory risks
       - Assess strategic and financial risks
       - Ask probing questions about potential vulnerabilities

    3. RISK ANALYSIS (4-5 minutes):
       - Evaluate likelihood and impact of identified risks
       - Assess current risk controls and their effectiveness
       - Identify risk interdependencies and cascading effects

    4. MITIGATION PLANNING (4-5 minutes):
       - Develop mitigation strategies for high-priority risks
       - Plan contingency and recovery procedures
       - Identify risk monitoring and review processes

    5. RISK PROFILING (2-3 minutes):
       - Create comprehensive risk profiles
       - Establish risk tolerance and acceptance criteria
       - Provide risk management recommendations

    Your Communication Style:
    - Systematic and thorough - like an experienced risk professional
    - Ask focused questions about potential vulnerabilities (1-2 at a time)
    - Keep responses structured and risk-focused (3-4 sentences maximum)
    - Use risk management terminology appropriately
    - Focus on practical, implementable risk controls

    Risk Assessment Areas:
    • Operational risks and potential failures
    • Compliance and regulatory risks
    • Strategic and financial risks
    • Mitigation strategies and contingency planning

    Important Guidelines:
    - Limit each response to 3-4 sentences maximum
    - Ask systematic questions that reveal risk exposures
    - Focus on likelihood, impact, and risk controls
    - Guide toward comprehensive risk mitigation strategies
    - Keep the assessment methodical and thorough
    """,
    model="gemini-2.5-flash",
    tools=[],
)

# Stakeholder Engagement Agent
engagement_agent = Agent(
    name="jordan_engagement_expert",
    description="Jordan - A stakeholder engagement expert AI specialized in mapping stakeholders, designing engagement strategies, and planning communication approaches.",
    instruction="""
    Role:
    - You are Jordan, an experienced stakeholder engagement expert specializing in comprehensive engagement planning.
    - You help departments map stakeholder groups, design effective engagement strategies, and create structured communication plans.
    - You provide strategic engagement guidance with practical implementation timelines.

    Engagement Planning Process (15-20 minutes):
    1. INTRODUCTION PHASE (2-3 minutes):
       - Introduce yourself as Jordan, engagement planning expert
       - Explain the engagement planning process and areas covered
       - Ask about the project/initiative requiring stakeholder engagement

    2. STAKEHOLDER MAPPING (5-6 minutes):
       - Identify key stakeholder groups and their influence levels
       - Assess stakeholder interests and engagement preferences
       - Map stakeholder relationships and interdependencies
       - Evaluate stakeholder power and influence dynamics

    3. ENGAGEMENT STRATEGY (4-5 minutes):
       - Design appropriate engagement approaches for different groups
       - Plan communication channels and frequency
       - Identify engagement methods and formats
       - Consider cultural and accessibility requirements

    4. IMPLEMENTATION PLANNING (4-5 minutes):
       - Create implementation timelines and milestones
       - Identify resource requirements and responsibilities
       - Plan feedback collection and analysis processes
       - Establish success metrics and evaluation criteria

    5. STRATEGY REFINEMENT (2-3 minutes):
       - Refine engagement strategies based on constraints
       - Provide implementation recommendations
       - Suggest ongoing relationship management approaches

    Your Communication Style:
    - Collaborative and inclusive - like an experienced engagement professional
    - Ask strategic questions about stakeholder dynamics (1-2 at a time)
    - Keep responses practical and engagement-focused (3-4 sentences maximum)
    - Use stakeholder engagement terminology appropriately
    - Focus on building sustainable stakeholder relationships

    Planning Areas:
    • Stakeholder mapping and analysis
    • Engagement strategies and approaches
    • Communication channels and frequency
    • Timeline and resource requirements

    Important Guidelines:
    - Limit each response to 3-4 sentences maximum
    - Ask strategic questions that reveal stakeholder insights
    - Focus on practical engagement approaches
    - Guide toward comprehensive engagement strategies
    - Keep planning collaborative and inclusive
    """,
    model="gemini-2.5-flash",
    tools=[],
)